import queue
import threading
import time
from typing import Dict, List, Optional, Any, Callable
import numpy as np
import pyaudiowpatch as pyaudio
from engine.config import AudioConfig

class AudioCaptureManager:
    def __init__(
        self,
        audio_queue: queue.Queue,
        config: Optional[AudioConfig] = None,
        vu_callback: Optional[Callable[[float, float], None]] = None,
        failover_callback: Optional[Callable[[str, int], None]] = None
    ):
        self.audio_queue = audio_queue
        self.config = config or AudioConfig()
        self.vu_callback = vu_callback
        self.failover_callback = failover_callback
        self.pa: Optional[pyaudio.PyAudio] = None
        self.stream: Optional[pyaudio.Stream] = None
        self.is_running = False
        self.active_device_index: Optional[int] = None
        self.active_device_name: str = ""
        self.src_sample_rate = 48000
        self.src_channels = 2
        self.last_audio_timestamp = 0.0
        self.feeder_thread: Optional[threading.Thread] = None
        self.failover_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()

    def get_audio_devices(self) -> Dict[str, List[Dict[str, Any]]]:
        temp_pa = pyaudio.PyAudio()
        loopback_devices = []
        input_devices = []
        try:
            device_count = temp_pa.get_device_count()
            for i in range(device_count):
                try:
                    info = temp_pa.get_device_info_by_index(i)
                    if info.get("isLoopbackDevice", False):
                        loopback_devices.append({
                            "index": i,
                            "name": info.get("name", ""),
                            "default_sample_rate": int(info.get("defaultSampleRate", 48000)),
                            "channels": int(info.get("maxInputChannels", 2)),
                            "type": "loopback"
                        })
                    elif info.get("maxInputChannels", 0) > 0:
                        loopback_devices.append({
                            "index": i,
                            "name": info.get("name", ""),
                            "default_sample_rate": int(info.get("defaultSampleRate", 48000)),
                            "channels": int(info.get("maxInputChannels", 1)),
                            "type": "physical_input"
                        })
                except Exception:
                    continue
        finally:
            temp_pa.terminate()
        return {
            "loopback": [d for d in loopback_devices if d["type"] == "loopback"],
            "physical_input": [d for d in loopback_devices if d["type"] == "physical_input"]
        }

    def get_default_loopback_device(self) -> Optional[Dict[str, Any]]:
        temp_pa = pyaudio.PyAudio()
        try:
            info = temp_pa.get_default_wasapi_loopback()
            if info:
                return {
                    "index": info.get("index"),
                    "name": info.get("name"),
                    "default_sample_rate": int(info.get("defaultSampleRate", 48000)),
                    "channels": int(info.get("maxInputChannels", 2))
                }
        except Exception:
            return None
        finally:
            temp_pa.terminate()
        return None

    def start_capture(self, device_index: Optional[int] = None) -> bool:
        with self.lock:
            if self.is_running:
                return True
            self.pa = pyaudio.PyAudio()
            target_device = None
            if device_index is not None:
                try:
                    info = self.pa.get_device_info_by_index(device_index)
                    if info:
                        target_device = info
                except Exception:
                    target_device = None
            if target_device is None:
                try:
                    target_device = self.pa.get_default_wasapi_loopback()
                except Exception:
                    target_device = None
            if target_device is None:
                self.pa.terminate()
                self.pa = None
                return False

            self.active_device_index = target_device.get("index")
            self.active_device_name = target_device.get("name", "Unknown")
            self.src_sample_rate = int(target_device.get("defaultSampleRate", 48000))
            self.src_channels = int(target_device.get("maxInputChannels", 2))

            try:
                self.stream = self.pa.open(
                    format=pyaudio.paFloat32,
                    channels=self.src_channels,
                    rate=self.src_sample_rate,
                    input=True,
                    input_device_index=self.active_device_index,
                    frames_per_buffer=1024,
                    stream_callback=self._audio_callback
                )
            except Exception:
                self.pa.terminate()
                self.pa = None
                return False

            self.is_running = True
            self.last_audio_timestamp = time.time()
            self.stream.start_stream()

            self.feeder_thread = threading.Thread(target=self._silence_feeder_worker, daemon=True)
            self.feeder_thread.start()

            if self.config.auto_failover:
                self.failover_thread = threading.Thread(target=self._failover_watcher_worker, daemon=True)
                self.failover_thread.start()

            return True

    def stop_capture(self) -> None:
        with self.lock:
            self.is_running = False
            if self.stream is not None:
                try:
                    self.stream.stop_stream()
                    self.stream.close()
                except Exception:
                    pass
                self.stream = None
            if self.pa is not None:
                try:
                    self.pa.terminate()
                except Exception:
                    pass
                self.pa = None

    def switch_device(self, device_index: Optional[int]) -> bool:
        was_running = self.is_running
        self.stop_capture()
        self.config.device_index = device_index
        if was_running:
            return self.start_capture(device_index=device_index)
        return True

    def _audio_callback(self, in_data, frame_count, time_info, status):
        if not self.is_running or not in_data:
            return (None, pyaudio.paContinue)
        self.last_audio_timestamp = time.time()
        raw_samples = np.frombuffer(in_data, dtype=np.float32)
        if len(raw_samples) == 0:
            return (None, pyaudio.paContinue)

        if self.src_channels > 1:
            try:
                reshaped = raw_samples.reshape(-1, self.src_channels)
                mono = reshaped.mean(axis=1)
            except Exception:
                mono = raw_samples
        else:
            mono = raw_samples

        if self.src_sample_rate != 16000 and len(mono) > 1:
            num_target = int(len(mono) * 16000 / self.src_sample_rate)
            if num_target > 0:
                indices = np.linspace(0, len(mono) - 1, num_target)
                resampled = np.interp(indices, np.arange(len(mono)), mono).astype(np.float32)
            else:
                resampled = mono
        else:
            resampled = mono.astype(np.float32)

        peak = float(np.max(np.abs(resampled))) if len(resampled) > 0 else 0.0
        rms = float(np.sqrt(np.mean(resampled ** 2))) if len(resampled) > 0 else 0.0

        if self.vu_callback is not None:
            try:
                self.vu_callback(peak, rms)
            except Exception:
                pass

        try:
            self.audio_queue.put_nowait(resampled)
        except queue.Full:
            pass

        return (None, pyaudio.paContinue)

    def _silence_feeder_worker(self) -> None:
        silent_chunk = np.zeros(640, dtype=np.float32)
        while self.is_running:
            time.sleep(0.04)
            if not self.is_running:
                break
            elapsed = time.time() - self.last_audio_timestamp
            if elapsed > 0.04:
                try:
                    self.audio_queue.put_nowait(silent_chunk)
                    self.last_audio_timestamp = time.time()
                except queue.Full:
                    pass

    def _failover_watcher_worker(self) -> None:
        while self.is_running:
            time.sleep(1.5)
            if not self.is_running:
                break
            if self.stream is not None and not self.stream.is_active():
                self._handle_failover()

    def _handle_failover(self) -> None:
        old_name = self.active_device_name
        self.stop_capture()
        time.sleep(1.0)
        success = self.start_capture()
        if success and self.failover_callback is not None:
            self.failover_callback(self.active_device_name, self.active_device_index or 0)
