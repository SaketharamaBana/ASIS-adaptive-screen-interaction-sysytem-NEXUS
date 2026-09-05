"""Responsive PySide6 dashboard for NEXUS live control."""

import os
import sys
import time
import urllib.request
from datetime import datetime

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
import pyautogui

from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtGui import QImage, QPixmap, QFont
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

import config
from actions import ActionDispatcher
from capture import FrameGrabber
from filters import PointOneEuroFilter
from fusion import CursorHistory
from gestures import GestureState, precision_mode_active, process_landmarks, get_trainer_instance
from trainer import GestureTrainer


class RecorderWorker(QThread):
    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, gesture_name, sample_count, frame_count):
        super().__init__()
        self.gesture_name = gesture_name
        self.sample_count = sample_count
        self.frame_count = frame_count

    def run(self):
        try:
            from recorder import GestureRecorder, record_from_camera

            recorder = GestureRecorder()
            paths = record_from_camera(
                recorder,
                self.gesture_name,
                self.sample_count,
                self.frame_count,
            )
            self.completed.emit(paths)
        except Exception as error:
            self.failed.emit(str(error))


class ModelTrainerWorker(QThread):
    completed = Signal(dict)
    failed = Signal(str)

    def run(self):
        try:
            trainer = GestureTrainer()
            res = trainer.train()
            # Reload active model instance in gestures pipeline
            get_trainer_instance().load()
            self.completed.emit(res)
        except Exception as error:
            self.failed.emit(str(error))


class VoiceWorker(QThread):
    heard = Signal(float)
    failed = Signal(str)
    log_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.detector = None

    def run(self):
        try:
            from voice import JarvisWakeWord

            self.log_signal.emit("Initializing Jarvis offline wake-word detector...")
            self.detector = JarvisWakeWord(
                on_heard=self._on_heard_internal
            )
            self.detector.on_error = self.failed.emit
            self.detector.start()
            self.log_signal.emit("Jarvis engine active — listening for 'Hey Jarvis'")
            self.detector.join()
        except Exception as error:
            self.failed.emit(str(error))

    def _on_heard_internal(self, score):
        self.log_signal.emit(f"Jarvis wake word heard! Confidence: {score:.2f}")
        self.heard.emit(score)

    def stop(self):
        if self.detector is not None:
            self.detector.stop()


