import asyncio
import math
import os
import queue
import time
from dataclasses import asdict
from typing import Set, Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from engine.config import load_config, save_config, AppConfig
from engine.db import DatabaseManager
from engine.seed_data import seed_database
from engine.audio_capture import AudioCaptureManager
from engine.asr_worker import ASRWorker
from engine.text_processor import TextProcessor
from engine.file_writer import AtomicFileWriter
from engine.session_logger import SessionLogger
from engine.translator import OfflineSentenceTranslator

app = FastAPI(title="PUSTASUB Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = load_config()
db_manager = DatabaseManager()
seed_database(db_manager)

audio_queue = queue.Queue(maxsize=200)
text_processor = TextProcessor(hotwords_file=config.asr.hotwords_file)
for v in db_manager.get_all_vocabulary():
    text_processor.add_hotword(v["term"])

file_writer = AtomicFileWriter()
session_logger = SessionLogger()

active_websockets: Set[WebSocket] = set()
server_loop: Optional[asyncio.AbstractEventLoop] = None
is_engine_running = False
is_frozen = False
session_start_timestamp = 0.0

audio_manager: Optional[AudioCaptureManager] = None
asr_worker: Optional[ASRWorker] = None

class ControlCommand(BaseModel):
    action: Optional[str] = None
    running: Optional[bool] = None
    preset_id: Optional[str] = None
    preset: Optional[str] = None
    pacing_mode: Optional[str] = None
    hotword: Optional[str] = None
    term: Optional[str] = None
    category: Optional[str] = "academic"
    phonetic_hint: Optional[str] = ""
    boost_score: Optional[float] = 2.5
    weight: Optional[float] = None
    enabled: Optional[bool] = None
    frozen: Optional[bool] = None
    device_index: Optional[int] = None
    position: Optional[str] = None
    offset_x: Optional[int] = None
    offset_y: Optional[int] = None
    speaker_name: Optional[str] = None
    speaker_title: Optional[str] = None
    speaker_badge_enabled: Optional[bool] = None
    bilingual_mode: Optional[bool] = None
    karaoke_glow: Optional[bool] = None
    font_family: Optional[str] = None
    font_size_px: Optional[int] = None
    font_size: Optional[int] = None
    font_color: Optional[str] = None
    stroke_color: Optional[str] = None
    stroke_width_px: Optional[float] = None
    stroke_width: Optional[float] = None
    background_color: Optional[str] = None
    background_opacity: Optional[float] = None
    bg_opacity: Optional[float] = None
    border_radius_px: Optional[int] = None
    border_radius: Optional[int] = None
    translation_enabled: Optional[bool] = None
    translation_position: Optional[str] = None
    translation_offset_x: Optional[int] = None
    translation_offset_y: Optional[int] = None
    translation_font_size_px: Optional[int] = None

def broadcast_sync(payload: dict) -> None:
    global server_loop, active_websockets
    if not active_websockets:
        return
    for ws in list(active_websockets):
        try:
            if server_loop and server_loop.is_running():
                asyncio.run_coroutine_threadsafe(ws.send_json(payload), server_loop)
            else:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(ws.send_json(payload))
                else:
                    loop.run_until_complete(ws.send_json(payload))
        except Exception:
            pass

def on_sentence_translated(en_text: str, id_text: str) -> None:
    broadcast_sync({
        "event": "translation_sentence",
        "type": "translation",
        "english": en_text,
        "indonesian": id_text,
        "text": id_text,
        "enabled": config.overlay_style.translation_enabled,
        "position": config.overlay_style.translation_position,
        "timestamp": time.time()
    })
    if config.overlay_style.bilingual_mode:
        file_writer.write_subtitle(f"{en_text}\n{id_text}")

translator = OfflineSentenceTranslator(db_manager=db_manager, on_translation=on_sentence_translated)

def on_partial_transcript(raw_text: str) -> None:
    global is_frozen
    if is_frozen or not raw_text.strip():
        return
    formatted = text_processor.apply_pacing(raw_text, mode=config.asr.pacing_mode, is_final=False)
    file_writer.write_subtitle(formatted)
    glossary_tag = ""
    if config.overlay_style.bilingual_mode:
        glossary_tag = text_processor.get_glossary_tag(raw_text)
    broadcast_sync({
        "event": "partial_subtitle",
        "text": formatted,
        "raw": raw_text,
        "pacing_mode": config.asr.pacing_mode,
        "glossary_tag": glossary_tag,
        "speaker_badge": {
            "name": config.overlay_style.speaker_name,
            "title": config.overlay_style.speaker_title,
            "enabled": config.overlay_style.speaker_badge_enabled
        },
        "timestamp": time.time()
    })

def on_final_transcript(raw_text: str) -> None:
    global is_frozen, session_start_timestamp
    if not raw_text.strip():
        return
    formatted = text_processor.apply_pacing(raw_text, mode=config.asr.pacing_mode, is_final=True)
    if not is_frozen:
        file_writer.write_subtitle(formatted)
    now = time.time()
    rel_end = now - session_start_timestamp
    rel_start = max(0.0, rel_end - 2.5)
    session_logger.log_phrase(formatted, rel_start, rel_end)
    glossary_tag = ""
    if config.overlay_style.bilingual_mode:
        glossary_tag = text_processor.get_glossary_tag(raw_text)
    db_manager.log_subtitle(
        session_id=str(int(session_start_timestamp)),
        start_time=rel_start,
        end_time=rel_end,
        raw_text=raw_text,
        formatted_text=formatted,
        glossary_tag=glossary_tag,
        speaker_name=config.overlay_style.speaker_name if config.overlay_style.speaker_badge_enabled else ""
    )
    broadcast_sync({
        "event": "final_subtitle",
        "text": formatted,
        "raw": raw_text,
        "pacing_mode": config.asr.pacing_mode,
        "glossary_tag": glossary_tag,
        "speaker_badge": {
            "name": config.overlay_style.speaker_name,
            "title": config.overlay_style.speaker_title,
            "enabled": config.overlay_style.speaker_badge_enabled
        },
        "timestamp": now
    })
    translator.process_final_transcript(formatted or raw_text)

def on_vu_meter(peak: float, rms: float) -> None:
    peak_db = 20.0 * math.log10(max(peak, 1e-5)) if peak > 0 else -60.0
    rms_db = 20.0 * math.log10(max(rms, 1e-5)) if rms > 0 else -60.0
    broadcast_sync({
        "event": "vu_meter",
        "type": "audio_level",
        "peak": round(peak, 3),
        "rms": round(rms, 3),
        "peak_db": round(max(-60.0, min(0.0, peak_db)), 1),
        "rms_db": round(max(-60.0, min(0.0, rms_db)), 1)
    })

def on_audio_failover(new_device_name: str, new_device_index: int) -> None:
    broadcast_sync({
        "event": "audio_failover",
        "status": "reconnected",
        "device_name": new_device_name,
        "device_index": new_device_index,
        "timestamp": time.time()
    })

def ensure_subsystems_initialized() -> None:
    global server_loop, audio_manager, asr_worker
    if server_loop is None:
        try:
            server_loop = asyncio.get_running_loop()
        except RuntimeError:
            pass
    if audio_manager is None:
        audio_manager = AudioCaptureManager(
            audio_queue=audio_queue,
            config=config.audio,
            vu_callback=on_vu_meter,
            failover_callback=on_audio_failover
        )
    if asr_worker is None:
        asr_worker = ASRWorker(
            audio_queue=audio_queue,
            config=config.asr,
            on_partial=on_partial_transcript,
            on_final=on_final_transcript
        )

@app.on_event("startup")
async def startup_event():
    global server_loop
    server_loop = asyncio.get_running_loop()
    ensure_subsystems_initialized()

@app.on_event("shutdown")
async def shutdown_event():
    stop_engine_internal()

def start_engine_internal() -> bool:
    global is_engine_running, session_start_timestamp, audio_manager, asr_worker
    if is_engine_running:
        return True
    ensure_subsystems_initialized()
    if asr_worker is None or audio_manager is None:
        return False
    session_start_timestamp = time.time()
    session_logger.start_session()
    asr_started = asr_worker.start()
    if not asr_started:
        return False
    audio_started = audio_manager.start_capture(device_index=config.audio.device_index)
    if not audio_started:
        asr_worker.stop()
        return False
    is_engine_running = True
    broadcast_sync({
        "event": "engine_status",
        "status": "LIVE",
        "timestamp": time.time()
    })
    return True

def stop_engine_internal() -> None:
    global is_engine_running, audio_manager, asr_worker
    is_engine_running = False
    if audio_manager is not None:
        audio_manager.stop_capture()
    if asr_worker is not None:
        asr_worker.stop()
    file_writer.clear_subtitle()
    broadcast_sync({
        "event": "engine_status",
        "status": "STANDBY",
        "timestamp": time.time()
    })

@app.get("/api/status")
async def get_status():
    ensure_subsystems_initialized()
    devices = audio_manager.get_audio_devices() if audio_manager else {"loopback": [], "physical_input": []}
    return {
        "status": "LIVE" if is_engine_running else "STANDBY",
        "is_frozen": is_frozen,
        "active_preset": config.active_preset,
        "active_language": "en",
        "pacing_mode": config.asr.pacing_mode,
        "active_device_name": audio_manager.active_device_name if audio_manager else "",
        "active_device_index": audio_manager.active_device_index if audio_manager else None,
        "devices": devices,
        "presets": config.presets,
        "overlay_style": asdict(config.overlay_style),
        "database": "sqlite_wal",
        "vocabulary_count": len(db_manager.get_all_vocabulary())
    }

@app.post("/api/control/engine")
async def api_engine_control(cmd: ControlCommand):
    target_running = cmd.running
    if target_running is None:
        target_running = not is_engine_running
    if target_running:
        success = start_engine_internal()
    else:
        stop_engine_internal()
        success = True
    return {
        "success": success,
        "is_running": is_engine_running,
        "status": "LIVE" if is_engine_running else "STANDBY"
    }

@app.post("/api/control/start")
async def api_start():
    success = start_engine_internal()
    return {"success": success, "status": "LIVE" if is_engine_running else "STANDBY"}

@app.post("/api/control/stop")
async def api_stop():
    stop_engine_internal()
    return {"success": True, "status": "STANDBY"}

@app.get("/api/devices")
async def api_devices():
    ensure_subsystems_initialized()
    dev_dict = audio_manager.get_audio_devices() if audio_manager else {"loopback": [], "physical_input": []}
    flat_devices = []
    if isinstance(dev_dict, dict):
        for d in dev_dict.get("loopback", []):
            flat_devices.append({"index": d.get("index"), "name": d.get("name", "Audio Device")})
        for d in dev_dict.get("physical_input", []):
            flat_devices.append({"index": d.get("index"), "name": d.get("name", "Microphone")})
    elif isinstance(dev_dict, list):
        flat_devices = dev_dict
    active_name = audio_manager.active_device_name if audio_manager else "Suara Komputer (Loopback Default)"
    return {
        "success": True,
        "devices": flat_devices,
        "device_groups": dev_dict,
        "active_device_name": active_name,
        "active_device_index": config.audio.device_index
    }

@app.post("/api/control/panic")
async def api_panic():
    file_writer.clear_subtitle()
    translator.clear_translation()
    broadcast_sync({
        "event": "panic_clear",
        "action": "instant_wipe",
        "timestamp": time.time()
    })
    return {"success": True, "action": "panic_cleared"}

@app.post("/api/control/freeze")
async def api_freeze(cmd: Optional[ControlCommand] = None):
    global is_frozen
    if cmd and cmd.frozen is not None:
        is_frozen = cmd.frozen
    else:
        is_frozen = not is_frozen
    broadcast_sync({
        "event": "freeze_subtitle",
        "is_frozen": is_frozen,
        "frozen": is_frozen,
        "timestamp": time.time()
    })
    return {"success": True, "is_frozen": is_frozen, "frozen": is_frozen}

@app.post("/api/control/translation")
async def api_translation(cmd: ControlCommand):
    if cmd.enabled is not None:
        config.overlay_style.translation_enabled = cmd.enabled
    elif cmd.translation_enabled is not None:
        config.overlay_style.translation_enabled = cmd.translation_enabled
    if cmd.position is not None:
        config.overlay_style.translation_position = cmd.position
    elif cmd.translation_position is not None:
        config.overlay_style.translation_position = cmd.translation_position
    if cmd.offset_x is not None:
        config.overlay_style.translation_offset_x = cmd.offset_x
    if cmd.offset_y is not None:
        config.overlay_style.translation_offset_y = cmd.offset_y
    save_config(config)
    broadcast_sync({
        "event": "switch_translation",
        "type": "translation",
        "enabled": config.overlay_style.translation_enabled,
        "position": config.overlay_style.translation_position,
        "offset_x": config.overlay_style.translation_offset_x,
        "offset_y": config.overlay_style.translation_offset_y,
        "timestamp": time.time()
    })
    return {
        "success": True,
        "translation_enabled": config.overlay_style.translation_enabled,
        "translation_position": config.overlay_style.translation_position
    }

@app.post("/api/control/device")
async def api_device(cmd: ControlCommand):
    ensure_subsystems_initialized()
    dev_idx = cmd.device_index
    if dev_idx == -1:
        dev_idx = None
    config.audio.device_index = dev_idx
    save_config(config)
    success = True
    if audio_manager:
        success = audio_manager.switch_device(dev_idx)
    active_name = audio_manager.active_device_name if audio_manager else "Default"
    active_idx = audio_manager.active_device_index if audio_manager else dev_idx
    broadcast_sync({
        "event": "update_device",
        "device_index": active_idx,
        "device_name": active_name,
        "timestamp": time.time()
    })
    return {"success": success, "device_index": active_idx, "device_name": active_name}

@app.post("/api/control/preset")
async def api_preset(cmd: ControlCommand):
    target_preset = cmd.preset_id or cmd.preset
    if not target_preset or target_preset not in config.presets:
        return JSONResponse(status_code=400, content={"error": "Invalid preset_id"})
    config.active_preset = target_preset
    db_manager.set_active_preset(target_preset)
    save_config(config)
    selected_style = config.presets[target_preset]
    broadcast_sync({
        "event": "apply_preset",
        "preset_id": target_preset,
        "style": selected_style,
        "timestamp": time.time()
    })
    return {"success": True, "active_preset": target_preset, "style": selected_style}

@app.get("/api/vocabulary")
async def api_get_vocabulary():
    items = db_manager.get_all_vocabulary()
    return {
        "success": True,
        "count": len(items),
        "items": items,
        "vocabulary": items
    }

@app.post("/api/vocabulary")
async def api_add_vocabulary(cmd: ControlCommand):
    term = (cmd.term or cmd.hotword or "").strip()
    if not term:
        return JSONResponse(status_code=400, content={"error": "Term cannot be empty"})
    category = cmd.category or "academic"
    hint = cmd.phonetic_hint or ""
    score = cmd.boost_score if cmd.boost_score is not None else (cmd.weight or 2.5)
    db_manager.add_vocabulary(term, category=category, phonetic_hint=hint, boost_score=score)
    text_processor.add_hotword(term)
    if translator:
        translator.add_vocabulary_term(term, category)
    items = db_manager.get_all_vocabulary()
    return {"success": True, "term": term, "category": category, "boost_score": score, "items": items, "vocabulary": items}

@app.delete("/api/vocabulary/{identifier}")
async def api_delete_vocabulary(identifier: str):
    clean_id = identifier.strip()
    actual_term = db_manager.get_term_by_id_or_term(clean_id) or clean_id
    removed = db_manager.remove_vocabulary(clean_id)
    if actual_term:
        text_processor.remove_hotword(actual_term)
        if translator:
            translator.remove_vocabulary_term(actual_term)
    items = db_manager.get_all_vocabulary()
    return {"success": True, "removed": removed, "term": actual_term, "items": items, "vocabulary": items}

@app.post("/api/control/pacing")
async def api_pacing(cmd: ControlCommand):
    if not cmd.pacing_mode or cmd.pacing_mode not in ("word_flow", "paced_chunk"):
        return JSONResponse(status_code=400, content={"error": "Pacing must be 'word_flow' or 'paced_chunk'"})
    config.asr.pacing_mode = cmd.pacing_mode
    save_config(config)
    broadcast_sync({
        "event": "switch_pacing",
        "pacing_mode": cmd.pacing_mode,
        "timestamp": time.time()
    })
    return {"success": True, "pacing_mode": cmd.pacing_mode}

@app.post("/api/control/position")
async def api_position(cmd: ControlCommand):
    if cmd.position:
        config.overlay_style.position = cmd.position
    if cmd.offset_x is not None:
        config.overlay_style.offset_x = cmd.offset_x
    if cmd.offset_y is not None:
        config.overlay_style.offset_y = cmd.offset_y
    save_config(config)
    broadcast_sync({
        "event": "update_position",
        "position": config.overlay_style.position,
        "offset_x": config.overlay_style.offset_x,
        "offset_y": config.overlay_style.offset_y,
        "timestamp": time.time()
    })
    return {
        "success": True,
        "position": config.overlay_style.position,
        "offset_x": config.overlay_style.offset_x,
        "offset_y": config.overlay_style.offset_y
    }

@app.post("/api/control/speaker")
async def api_speaker(cmd: ControlCommand):
    if cmd.speaker_name is not None:
        config.overlay_style.speaker_name = cmd.speaker_name
    if cmd.speaker_title is not None:
        config.overlay_style.speaker_title = cmd.speaker_title
    if cmd.speaker_badge_enabled is not None:
        config.overlay_style.speaker_badge_enabled = cmd.speaker_badge_enabled
    db_manager.set_active_speaker(
        config.overlay_style.speaker_name,
        config.overlay_style.speaker_title,
        config.overlay_style.speaker_badge_enabled
    )
    save_config(config)
    broadcast_sync({
        "event": "update_speaker",
        "speaker_name": config.overlay_style.speaker_name,
        "speaker_title": config.overlay_style.speaker_title,
        "speaker_badge_enabled": config.overlay_style.speaker_badge_enabled,
        "timestamp": time.time()
    })
    return {
        "success": True,
        "speaker_name": config.overlay_style.speaker_name,
        "speaker_title": config.overlay_style.speaker_title,
        "speaker_badge_enabled": config.overlay_style.speaker_badge_enabled
    }

@app.post("/api/control/bilingual")
async def api_bilingual(cmd: ControlCommand):
    target_mode = cmd.bilingual_mode if cmd.bilingual_mode is not None else cmd.enabled
    if target_mode is not None:
        config.overlay_style.bilingual_mode = target_mode
    save_config(config)
    broadcast_sync({
        "event": "switch_bilingual",
        "bilingual_mode": config.overlay_style.bilingual_mode,
        "timestamp": time.time()
    })
    return {"success": True, "bilingual_mode": config.overlay_style.bilingual_mode}

@app.post("/api/control/style")
async def api_style(cmd: ControlCommand):
    if cmd.font_family is not None:
        config.overlay_style.font_family = cmd.font_family
    target_font_size = cmd.font_size_px if cmd.font_size_px is not None else cmd.font_size
    if target_font_size is not None:
        config.overlay_style.font_size_px = target_font_size
    if cmd.font_color is not None:
        config.overlay_style.font_color = cmd.font_color
    if cmd.stroke_color is not None:
        config.overlay_style.stroke_color = cmd.stroke_color
    target_stroke = cmd.stroke_width_px if cmd.stroke_width_px is not None else cmd.stroke_width
    if target_stroke is not None:
        config.overlay_style.stroke_width_px = target_stroke
    if cmd.background_color is not None:
        config.overlay_style.background_color = cmd.background_color
    target_opacity = cmd.background_opacity if cmd.background_opacity is not None else cmd.bg_opacity
    if target_opacity is not None:
        config.overlay_style.background_opacity = target_opacity
    target_radius = cmd.border_radius_px if cmd.border_radius_px is not None else cmd.border_radius
    if target_radius is not None:
        config.overlay_style.border_radius_px = target_radius
    if cmd.karaoke_glow is not None:
        config.overlay_style.karaoke_glow = cmd.karaoke_glow
    if cmd.translation_enabled is not None:
        config.overlay_style.translation_enabled = cmd.translation_enabled
    elif cmd.enabled is not None:
        config.overlay_style.translation_enabled = cmd.enabled
    if cmd.translation_position is not None:
        config.overlay_style.translation_position = cmd.translation_position
    elif cmd.position is not None:
        config.overlay_style.translation_position = cmd.position
    if cmd.translation_offset_x is not None:
        config.overlay_style.translation_offset_x = cmd.translation_offset_x
    if cmd.translation_offset_y is not None:
        config.overlay_style.translation_offset_y = cmd.translation_offset_y
    if cmd.translation_font_size_px is not None:
        config.overlay_style.translation_font_size_px = cmd.translation_font_size_px
    save_config(config)
    style_dict = asdict(config.overlay_style)
    broadcast_sync({
        "event": "update_style",
        "style": style_dict,
        "timestamp": time.time()
    })
    return {"success": True, "style": style_dict}

@app.post("/api/control/preset_save")
async def api_preset_save(cmd: ControlCommand):
    if not cmd.preset_id:
        return JSONResponse(status_code=400, content={"error": "preset_id required"})
    style_dict = asdict(config.overlay_style)
    style_dict["name"] = cmd.action or cmd.preset_id
    config.presets[cmd.preset_id] = style_dict
    config.active_preset = cmd.preset_id
    save_config(config)
    broadcast_sync({
        "event": "apply_preset",
        "preset_id": cmd.preset_id,
        "style": style_dict,
        "timestamp": time.time()
    })
    return {"success": True, "preset_id": cmd.preset_id, "style": style_dict}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_websockets.add(websocket)
    try:
        await websocket.send_json({
            "event": "init_state",
            "status": "LIVE" if is_engine_running else "STANDBY",
            "is_frozen": is_frozen,
            "active_preset": config.active_preset,
            "style": config.presets.get(config.active_preset, {}),
            "overlay_style": asdict(config.overlay_style),
            "timestamp": time.time()
        })
        while True:
            data = await websocket.receive_json()
            event_type = data.get("event")
            if event_type == "panic_clear":
                await api_panic()
            elif event_type == "freeze_toggle":
                await api_freeze()
            elif event_type == "apply_preset":
                preset_id = data.get("preset_id")
                if preset_id:
                    await api_preset(ControlCommand(preset_id=preset_id))
    except WebSocketDisconnect:
        active_websockets.discard(websocket)
    except Exception:
        active_websockets.discard(websocket)

admin_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web", "admin"))
overlay_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web", "overlay"))
os.makedirs(admin_dir, exist_ok=True)
os.makedirs(overlay_dir, exist_ok=True)

@app.get("/")
async def get_admin_root():
    admin_html = os.path.join(admin_dir, "index.html")
    if os.path.exists(admin_html):
        return FileResponse(admin_html)
    return JSONResponse(content={"app": "PUSTASUB", "status": "Admin UI pending Milestone 4"})

app.mount("/overlay", StaticFiles(directory=overlay_dir, html=True), name="overlay")
app.mount("/admin", StaticFiles(directory=admin_dir, html=True), name="admin")
