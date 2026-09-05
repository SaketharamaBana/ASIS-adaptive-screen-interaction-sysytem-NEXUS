<div align="center">

# ⚡ NEXUS
### **Adaptive Touchless Interaction & Intelligent Gesture Control System**

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Computer Vision](https://img.shields.io/badge/MediaPipe-v0.10-00E5FF.svg)](https://ai.google.dev/edge/mediapipe/solutions/guide)
[![GUI Framework](https://img.shields.io/badge/PySide6-v6.7%2B-green.svg)](https://www.qt.io/qt-for-python)
[![ML Classifier](https://img.shields.io/badge/Scikit--Learn-RandomForest-orange.svg)](https://scikit-learn.org/)
[![Voice Engine](https://img.shields.io/badge/ONNX--Runtime-openWakeWord-purple.svg)](https://github.com/dscripka/openWakeWord)
[![License](https://img.shields.io/badge/license-MIT-brightgreen.svg)](#license)

---

**NEXUS** is an AI-powered, multi-modal touchless interaction system that converts webcam video feed and audio input into smooth, zero-latency desktop operating system controls. 

Built with modular Python architecture, NEXUS combines **MediaPipe Hand Landmark Tracking**, an adaptive **One-Euro Velocity Smoothing Filter**, a custom **Machine Learning Gesture Training Engine**, an offline **Jarvis Voice Trigger** (ONNX Runtime), and a dark-themed **PySide6 Control Dashboard**.

---
</div>

## 🌟 Key Features

- 🎯 **Sub-Pixel Cursor Tracking & One-Euro Filter**  
  Adapts smoothing strength dynamically based on hand movement speed—eliminating microscopic jitter when still while preserving ultra-fast response during quick gestures.

- 🖐️ **Built-in System Gestures**  
  - **Cursor Move**: Smooth tracking following the right index fingertip.
  - **Left Click**: Quick pinch between thumb and index finger.
  - **Drag & Drop**: Held pinch beyond $0.5\text{ s}$ activates OS mouse drag mode.
  - **Right Click**: Quick pinch between thumb and middle finger.
  - **Vertical Scroll**: Held pinch between thumb and pinky combined with vertical hand movement.
  - **Precision Mode Modifier**: Pinching left hand dampens cursor sensitivity by $65\%$ for pixel-accurate photo/video editing and graphic work.

- 🧠 **User-Defined Gesture Training Engine**  
  Collect custom hand landmark sequences directly from your camera and train a **Random Forest Classifier** in real-time. Features are translation-invariant and scale-invariant, allowing custom gestures to work reliably at any distance from the webcam.

- 🎙️ **Offline Jarvis Voice Engine & Spatial Fusion**  
  Uses **openWakeWord** powered by **ONNX Runtime** for local wake-word detection (*"Hey Jarvis"*) without cloud latency or privacy concerns. Integrates temporal cursor history to resolve deictic spoken references (*"click here"*, *"select this"*).

- 🔒 **Guardian Anti-Spoofing Liveness Checks**  
  Local verification primitives measuring natural micro-facial motion, blink detection, and voice energy variance to resist casual presentation or static photo replay attacks.

- 🖥️ **PySide6 Control Dashboard**  
  A dark-themed control center equipped with:
  - **Live Camera Stream** with real-time landmark overlays, gesture names, and FPS metrics.
  - **Gesture Trainer & ML Model Manager** with sample counts and cross-validation accuracy scoring.
  - **Custom Action Binding Matrix** (map gestures to Hotkeys, Media Play/Pause, Mute, Screenshot, Window Toggles).
  - **Live System Activity Log** with real-time timestamps.
  - **Interactive Configuration Panel** for tuning all threshold parameters.

---

## 🏗️ System Architecture

```
                                +-----------------------+
                                |     Webcam Input      |
                                +-----------+-----------+
                                            |
                                            v
                                +-----------+-----------+
                                |  MediaPipe Landmarker |
                                +-----------+-----------+
                                            |
                         +------------------+------------------+
                         |                                     |
                         v                                     v
             +-----------+-----------+             +-----------+-----------+
             |   One-Euro Filter     |             |  Gesture Recognition  |
             |   (Jitter Removal)    |             |    State Machine      |
             +-----------+-----------+             +-----------+-----------+
                         |                                     |
                         |                         +-----------+-----------+
                         |                         | Custom ML Classifier  |
                         |                         |    (RandomForest)     |
                         |                         +-----------+-----------+
                         |                                     |
                         +------------------+------------------+
                                            |
                                            v
                                +-----------+-----------+
                                |   Action Dispatcher   |
                                | (PyAutoGUI Controller)|
                                +-----------+-----------+
                                            |
                                            v
                                +-----------+-----------+
                                | OS Cursor / Mouse /   |
                                | Keyboard Trigger      |
                                +-----------------------+
```

---

## 📁 Repository Structure

```
ASIS-NEXUS-FINAL/
├── README.md                   # Core Project Documentation
├── .gitignore                  # Git Exclusion Rules
└── files/
    ├── main.py                 # Primary Entry Point (GUI & CLI modes)
    ├── config.py               # Tunable Thresholds & Configuration
    ├── capture.py              # Threaded Webcam Frame Grabber
    ├── filters.py              # One-Euro Signal Smoothing Filter
    ├── actions.py              # Central OS Action Dispatcher
    ├── gestures.py             # Gesture Recognition & State Machine
    ├── trainer.py              # Feature Extraction & ML Model Trainer
    ├── voice.py                # Offline Jarvis Wake-Word Detector
    ├── liveness.py             # Anti-Spoofing Guardian Liveness Signals
    ├── fusion.py               # Temporal Voice-Gesture Deictic Resolver
    ├── recorder.py             # Camera Dataset Sample Recorder
    ├── requirements.txt        # Python Dependency Manifest
    ├── NEXUS.spec              # PyInstaller Executable Build Spec
    └── ui/
        └── dashboard.py        # PySide6 Control Dashboard Interface
```

---

## 🚀 Quick Start & Installation

### 1. Prerequisites
Ensure Python **3.10+** is installed on your system.

### 2. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/SaketharamaBana/ASIS-adaptive-screen-interaction-sysytem-NEXUS.git
cd ASIS-adaptive-screen-interaction-sysytem-NEXUS

# Create virtual environment
python -m venv .venv

# Activate environment
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
cd files
pip install -r requirements.txt
```

### 4. Launch Application

#### Option A: PySide6 Control Dashboard Mode (Recommended)
```bash
python main.py
```

#### Option B: Headless / OpenCV Debug Window Mode
```bash
python main.py --cli
```

*Note: On first execution, MediaPipe landmark model files and openWakeWord ONNX models will automatically download (~10MB).*

---

## 🎮 Built-in Gestures Quick Reference

| Gesture | Physical Hand Action | Triggered Action |
|---|---|---|
| **Cursor Move** | Move right index fingertip | Move OS Cursor |
| **Left Click** | Quick pinch (Thumb + Index) | OS Left Click |
| **Drag & Drop** | Hold pinch (Thumb + Index > $0.5\text{ s}$) | OS Mouse Drag |
| **Right Click** | Quick pinch (Thumb + Middle) | OS Right Click |
| **Vertical Scroll** | Hold pinch (Thumb + Pinky) & move up/down | OS Scroll Wheel |
| **Precision Mode** | Pinch left hand (Thumb + Index) | Dampen sensitivity ($65\%$) |
| **Voice Command** | Speak *"Hey Jarvis"* into microphone | Trigger Voice Listener |

---

## 🧠 Training Custom User-Defined Gestures

1. Open the **NEXUS Dashboard** (`python main.py`).
2. Navigate to the **Trainer** tab.
3. Enter a custom gesture label (e.g. `wave`, `peace_sign`, `thumbs_up`).
4. Click **1. Record Gesture** and follow camera prompt (press `SPACE` to capture each sample).
5. Click **2. Train Custom Model (Random Forest)**. The model trains instantly and displays cross-validation accuracy.
6. Switch to the **Bindings** tab to assign custom actions:
   - **Media Play / Pause**
   - **Mute Volume**
   - **Take Screenshot**
   - **Toggle Desktop (`Win + D`)**
   - **Switch Window (`Alt + Tab`)**
   - **Custom Key Combination**

---

## ⚙️ Configuration & Tuning

All sensitivity values and thresholds are centralized in `config.py` and can also be adjusted live from the Dashboard **Settings** tab:

```python
# One-Euro filter tuning
SMOOTHING_MIN_CUTOFF = 0.8   # Lower = smoother, higher = faster
SMOOTHING_BETA = 0.4         # Speed coefficient

# Thresholds
PINCH_THRESHOLD = 0.045      # Left click pinch distance
RIGHT_PINCH_THRESHOLD = 0.045 # Right click pinch distance
DRAG_HOLD_SEC = 0.5          # Hold time to switch click to drag
ACTIVE_ZONE_MARGIN = 0.15    # Dead space margin around camera bounds
```

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

<div align="center">
  <sub>Built with ❤️ by Team NEXUS</sub>
</div>
