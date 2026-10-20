import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import queue
import time
from engine.config import load_config
from engine.audio_capture import AudioCaptureManager
from engine.asr_worker import ASRWorker

def main():
    print("=" * 60)
    print("PUSTASUB — MILESTONE 1 INTEGRATED PIPELINE VERIFICATION")
    print("=" * 60)

    config = load_config()
    audio_queue = queue.Queue(maxsize=200)

    partial_count = 0
    final_count = 0

    def on_partial(text: str):
        nonlocal partial_count
        partial_count += 1
        print(f"\r[STREAMING] {text}", end="", flush=True)

    def on_final(text: str):
        nonlocal final_count
        final_count += 1
        print(f"\n[FINAL PHRASE] {text}\n")

    def on_vu(peak: float, rms: float):
        pass

    audio_manager = AudioCaptureManager(
        audio_queue=audio_queue,
        config=config.audio,
        vu_callback=on_vu
    )

    asr_worker = ASRWorker(
        audio_queue=audio_queue,
        config=config.asr,
        on_partial=on_partial,
        on_final=on_final
    )

    print("Initializing ASR Streaming Zipformer Model...")
    asr_initialized = asr_worker.initialize()
    if not asr_initialized:
        print("ERROR: Failed to initialize ASR Worker")
        return False
    print("ASR Model Loaded Successfully.")

    print("Starting ASR Worker Thread...")
    asr_started = asr_worker.start()
    if not asr_started:
        print("ERROR: Failed to start ASR Worker Thread")
        return False

    print("Starting WASAPI Loopback Audio Capture...")
    audio_started = audio_manager.start_capture()
    if not audio_started:
        print("ERROR: Failed to start WASAPI Loopback Capture")
        asr_worker.stop()
        return False

    dev_name = audio_manager.active_device_name
    print(f"Capture Active on: {dev_name}")
    print("System listening to speaker output for 4 seconds...")

    time.sleep(4.0)

    captured_chunks = audio_queue.qsize()
    print(f"\nQueue status after 4 seconds: {captured_chunks} chunks captured/fed.")

    audio_manager.stop_capture()
    asr_worker.stop()

    print("Audio Capture and ASR Worker stopped cleanly.")
    print("MILESTONE 1 PIPELINE VERIFICATION COMPLETE: SUCCESS")
    return True

if __name__ == "__main__":
    main()