class InferenceWorker(QThread):
    frame_ready = Signal(QImage)
    metrics_ready = Signal(str, float, float, int, bool, bool)
    status_ready = Signal(str)
    failed = Signal(str)
    log_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self._stop_requested = False
        self._failed = False

    def stop(self):
        self._stop_requested = True

    def run(self):
        landmarker = None
        grabber = None
        dispatcher = None
        last_gesture_logged = "none"
        try:
            if not os.path.exists(config.MODEL_PATH):
                self.status_ready.emit("Downloading hand model...")
                self.log_signal.emit("Downloading MediaPipe hand landmark model...")
                urllib.request.urlretrieve(config.MODEL_URL, config.MODEL_PATH)
                self.log_signal.emit("Hand landmark model download complete.")

            base_options = mp_python.BaseOptions(model_asset_path=config.MODEL_PATH)
            options = mp_vision.HandLandmarkerOptions(
                base_options=base_options,
                num_hands=config.MAX_HANDS,
                min_hand_detection_confidence=0.6,
                min_tracking_confidence=0.6,
            )
            landmarker = mp_vision.HandLandmarker.create_from_options(options)
            grabber = FrameGrabber(
                config.CAM_INDEX, config.CAM_WIDTH, config.CAM_HEIGHT, config.MAX_HANDS
            )
            grabber.start()
            dispatcher = ActionDispatcher()
            point_filter = PointOneEuroFilter(
                min_cutoff=config.SMOOTHING_MIN_CUTOFF,
                beta=config.SMOOTHING_BETA,
            )
            gesture_states = {"left": GestureState(), "right": GestureState()}
            cursor_history = CursorHistory(config.FUSION_HISTORY_SECONDS)
            screen_w, screen_h = pyautogui.size()
            previous_time = time.time()
            fps_values = []
            self.status_ready.emit("Running")
            self.log_signal.emit("NEXUS computer vision pipeline started successfully.")

            while not self._stop_requested:
                frame = grabber.get_frame()
                if frame is None:
                    time.sleep(0.005)
                    continue

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                result = landmarker.detect(image)
                height, width = frame.shape[:2]
                info = {"gesture": "none", "confidence": 0.0}
                left_detected = False
                right_detected = False

                if result.hand_landmarks:
                    hands = []
                    for index, landmarks in enumerate(result.hand_landmarks):
                        handedness = "right"
                        if index < len(result.handedness):
                            handedness = result.handedness[index][0].category_name.lower()
                        left_detected = left_detected or handedness == "left"
                        right_detected = right_detected or handedness == "right"
                        hands.append((handedness, landmarks))
                        color = (255, 160, 0) if handedness == "left" else (0, 255, 0)
                        for point in landmarks:
                            cv2.circle(
                                frame,
                                (int(point.x * width), int(point.y * height)),
                                4,
                                color,
                                -1,
                            )

                    left_hand = next((hand for hand in hands if hand[0] == "left"), None)
                    right_hand = next((hand for hand in hands if hand[0] == "right"), None)
                    precision_active = (
                        precision_mode_active(left_hand[1])[0]
                        if left_hand is not None
                        else False
                    )

                    if right_hand is not None:
                        landmarks = right_hand[1]
                        sx, sy = point_filter.filter(landmarks[8].x, landmarks[8].y)
                        if precision_active:
                            sx = 0.5 + (sx - 0.5) * config.PRECISION_SENSITIVITY
                            sy = 0.5 + (sy - 0.5) * config.PRECISION_SENSITIVITY
                        tx, ty = self._map_to_screen(sx, sy, screen_w, screen_h)
                        cursor_history.record(tx, ty)
                        dispatcher.move_cursor(tx, ty)
                        info = process_landmarks(
                            landmarks, gesture_states["right"], dispatcher
                        )
                        if precision_active:
                            info["gesture"] = f"precision + {info['gesture']}"
                    else:
                        point_filter.reset()
                        gesture_states["right"].reset(dispatcher)

                    if left_hand is not None:
                        gesture_states["left"].reset(dispatcher)
                else:
                    point_filter.reset()
                    for state in gesture_states.values():
                        state.reset(dispatcher)

                # Log gesture transitions if changed
                current_g = info["gesture"]
                if current_g != "none" and current_g != last_gesture_logged:
                    self.log_signal.emit(f"Gesture triggered: {current_g} (conf={info['confidence']:.2f})")
                    last_gesture_logged = current_g
                elif current_g == "none":
                    last_gesture_logged = "none"

                current_time = time.time()
                fps_values.append(1.0 / max(current_time - previous_time, 1e-6))
                fps_values = fps_values[-30:]
                previous_time = current_time
                fps = sum(fps_values) / len(fps_values)
                cv2.putText(
                    frame,
                    f"FPS: {fps:.1f}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 0),
                    2,
                )

                # Ensure contiguous memory before creating QImage
                frame_contig = np.ascontiguousarray(frame)
                output = QImage(
                    frame_contig.data,
                    width,
                    height,
                    frame_contig.strides[0],
                    QImage.Format.Format_BGR888,
                ).copy()
                self.frame_ready.emit(output)
                self.metrics_ready.emit(
                    info["gesture"],
                    float(info["confidence"]),
                    float(fps),
                    len(result.hand_landmarks) if result.hand_landmarks else 0,
                    left_detected,
                    right_detected,
                )
        except Exception as error:
            self._failed = True
            self.failed.emit(str(error))
            self.log_signal.emit(f"NEXUS Error: {error}")
        finally:
            if grabber is not None:
                grabber.stop()
            if dispatcher is not None:
                dispatcher.shutdown()
            if landmarker is not None:
                landmarker.close()
            if not self._failed:
                self.status_ready.emit("Stopped")
                self.log_signal.emit("NEXUS pipeline stopped.")

    @staticmethod
    def _map_to_screen(nx, ny, screen_w, screen_h):
        margin = config.ACTIVE_ZONE_MARGIN
        nx = min(max((nx - margin) / (1 - 2 * margin), 0.0), 1.0)
        ny = min(max((ny - margin) / (1 - 2 * margin), 0.0), 1.0)
        return nx * screen_w, ny * screen_h


