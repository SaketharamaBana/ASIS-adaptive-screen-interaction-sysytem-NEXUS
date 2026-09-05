"""
ActionDispatcher: single shared entry point for every action (click,
right-click, scroll, drag, zoom). Gestures call into this, and later a
voice/plugin layer could call the same functions without duplicating logic.
"""

import threading
import queue
import time
import pyautogui

pyautogui.FAILSAFE = False


class CursorController(threading.Thread):
    """Moves the OS cursor on its own thread so a slow OS call never
    stalls the tracking/render loop."""

    def __init__(self):
        super().__init__(daemon=True)
        self.target_queue: "queue.Queue[tuple[float, float]]" = queue.Queue(maxsize=1)
        self.running = True

    def run(self):
        while self.running:
            try:
                x, y = self.target_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            try:
                pyautogui.moveTo(x, y, duration=0)
            except Exception as e:
                print(f"[cursor] move failed: {e}")

    def move_to(self, x: float, y: float):
        try:
            self.target_queue.get_nowait()
        except queue.Empty:
            pass
        try:
            self.target_queue.put_nowait((x, y))
        except queue.Full:
            pass

    def stop(self):
        self.running = False


class ActionDispatcher:
    """Central place every gesture (and later, voice/plugins) routes
    through. Keeping this separate from recognition code is what makes
    the system extensible instead of hardcoded."""

    def __init__(self):
        self.cursor = CursorController()
        self.cursor.start()
        self._dragging = False

    # -- cursor movement --
    def move_cursor(self, x: float, y: float):
        self.cursor.move_to(x, y)

    # -- discrete actions --
    def left_click(self):
        pyautogui.click()

    def right_click(self):
        pyautogui.click(button="right")

    def scroll(self, amount: int):
        pyautogui.scroll(amount)

    def start_drag(self):
        if not self._dragging:
            pyautogui.mouseDown()
            self._dragging = True

    def end_drag(self):
        if self._dragging:
            pyautogui.mouseUp()
            self._dragging = False

    def zoom(self, direction: str):
        # Ctrl + scroll is the OS-standard zoom gesture in most apps/browsers.
        if direction == "in":
            pyautogui.hotkey("ctrl", "+")
        else:
            pyautogui.hotkey("ctrl", "-")

    def press_hotkey(self, *keys):
        try:
            pyautogui.hotkey(*keys)
        except Exception as e:
            print(f"[action] hotkey failed: {e}")

    def media_play_pause(self):
        try:
            pyautogui.press("playpause")
        except Exception as e:
            print(f"[action] playpause failed: {e}")

    def volume_mute(self):
        try:
            pyautogui.press("volumemute")
        except Exception as e:
            print(f"[action] volumemute failed: {e}")

    def take_screenshot(self):
        try:
            pyautogui.hotkey("win", "printscreen")
        except Exception as e:
            print(f"[action] screenshot failed: {e}")

    def execute_custom_action(self, action_str: str):
        if not action_str or action_str == "none":
            return
        act = action_str.lower().strip()
        if act == "media_play_pause":
            self.media_play_pause()
        elif act == "volume_mute":
            self.volume_mute()
        elif act == "screenshot":
            self.take_screenshot()
        elif act.startswith("hotkey:"):
            keys = [k.strip() for k in act[7:].split(",")]
            self.press_hotkey(*keys)
        elif act == "left_click":
            self.left_click()
        elif act == "right_click":
            self.right_click()
        else:
            print(f"[action] Unknown custom action string: {action_str}")

    def shutdown(self):
        self.end_drag()
        self.cursor.stop()
