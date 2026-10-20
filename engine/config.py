from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
import json
import os
import tempfile

@dataclass
class ServerConfig:
    host: str = "127.0.0.1"
    port: int = 8765

@dataclass
class AudioConfig:
    capture_mode: str = "master_loopback"
    target_process_name: str = "Zoom.exe"
    device_index: Optional[int] = None
    sample_rate: int = 16000
    channels: int = 1
    silence_threshold_ms: int = 3500
    auto_failover: bool = True

@dataclass
class ASRConfig:
    active_language: str = "en"
    pacing_mode: str = "paced_chunk"
    model_path_en: str = "models/sherpa-onnx-streaming-zipformer-en-20M-2023-02-17"
    num_threads: int = 2
    hotwords_file: str = "config/hotwords.txt"
    hotwords_score: float = 2.5
    decoding_method: str = "modified_beam_search"
    max_active_paths: int = 4
    smart_repair_enabled: bool = True

@dataclass
class OverlayStyleConfig:
    font_family: str = "Plus Jakarta Sans, Inter, sans-serif"
    font_size_px: int = 42
    font_color: str = "#FFFDF0"
    stroke_color: str = "#034694"
    stroke_width_px: float = 2.5
    background_color: str = "#1B1238"
    background_opacity: float = 0.75
    max_lines: int = 2
    position: str = "bottom"
    offset_x: int = 0
    offset_y: int = 72
    border_radius_px: int = 32
    animation_fade_ms: int = 300
    speaker_name: str = ""
    speaker_title: str = ""
    speaker_badge_enabled: bool = False
    bilingual_mode: bool = False
    karaoke_glow: bool = True
    translation_enabled: bool = False
    translation_position: str = "bottom-right"
    translation_offset_x: int = 48
    translation_offset_y: int = 48
    translation_font_size_px: int = 24

@dataclass
class ShortcutsConfig:
    panic_clear_key: str = "Escape"
    freeze_toggle_key: str = "Space"

def get_default_presets() -> Dict[str, Dict[str, Any]]:
    return {
        "academic_formal": {
            "name": "Academic Formal (UT)",
            "font_family": "Plus Jakarta Sans, Inter, sans-serif",
            "font_size_px": 42,
            "font_color": "#FFFDF0",
            "stroke_color": "#034694",
            "stroke_width_px": 2.5,
            "background_color": "#1B1238",
            "background_opacity": 0.75,
            "max_lines": 2,
            "position": "bottom",
            "border_radius_px": 32,
            "animation_fade_ms": 300
        },
        "slide_friendly": {
            "name": "Slide-Friendly Slim",
            "font_family": "Inter, sans-serif",
            "font_size_px": 30,
            "font_color": "#FFFDF0",
            "stroke_color": "#0E21A0",
            "stroke_width_px": 2.0,
            "background_color": "#0E21A0",
            "background_opacity": 0.85,
            "max_lines": 1,
            "position": "bottom",
            "border_radius_px": 24,
            "animation_fade_ms": 250
        },
        "minimalist_glass": {
            "name": "Minimalist Transparent",
            "font_family": "Inter, sans-serif",
            "font_size_px": 38,
            "font_color": "#FFFDF0",
            "stroke_color": "#000000",
            "stroke_width_px": 2.0,
            "background_color": "transparent",
            "background_opacity": 0.0,
            "max_lines": 2,
            "position": "bottom",
            "border_radius_px": 0,
            "animation_fade_ms": 300
        },
        "talkshow_honey": {
            "name": "Talkshow Honey Accent",
            "font_family": "Plus Jakarta Sans, sans-serif",
            "font_size_px": 44,
            "font_color": "#FFDE00",
            "stroke_color": "#1B1238",
            "stroke_width_px": 3.0,
            "background_color": "#1B1238",
            "background_opacity": 0.65,
            "max_lines": 2,
            "position": "bottom",
            "border_radius_px": 28,
            "animation_fade_ms": 300
        },
        "glow_neon_candy": {
            "name": "Glow Neon Candy",
            "font_family": "Plus Jakarta Sans, sans-serif",
            "font_size_px": 42,
            "font_color": "#FFFDF0",
            "stroke_color": "#4D2FB2",
            "stroke_width_px": 2.5,
            "background_color": "#1B1238",
            "background_opacity": 0.85,
            "max_lines": 2,
            "position": "bottom",
            "border_radius_px": 32,
            "animation_fade_ms": 300
        },
        "news_ticker_ribbon": {
            "name": "News Ticker Ribbon",
            "font_family": "Inter, sans-serif",
            "font_size_px": 36,
            "font_color": "#FFFDF0",
            "stroke_color": "#034694",
            "stroke_width_px": 2.0,
            "background_color": "#034694",
            "background_opacity": 0.90,
            "max_lines": 1,
            "position": "bottom",
            "border_radius_px": 0,
            "animation_fade_ms": 250
        },
        "speech_bubble_playful": {
            "name": "Speech Bubble Playful",
            "font_family": "Outfit, sans-serif",
            "font_size_px": 40,
            "font_color": "#FFFDF0",
            "stroke_color": "#0E21A0",
            "stroke_width_px": 2.0,
            "background_color": "#4D2FB2",
            "background_opacity": 0.82,
            "max_lines": 2,
            "position": "bottom",
            "border_radius_px": 36,
            "animation_fade_ms": 280
        },
        "top_banner_clean": {
            "name": "Top-Banner Clean",
            "font_family": "Plus Jakarta Sans, sans-serif",
            "font_size_px": 34,
            "font_color": "#FFFDF0",
            "stroke_color": "#034694",
            "stroke_width_px": 2.0,
            "background_color": "#1B1238",
            "background_opacity": 0.80,
            "max_lines": 1,
            "position": "top",
            "border_radius_px": 20,
            "animation_fade_ms": 250
        }
    }

@dataclass
class AppConfig:
    server: ServerConfig = field(default_factory=ServerConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    asr: ASRConfig = field(default_factory=ASRConfig)
    overlay_style: OverlayStyleConfig = field(default_factory=OverlayStyleConfig)
    shortcuts: ShortcutsConfig = field(default_factory=ShortcutsConfig)
    active_preset: str = "academic_formal"
    presets: Dict[str, Dict[str, Any]] = field(default_factory=get_default_presets)

def load_config(config_path: str = "config.json") -> AppConfig:
    if not os.path.exists(config_path):
        default_config = AppConfig()
        save_config(default_config, config_path)
        return default_config
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged_presets = get_default_presets()
        merged_presets.update(data.get("presets", {}))
        return AppConfig(
            server=ServerConfig(**data.get("server", {})),
            audio=AudioConfig(**data.get("audio", {})),
            asr=ASRConfig(**data.get("asr", {})),
            overlay_style=OverlayStyleConfig(**data.get("overlay_style", {})),
            shortcuts=ShortcutsConfig(**data.get("shortcuts", {})),
            active_preset=data.get("active_preset", "academic_formal"),
            presets=merged_presets
        )
    except Exception:
        default_config = AppConfig()
        save_config(default_config, config_path)
        return default_config

def save_config(config: AppConfig, config_path: str = "config.json") -> None:
    data = asdict(config)
    dir_name = os.path.dirname(os.path.abspath(config_path))
    os.makedirs(dir_name, exist_ok=True)
    fd, temp_file_path = tempfile.mkstemp(dir=dir_name, text=True)
    with open(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(temp_file_path, config_path)