class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.voice_worker = None
        self.setWindowTitle("NEXUS — Adaptive Touchless Interaction Dashboard")
        self.resize(1180, 780)
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(
            "QMainWindow { background: #0f141c; color: #e1e7ec; font-family: 'Segoe UI', Arial, sans-serif; }"
            "QLabel { color: #d0d9e0; font-size: 13px; }"
            "QPushButton { padding: 9px 18px; background: #0088a9; font-weight: bold;"
            " border: 0; border-radius: 5px; color: white; min-height: 20px; }"
            "QPushButton:hover { background: #00a5cd; }"
            "QPushButton:disabled { background: #263545; color: #617485; }"
            "QTabWidget::pane { border: 1px solid #233140; background: #131b26; border-radius: 4px; }"
            "QTabBar::tab { padding: 11px 22px; background: #182330; color: #8e9dae; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; font-weight: 600; }"
            "QTabBar::tab:selected { background: #0088a9; color: white; }"
            "QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox { background: #1a2533; color: #e1e7ec; border: 1px solid #2e3e52; padding: 6px; border-radius: 4px; }"
            "QTableWidget { background: #131b26; color: #e1e7ec; gridline-color: #233140; border: none; }"
            "QHeaderView::section { background: #1a2533; color: #00a5cd; font-weight: bold; padding: 6px; border: 1px solid #233140; }"
            "QListWidget, QTextEdit { background: #0b0f16; color: #00e5ff; font-family: 'Consolas', 'Courier New', monospace; border: 1px solid #233140; border-radius: 4px; padding: 6px; }"
        )
        self.tabs = QTabWidget()
        self.tabs.addTab(self._live_tab(), "Live View")
        self.tabs.addTab(self._trainer_tab(), "Trainer")
        self.tabs.addTab(self._bindings_tab(), "Bindings")
        self.tabs.addTab(self._settings_tab(), "Settings")
        self.tabs.addTab(self._activity_log_tab(), "Activity Log")
        self.tabs.addTab(self._voice_tab(), "Voice")
        self.setCentralWidget(self.tabs)
        self.log_event("Dashboard initialized. System ready.")
        self.refresh_gestures_list()

    def log_event(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        if hasattr(self, "log_widget"):
            self.log_widget.append(entry)

    def _live_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.camera_label = QLabel("NEXUS Camera Stream (Stopped)")
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setMinimumSize(800, 480)
        self.camera_label.setStyleSheet("background: #080c12; color: #637788; font-size: 16px; border-radius: 8px; border: 1px solid #1a2533;")
        layout.addWidget(self.camera_label, 1)

        status_row = QHBoxLayout()
        self.gesture_label = QLabel("Gesture: none")
        self.gesture_label.setStyleSheet("font-weight: bold; color: #00e5ff;")
        self.confidence_label = QLabel("Confidence: 0.00")
        self.fps_label = QLabel("FPS: 0.0")
        self.hands_label = QLabel("Hands: 0 (left: no, right: no)")
        self.status_label = QLabel("Status: Stopped")
        self.status_label.setStyleSheet("font-weight: bold; color: #ff5252;")
        
        self.toggle_button = QPushButton("Start NEXUS")
        self.toggle_button.clicked.connect(self.toggle_worker)
        
        for widget in (
            self.gesture_label,
            self.confidence_label,
            self.fps_label,
            self.hands_label,
            self.status_label,
            self.toggle_button,
        ):
            status_row.addWidget(widget)
        layout.addLayout(status_row)
        return tab

    def _trainer_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        title = QLabel("User-Defined Gesture Recording & Machine Learning Trainer")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00a5cd;")
        layout.addWidget(title)
        
        desc = QLabel("Record custom gesture samples from camera and train a Random Forest classifier model.")
        desc.setStyleSheet("color: #8e9dae;")
        layout.addWidget(desc)
        
        form_row = QHBoxLayout()
        self.trainer_name = QLineEdit()
        self.trainer_name.setPlaceholderText("Gesture name (e.g., wave, peace_sign, thumbs_up)")
        form_row.addWidget(self.trainer_name, 2)
        
        self.trainer_samples = QSpinBox()
        self.trainer_samples.setRange(5, 8)
        self.trainer_samples.setValue(5)
        
        self.trainer_frames = QSpinBox()
        self.trainer_frames.setRange(15, 20)
        self.trainer_frames.setValue(15)
        
        form_row.addWidget(QLabel("Samples:"))
        form_row.addWidget(self.trainer_samples)
        form_row.addWidget(QLabel("Frames/Sample:"))
        form_row.addWidget(self.trainer_frames)
        
        self.record_button = QPushButton("1. Record Gesture")
        self.record_button.clicked.connect(self._record_gesture)
        form_row.addWidget(self.record_button)
        layout.addLayout(form_row)
        
        self.trainer_status = QLabel("Status: Ready")
        self.trainer_status.setStyleSheet("color: #00e5ff;")
        layout.addWidget(self.trainer_status)

        # Recorded Gestures & Training Panel
        middle_row = QHBoxLayout()
        left_box = QVBoxLayout()
        left_box.addWidget(QLabel("Recorded Gesture Classes:"))
        self.gesture_list_widget = QListWidget()
        left_box.addWidget(self.gesture_list_widget)
        
        btn_box = QHBoxLayout()
        self.train_model_btn = QPushButton("2. Train Custom Model (Random Forest)")
        self.train_model_btn.setStyleSheet("background: #00c853; font-size: 14px; font-weight: bold; padding: 10px;")
        self.train_model_btn.clicked.connect(self._train_custom_model)
        btn_box.addWidget(self.train_model_btn)
        left_box.addLayout(btn_box)
        
        middle_row.addLayout(left_box, 1)
        
        # Metrics & Log Output
        right_box = QVBoxLayout()
        right_box.addWidget(QLabel("Training Metrics & Status:"))
        self.train_output_log = QTextEdit()
        self.train_output_log.setReadOnly(True)
        right_box.addWidget(self.train_output_log)
        middle_row.addLayout(right_box, 1)
        
        layout.addLayout(middle_row)
        return tab

    def refresh_gestures_list(self):
        if not hasattr(self, "gesture_list_widget"):
            return
        self.gesture_list_widget.clear()
        try:
            from recorder import GestureRecorder
            rec = GestureRecorder()
            gestures = rec.list_gestures()
            if not gestures:
                self.gesture_list_widget.addItem("No custom gestures recorded yet.")
            else:
                for g_name, info in gestures.items():
                    samples = info.get("samples", 0)
                    self.gesture_list_widget.addItem(f"• {g_name} ({samples} sample file(s))")
        except Exception as e:
            self.gesture_list_widget.addItem(f"Error loading gestures: {e}")

    def _train_custom_model(self):
        if self.worker is not None and self.worker.isRunning():
            QMessageBox.warning(self, "NEXUS Trainer", "Please stop live NEXUS tracking before training the model.")
            return
        
        self.train_model_btn.setEnabled(False)
        self.trainer_status.setText("Status: Training Machine Learning Classifier...")
        self.train_output_log.append("Starting Random Forest Model training...")
        self.log_event("Training custom gesture ML classifier...")
        
        self.train_worker = ModelTrainerWorker()
        self.train_worker.completed.connect(self._on_training_completed)
        self.train_worker.failed.connect(self._on_training_failed)
        self.train_worker.finished.connect(lambda: self.train_model_btn.setEnabled(True))
        self.train_worker.start()

    def _on_training_completed(self, res):
        accuracy_pct = res.get("accuracy", 1.0) * 100.0
        classes = res.get("classes", [])
        counts = res.get("gesture_counts", {})
        
        msg = f"Training Successful! CV Accuracy: {accuracy_pct:.1f}% on {len(classes)} gesture(s)."
        self.trainer_status.setText(f"Status: {msg}")
        self.train_output_log.append(f"\nSUCCESS: {msg}")
        self.train_output_log.append(f"Classes: {', '.join(classes)}")
        self.train_output_log.append(f"Sample Frame Counts: {counts}")
        self.log_event(f"Custom ML Model trained successfully. Classes: {classes}, Acc: {accuracy_pct:.1f}%")
        self.refresh_bindings_table()

    def _on_training_failed(self, error):
        self.trainer_status.setText(f"Status: Training error: {error}")
        self.train_output_log.append(f"\nERROR: {error}")
        self.log_event(f"Training failed: {error}")

    def _voice_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        title = QLabel("Jarvis Offline Wake-Word Detection")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00a5cd;")
        layout.addWidget(title)
        
        desc = QLabel("Uses openWakeWord engine (ONNX Runtime) to detect 'Hey Jarvis' wake phrase in real-time.")
        desc.setStyleSheet("color: #8e9dae;")
        layout.addWidget(desc)
        
        self.voice_status = QLabel("Status: Idle. Click 'Start Jarvis' to enable microphone listener.")
        self.voice_status.setStyleSheet("color: #00e5ff; font-size: 14px; margin-top: 10px;")
        layout.addWidget(self.voice_status)
        
        self.voice_button = QPushButton("Start Jarvis")
        self.voice_button.clicked.connect(self._toggle_voice)
        layout.addWidget(self.voice_button)
        layout.addStretch()
        return tab

    def _bindings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        title = QLabel("NEXUS Active & Custom Gesture Action Bindings")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00a5cd;")
        layout.addWidget(title)
        
        # System Built-in Bindings Table
        sys_title = QLabel("Built-in Core Gestures:")
        sys_title.setStyleSheet("font-weight: bold; color: #00e5ff;")
        layout.addWidget(sys_title)
        
        table = QTableWidget(6, 3)
        table.setHorizontalHeaderLabels(["Gesture Name", "Physical Action", "System Triggered Action"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        bindings = [
            ("Cursor Movement", "Move Right Hand Index Finger Tip", "Move OS Cursor (Filtered One-Euro)"),
            ("Left Click", "Quick Pinch (Thumb + Index Finger)", "OS Mouse Left Click"),
            ("Drag & Drop", "Hold Pinch (Thumb + Index Finger > 0.5s)", "OS Mouse Hold Down / Drag"),
            ("Right Click", "Pinch (Thumb + Middle Finger)", "OS Mouse Right Click"),
            ("Vertical Scroll", "Pinch (Thumb + Pinky) & Move Hand Up/Down", "OS Mouse Scroll Wheel"),
            ("Precision Mode", "Pinch Left Hand (Thumb + Index)", "Dampen Sensitivity for Fine Pixels"),
        ]
        
        for row, (name, phys, act) in enumerate(bindings):
            table.setItem(row, 0, QTableWidgetItem(name))
            table.setItem(row, 1, QTableWidgetItem(phys))
            table.setItem(row, 2, QTableWidgetItem(act))
            
        layout.addWidget(table)

        # Custom Trained Gestures Table
        custom_title = QLabel("User-Defined Custom Gesture Action Mappings:")
        custom_title.setStyleSheet("font-weight: bold; color: #00e5ff; margin-top: 10px;")
        layout.addWidget(custom_title)
        
        self.custom_bindings_table = QTableWidget(0, 2)
        self.custom_bindings_table.setHorizontalHeaderLabels(["Custom Gesture Name", "Triggered Action"])
        self.custom_bindings_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.custom_bindings_table)
        
        save_btn = QPushButton("Save Custom Action Bindings")
        save_btn.clicked.connect(self._save_custom_bindings)
        layout.addWidget(save_btn)
        
        self.refresh_bindings_table()
        return tab

    def refresh_bindings_table(self):
        if not hasattr(self, "custom_bindings_table"):
            return
        
        trainer = get_trainer_instance()
        classes = trainer.classes_ if trainer else []
        
        self.custom_bindings_table.setRowCount(len(classes))
        action_options = [
            ("Media Play / Pause", "media_play_pause"),
            ("Mute Volume", "volume_mute"),
            ("Take Screenshot", "screenshot"),
            ("Toggle Desktop (Win+D)", "hotkey:win,d"),
            ("Switch App (Alt+Tab)", "hotkey:alt,tab"),
            ("Left Click", "left_click"),
            ("Right Click", "right_click"),
        ]
        
        for idx, c_name in enumerate(classes):
            self.custom_bindings_table.setItem(idx, 0, QTableWidgetItem(f"custom:{c_name}"))
            
            combo = QComboBox()
            for label, act_val in action_options:
                combo.addItem(label, act_val)
                
            current_bound = config.CUSTOM_BINDINGS.get(c_name, "media_play_pause")
            # Set combo index to match current_bound
            for i in range(combo.count()):
                if combo.itemData(i) == current_bound:
                    combo.setCurrentIndex(i)
                    break
            self.custom_bindings_table.setCellWidget(idx, 1, combo)

    def _save_custom_bindings(self):
        trainer = get_trainer_instance()
        classes = trainer.classes_ if trainer else []
        new_bindings = {}
        for idx, c_name in enumerate(classes):
            combo = self.custom_bindings_table.cellWidget(idx, 1)
            if combo is not None:
                act_val = combo.currentData()
                new_bindings[c_name] = act_val
                
        config.CUSTOM_BINDINGS = new_bindings
        config.save_bindings()
        self.log_event(f"Saved custom gesture bindings: {new_bindings}")
        QMessageBox.information(self, "NEXUS Bindings", "Custom gesture bindings saved successfully!")

    def _activity_log_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        title = QLabel("System Activity & Event Log")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00a5cd;")
        layout.addWidget(title)
        
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        layout.addWidget(self.log_widget)
        
        btn_layout = QHBoxLayout()
        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(lambda: self.log_widget.clear())
        btn_layout.addWidget(clear_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        return tab

    def _settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        title = QLabel("NEXUS Fine-Tuning & Threshold Configuration")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00a5cd;")
        layout.addWidget(title)
        
        form = QFormLayout()
        self.settings = {
            "PINCH_THRESHOLD": self._double_setting(form, "Pinch Threshold (Left Click)", config.PINCH_THRESHOLD),
            "RIGHT_PINCH_THRESHOLD": self._double_setting(form, "Right Pinch Threshold (Right Click)", config.RIGHT_PINCH_THRESHOLD),
            "SCROLL_PINCH_THRESHOLD": self._double_setting(form, "Scroll Pinch Threshold", config.SCROLL_PINCH_THRESHOLD),
            "DRAG_HOLD_SEC": self._double_setting(form, "Drag Hold Delay (seconds)", config.DRAG_HOLD_SEC),
            "SMOOTHING_MIN_CUTOFF": self._double_setting(form, "One-Euro Min Cutoff (Jitter)", config.SMOOTHING_MIN_CUTOFF),
            "SMOOTHING_BETA": self._double_setting(form, "One-Euro Beta (Lag Response)", config.SMOOTHING_BETA),
            "PRECISION_SENSITIVITY": self._double_setting(form, "Precision Mode Sensitivity", config.PRECISION_SENSITIVITY),
            "SCROLL_SENSITIVITY": self._int_setting(form, "Scroll Sensitivity Multiplier", config.SCROLL_SENSITIVITY),
            "ACTIVE_ZONE_MARGIN": self._double_setting(form, "Active Zone Camera Margin (0.0 - 0.4)", config.ACTIVE_ZONE_MARGIN),
            "CUSTOM_GESTURE_CONFIDENCE_THRESHOLD": self._double_setting(form, "Custom Gesture Min Confidence Threshold", config.CUSTOM_GESTURE_CONFIDENCE_THRESHOLD),
            "CUSTOM_GESTURE_COOLDOWN_SEC": self._double_setting(form, "Custom Gesture Cooldown (seconds)", config.CUSTOM_GESTURE_COOLDOWN_SEC),
        }
        layout.addLayout(form)
        
        apply_btn = QPushButton("Apply Settings")
        apply_btn.clicked.connect(self._apply_settings)
        layout.addWidget(apply_btn)
        layout.addStretch()
        return tab

    def _apply_settings(self):
        for name, control in self.settings.items():
            val = control.value()
            setattr(config, name, val)
        self.log_event("Settings updated and applied to config module.")
        QMessageBox.information(self, "NEXUS Settings", "Settings applied successfully!")

    @staticmethod
    def _double_setting(form, label, value):
        control = QDoubleSpinBox()
        control.setRange(0.001, 10.0)
        control.setDecimals(3)
        control.setSingleStep(0.01)
        control.setValue(value)
        form.addRow(label, control)
        return control

    @staticmethod
    def _int_setting(form, label, value):
        control = QSpinBox()
        control.setRange(1, 10000)
        control.setValue(value)
        form.addRow(label, control)
        return control

    def toggle_worker(self):
        if self.worker is not None and self.worker.isRunning():
            self.worker.stop()
            self.toggle_button.setEnabled(False)
            self.log_event("Stopping NEXUS vision thread...")
            return
        
        self._apply_settings_silent()
        self.worker = InferenceWorker()
        self.worker.frame_ready.connect(self._update_frame)
        self.worker.metrics_ready.connect(self._update_metrics)
        self.worker.status_ready.connect(self._update_status_label)
        self.worker.log_signal.connect(self.log_event)
        self.worker.failed.connect(self._show_error)
        self.worker.finished.connect(lambda: self.toggle_button.setEnabled(True))
        self.worker.finished.connect(lambda: self.toggle_button.setText("Start NEXUS"))
        
        self.toggle_button.setText("Stop NEXUS")
        self.log_event("Launching NEXUS computer vision pipeline...")
        self.worker.start()

    def _apply_settings_silent(self):
        for name, control in self.settings.items():
            setattr(config, name, control.value())

    def _update_status_label(self, status):
        self.status_label.setText(f"Status: {status}")
        if status == "Running":
            self.status_label.setStyleSheet("font-weight: bold; color: #00e676;")
        else:
            self.status_label.setStyleSheet("font-weight: bold; color: #ff5252;")

    def _update_frame(self, image):
        self.camera_label.setPixmap(
            QPixmap.fromImage(image).scaled(
                self.camera_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def _update_metrics(self, gesture, confidence, fps, hand_count, left, right):
        self.gesture_label.setText(f"Gesture: {gesture}")
        self.confidence_label.setText(f"Confidence: {confidence:.2f}")
        self.fps_label.setText(f"FPS: {fps:.1f}")
        self.hands_label.setText(
            f"Hands: {hand_count} (left: {'yes' if left else 'no'}, "
            f"right: {'yes' if right else 'no'})"
        )

    def _record_gesture(self):
        name = self.trainer_name.text().strip()
        if not name:
            self.trainer_status.setText("Status: Enter a gesture name first.")
            return
        if self.worker is not None and self.worker.isRunning():
            self.trainer_status.setText("Status: Stop NEXUS before recording a gesture.")
            return
        self.record_button.setEnabled(False)
        self.trainer_status.setText(
            "Status: Recorder window active. Press SPACE in camera window for each sample."
        )
        self.log_event(f"Starting gesture recording session for '{name}'...")
        self.recorder_worker = RecorderWorker(
            name, self.trainer_samples.value(), self.trainer_frames.value()
        )
        self.recorder_worker.completed.connect(self._recording_completed)
        self.recorder_worker.failed.connect(self._recording_failed)
        self.recorder_worker.finished.connect(lambda: self.record_button.setEnabled(True))
        self.recorder_worker.start()

    def _recording_completed(self, paths):
        msg = f"Saved {len(paths)} sample(s) successfully."
        self.trainer_status.setText(f"Status: {msg}")
        self.log_event(f"Gesture recorder finished. {msg}")
        self.refresh_gestures_list()

    def _recording_failed(self, message):
        self.trainer_status.setText(f"Status: Recording error: {message}")
        self.log_event(f"Gesture recorder error: {message}")

    def _toggle_voice(self):
        if getattr(self, "voice_worker", None) is not None and self.voice_worker.isRunning():
            self.voice_worker.stop()
            self.voice_button.setEnabled(False)
            self.log_event("Stopping Jarvis voice listener...")
            return
        self.voice_worker = VoiceWorker()
        self.voice_worker.heard.connect(
            lambda score: self.voice_status.setText(
                f"Status: Jarvis heard! Wake confidence: {score:.2f}"
            )
        )
        self.voice_worker.log_signal.connect(self.log_event)
        self.voice_worker.failed.connect(
            lambda message: self.voice_status.setText(f"Status: Voice error: {message}")
        )
        self.voice_worker.finished.connect(lambda: self.voice_button.setEnabled(True))
        self.voice_worker.finished.connect(lambda: self.voice_button.setText("Start Jarvis"))
        self.voice_button.setText("Stop Jarvis")
        self.voice_worker.start()

    def _show_error(self, message):
        self.status_label.setText(f"Status: Error - {message}")
        self.status_label.setStyleSheet("font-weight: bold; color: #ff5252;")
        self.toggle_button.setText("Start NEXUS")
        self.log_event(f"Fatal error: {message}")
        QMessageBox.critical(self, "NEXUS Engine Error", message)

    def closeEvent(self, event):
        if self.worker is not None and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(3000)
        if getattr(self, "voice_worker", None) is not None and self.voice_worker.isRunning():
            self.voice_worker.stop()
            self.voice_worker.wait(3000)
        event.accept()


def launch_dashboard():
    app = QApplication.instance() or QApplication([])
    window = Dashboard()
    window.show()
    return app.exec()
