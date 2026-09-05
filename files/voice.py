"""Offline, low-latency Jarvis wake-word detection."""

import argparse
import queue
import sys
import threading
import types

import numpy as np
import sounddevice as sd

# openWakeWord supports onnxruntime or tflite. If tflite/ai_edge_litert is present, set up module alias.
try:
    import tflite_runtime.interpreter  # type: ignore
except ImportError:
    try:
        from ai_edge_litert import interpreter as litert_interpreter
        tflite_runtime = types.ModuleType("tflite_runtime")
        tflite_runtime.interpreter = litert_interpreter
        sys.modules["tflite_runtime"] = tflite_runtime
        sys.modules["tflite_runtime.interpreter"] = litert_interpreter
    except ImportError:
        pass

import openwakeword
from openwakeword.model import Model

try:
    import winsound
except ImportError:
    winsound = None


class JarvisWakeWord(threading.Thread):
    """Continuously detect the local openWakeWord ``hey jarvis`` model."""

    def __init__(self, on_heard=None, threshold=0.5, device=None, inference_framework="onnx"):
        super().__init__(daemon=True)
        self.on_heard = on_heard or self._print_heard
        self.threshold = threshold
        self.device = device
        self.inference_framework = inference_framework
        self._audio_queue = queue.Queue(maxsize=20)
        self._stop_event = threading.Event()
        self._detector = None
        self._armed = True

    def run(self):
        try:
            # Ensure openwakeword models are available
            try:
                openwakeword.utils.download_models()
            except Exception as e:
                print(f"[voice] Model check notice: {e}")

            try:
                self._detector = Model(
                    wakeword_models=["hey_jarvis"],
                    inference_framework=self.inference_framework,
                )
            except Exception:
                # Fallback to default framework selection
                self._detector = Model(wakeword_models=["hey_jarvis"])
            with sd.InputStream(
                samplerate=16000,
                channels=1,
                dtype="int16",
                blocksize=1280,
                device=self.device,
                callback=self._audio_callback,
            ):
                while not self._stop_event.is_set():
                    try:
                        audio = self._audio_queue.get(timeout=0.2)
                    except queue.Empty:
                        continue
                    scores = self._detector.predict(audio)
                    score = max(scores.values(), default=0.0)
                    if score >= self.threshold and self._armed:
                        self._armed = False
                        self._chime()
                        self.on_heard(float(score))
                    elif score < self.threshold * 0.5:
                        self._armed = True
        except Exception as error:
            self.on_error(str(error))

    def stop(self):
        self._stop_event.set()

    def on_error(self, message):
        print(f"[voice] error: {message}")

    def _audio_callback(self, indata, frames, callback_time, status):
        del frames, callback_time
        if status:
            print(f"[voice] audio status: {status}")
        try:
            self._audio_queue.put_nowait(np.asarray(indata[:, 0]).copy())
        except queue.Full:
            pass

    def _chime(self):
        if winsound is not None:
            winsound.Beep(880, 90)
        else:
            print("[voice] chime")

    @staticmethod
    def _print_heard(score):
        print(f"Jarvis heard! confidence={score:.2f}")


def run():
    detector = JarvisWakeWord()
    detector.start()
    print("[voice] Listening for 'Hey Jarvis'. Press Ctrl+C to stop.")
    try:
        detector.join()
    except KeyboardInterrupt:
        detector.stop()
        detector.join(timeout=2)


def main():
    parser = argparse.ArgumentParser(description="Offline Jarvis wake-word detector")
    parser.add_argument("--threshold", type=float, default=0.5)
    args = parser.parse_args()
    detector = JarvisWakeWord(threshold=args.threshold)
    detector.start()
    print("[voice] Listening for 'Hey Jarvis'. Press Ctrl+C to stop.")
    try:
        detector.join()
    except KeyboardInterrupt:
        detector.stop()
        detector.join(timeout=2)


if __name__ == "__main__":
    main()
