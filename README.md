# 🧠 NEXUS — Adaptive Touchless Interaction & Intelligent Gesture Control System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/OpenCV-4.9%2B-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV" />
  <img src="https://img.shields.io/badge/MediaPipe-Hand%20Tracking-FF6F00?style=for-the-badge" alt="MediaPipe" />
  <img src="https://img.shields.io/badge/PySide6-Desktop%20UI-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PySide6" />
  <img src="https://img.shields.io/badge/AI-Random%20Forest-00C853?style=for-the-badge" alt="Random Forest" />
</p>

<p align="center">
  <strong>Control your desktop naturally — without touching it.</strong>
</p>

<p align="center">
  Adaptive • Touchless • Multimodal • Real-Time • AI-Assisted
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-features">Features</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-custom-gesture-training">Training</a> •
  <a href="#-roadmap">Roadmap</a>
</p>

---

## 📌 Overview

**NEXUS (Adaptive Touchless Interaction & Intelligent Gesture Control System)** is a real-time multimodal Human-Computer Interaction (HCI) platform designed to control desktop environments using **hand gestures, voice commands, and AI-assisted gesture recognition**.

Instead of relying exclusively on a physical mouse and keyboard, NEXUS uses a webcam and microphone to interpret user intent and translate it into operating-system actions.

The system combines:

* 👋 Real-time hand landmark tracking
* 🖐️ Custom gesture recognition
* 🧠 Machine-learning-based gesture classification
* 🎙️ Offline voice activation
* 🖱️ Touchless mouse and cursor control
* ⌨️ Keyboard shortcut automation
* 🎵 Media control
* 📸 Screenshot actions
* 🎛️ Configurable action bindings
* 🖥️ PySide6 monitoring dashboard
* 🔄 Gesture-state filtering and smoothing
* 🛡️ Lightweight liveness/anti-spoofing signals

The goal is to create a **natural, low-latency, extensible interaction layer between humans and desktop computers**.

---

# 🎯 Why NEXUS?

Traditional desktop interaction depends heavily on physical input devices.

NEXUS explores an alternative interaction model:

```text
Human Intent
     │
     ▼
Hand / Voice Input
     │
     ▼
Perception
     │
     ▼
Feature Extraction
     │
     ▼
Gesture / Intent Recognition
     │
     ▼
State Validation & Filtering
     │
     ▼
Action Dispatcher
     │
     ▼
Operating System
```

This architecture allows NEXUS to evolve beyond simple gesture detection into a broader **multimodal desktop interaction framework**.

---

# ✨ Features

## 👋 Real-Time Hand Tracking

NEXUS uses webcam input and MediaPipe-based hand landmark detection to identify hand position and movement in real time.

Capabilities include:

* Hand landmark detection
* Finger position tracking
* Pinch detection
* Distance-based gesture detection
* Motion analysis
* Left/right hand interpretation
* Temporal gesture state tracking

---

## 🖱️ Touchless Cursor Control

Move the desktop cursor using your index fingertip.

### Supported interactions

| Gesture                              | Action                |
| ------------------------------------ | --------------------- |
| ☝️ Index fingertip movement          | Cursor movement       |
| 🤏 Thumb + index pinch               | Left click            |
| 🤏 Thumb + middle pinch              | Right click           |
| 🤏 Hold thumb + index                | Drag                  |
| 🤏 Thumb + pinky + vertical movement | Scroll                |
| 🤏 Left-hand pinch                   | Precision cursor mode |

NEXUS applies smoothing and filtering to reduce unwanted cursor jitter.

---

# 🧠 AI Gesture Recognition

NEXUS includes a **custom gesture-learning pipeline**.

Users can record their own gestures, extract features, train a machine-learning model, and associate the resulting gesture with a desktop action.

### Pipeline

```text
Camera
  ↓
Hand Landmarks
  ↓
Feature Extraction
  ↓
Gesture Dataset
  ↓
Random Forest Training
  ↓
Gesture Prediction
  ↓
Confidence Filtering
  ↓
Action Binding
```

This allows the system to support gestures beyond its built-in interaction rules.

---

# 🎙️ Voice Interaction

NEXUS supports optional offline voice activation through **openWakeWord**.

The voice layer is designed to complement gesture interaction rather than replace it.

Example architecture:

```text
Microphone
    ↓
Wake Word Detection
    ↓
Voice Intent
    ↓
Command Router
    ↓
Action Dispatcher
```

This creates a multimodal interaction model where users can combine:

**gesture + voice + desktop automation**

---

# 🤖 Multimodal Interaction

One of NEXUS's core design goals is combining multiple input modalities.

```text
             ┌──────────────┐
             │   Webcam     │
             └──────┬───────┘
                    │
                    ▼
             Hand Perception
                    │
                    ▼
             Gesture Engine
                    │
                    │
                    ▼
              ┌───────────┐
              │   Fusion  │
              │   Layer   │
              └─────┬─────┘
                    ▲
                    │
             Voice Perception
                    ▲
                    │
             ┌──────┴───────┐
             │ Microphone   │
             └──────────────┘

                    │
                    ▼
            Intent / Action
                    │
                    ▼
            Action Dispatcher
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
      Mouse      Keyboard      Media
```

The modular fusion layer provides a foundation for future context-aware interaction.

---

# 🏗️ Architecture

NEXUS follows a modular architecture where perception, processing, decision-making, and execution are separated.

```text
┌─────────────────────────────────────────────┐
│                 INPUT LAYER                 │
├───────────────────┬─────────────────────────┤
│ Webcam            │ Microphone              │
└─────────┬─────────┴────────────┬────────────┘
          │                      │
          ▼                      ▼
┌───────────────────┐  ┌──────────────────────┐
│ Hand Perception   │  │ Voice / Wake Word    │
│ MediaPipe/OpenCV  │  │ openWakeWord         │
└─────────┬─────────┘  └──────────┬───────────┘
          │                       │
          ▼                       ▼
┌─────────────────────────────────────────────┐
│            FEATURE / SIGNAL LAYER            │
│                                             │
│ Smoothing • Filtering • Pinch Detection    │
│ Motion Analysis • Feature Extraction       │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│             INTELLIGENCE LAYER              │
│                                             │
│ Gesture State Machine                       │
│ Rule-Based Gestures                         │
│ Custom ML Gesture Classifier                │
│ Confidence Filtering                        │
│ Multimodal Fusion                           │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│              ACTION DISPATCHER              │
├──────────────┬──────────────┬───────────────┤
│ Mouse        │ Keyboard     │ Media         │
│ Cursor       │ Hotkeys      │ Screenshot    │
│ Click        │ Shortcuts    │ Custom Action │
│ Drag         │              │               │
│ Scroll       │              │               │
└──────────────┴──────────────┴───────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Desktop / OS    │
              └─────────────────┘
```

---

# 🔬 Core Processing Pipeline

The complete NEXUS runtime pipeline is approximately:

```text
Camera Frame
     ↓
Frame Capture
     ↓
Hand Landmark Detection
     ↓
Landmark Normalization
     ↓
Feature Extraction
     ↓
Temporal Filtering
     ↓
Gesture State Evaluation
     ↓
Rule-Based / ML Recognition
     ↓
Confidence Validation
     ↓
Action Resolution
     ↓
Action Dispatcher
     ↓
Operating System
```

For voice:

```text
Microphone
     ↓
Wake Word Detection
     ↓
Voice Intent
     ↓
Command Resolution
     ↓
Action Dispatcher
```

---

# 🖐️ Core Gesture Controls

| Gesture                 | Detection             | Desktop Action |
| ----------------------- | --------------------- | -------------- |
| ☝️ Index movement       | Right index fingertip | Move cursor    |
| 🤏 Thumb + index pinch  | Finger distance       | Left click     |
| 🤏 Thumb + middle pinch | Finger distance       | Right click    |
| 🤏 Hold thumb + index   | Persistent pinch      | Drag           |
| 🤏 Thumb + pinky        | Vertical movement     | Scroll         |
| ✋ Left-hand pinch       | Left-hand state       | Precision mode |
| 🧠 Trained gesture      | ML classifier         | Custom action  |

---

# ⚡ Precision Cursor Mode

Fast cursor movement is useful for navigation, but precise interaction can be difficult.

NEXUS therefore provides a precision mode that reduces cursor sensitivity.

```text
Normal Mode
     ↓
Fast cursor movement

Precision Mode
     ↓
Reduced movement sensitivity
     ↓
More accurate positioning
```

This is particularly useful for:

* Small UI elements
* Design applications
* Text selection
* Buttons
* Fine cursor positioning

---

# 🎛️ Action Dispatcher

All interaction commands are routed through a centralized action layer.

This prevents gesture recognition code from becoming tightly coupled to operating-system operations.

Example:

```text
Gesture
   ↓
Recognition
   ↓
Action Name
   ↓
ActionDispatcher
   ↓
OS Operation
```

Supported action categories include:

| Category | Examples                      |
| -------- | ----------------------------- |
| Mouse    | Move, click, drag, scroll     |
| Keyboard | Hotkeys and shortcuts         |
| Media    | Play/pause, mute              |
| System   | Screenshot and other commands |
| Custom   | User-defined bindings         |

This makes the architecture easier to extend.

---

# 🧪 Custom Gesture Training

NEXUS allows users to create their own gesture vocabulary.

### Step 1 — Record

Open the trainer and define a label.

Example:

```text
wave
peace
thumbs_up
open_palm
```

### Step 2 — Capture Samples

Record multiple examples of the gesture.

```text
Gesture
   ↓
Multiple Frames
   ↓
Feature Extraction
   ↓
Dataset
```

### Step 3 — Train

The local training pipeline trains a Random Forest classifier.

```text
Training Dataset
       ↓
Feature Matrix
       ↓
Random Forest
       ↓
Saved Model
```

### Step 4 — Bind

Associate the trained gesture with an action.

Example:

```text
"peace"
   ↓
Screenshot
```

or:

```text
"thumbs_up"
   ↓
Play / Pause
```

---

# 💻 Command-Line Training

From the `files` directory:

```bash
python recorder.py wave --samples 5 --frames 15
```

Then train:

```bash
python trainer.py
```

Generated training data is stored locally and is intentionally excluded from the main repository.

---

# 📊 Technology Stack

| Technology          | Purpose                       |
| ------------------- | ----------------------------- |
| Python 3.10+        | Core application              |
| OpenCV              | Camera and image processing   |
| MediaPipe           | Hand landmark tracking        |
| PySide6             | Desktop dashboard             |
| Random Forest       | Custom gesture classification |
| openWakeWord        | Offline wake-word detection   |
| NumPy               | Numerical processing          |
| scikit-learn        | Machine learning              |
| PyAutoGUI / OS APIs | Desktop interaction           |

---

# 📁 Project Structure

```text
ASIS-adaptive-screen-interaction-sysytem-NEXUS/
│
├── README.md
├── .gitignore
│
└── files/
    │
    ├── main.py
    ├── config.py
    ├── capture.py
    ├── filters.py
    ├── gestures.py
    ├── actions.py
    ├── fusion.py
    ├── liveness.py
    ├── voice.py
    ├── recorder.py
    ├── trainer.py
    │
    ├── requirements.txt
    ├── NEXUS.spec
    │
    └── ui/
        └── dashboard.py
```

### Module Responsibilities

| Module         | Responsibility                      |
| -------------- | ----------------------------------- |
| `main.py`      | Application entry point             |
| `capture.py`   | Webcam/frame capture                |
| `filters.py`   | Signal smoothing and filtering      |
| `gestures.py`  | Gesture recognition and state logic |
| `actions.py`   | Desktop action dispatcher           |
| `fusion.py`    | Multimodal interaction logic        |
| `liveness.py`  | Lightweight anti-spoofing signals   |
| `voice.py`     | Voice/wake-word processing          |
| `recorder.py`  | Gesture dataset collection          |
| `trainer.py`   | Gesture ML training                 |
| `config.py`    | Runtime configuration               |
| `dashboard.py` | PySide6 user interface              |

---

# 🚀 Quick Start

## 1. Clone the Repository

```bash
git clone https://github.com/SaketharamaBana/ASIS-adaptive-screen-interaction-sysytem-NEXUS.git
```

```bash
cd ASIS-adaptive-screen-interaction-sysytem-NEXUS
```

---

## 2. Create a Virtual Environment

### Windows

```powershell
python -m venv .venv
```

Activate:

```powershell
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv .venv
```

Activate:

```bash
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
cd files
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

---

# ▶️ Running NEXUS

## Dashboard Mode

```bash
python main.py
```

This launches the PySide6 dashboard.

---

## CLI / Debug Mode

```bash
python main.py --cli
```

Use this mode when debugging perception, gesture recognition, or runtime behavior.

---

# 🎮 Runtime Controls

| Key | Function                          |
| --- | --------------------------------- |
| `q` | Quit                              |
| `c` | Reset smoothing and gesture state |

Additional controls may depend on the active dashboard configuration.

---

# ⚙️ Configuration

Most runtime parameters can be adjusted in:

```text
files/config.py
```

Configuration includes:

* Camera index
* Frame resolution
* Frame processing settings
* Pinch thresholds
* Cursor sensitivity
* Drag delay
* Scroll sensitivity
* Smoothing parameters
* Gesture confidence thresholds
* Custom action bindings

Example conceptual configuration:

```text
Camera
 ├── Index
 ├── Resolution
 └── FPS

Gesture
 ├── Pinch threshold
 ├── Confidence threshold
 └── Gesture timing

Cursor
 ├── Sensitivity
 ├── Smoothing
 └── Precision multiplier
```

---

# 🧩 Design Principles

NEXUS is designed around several engineering principles.

### 1. Modularity

Perception, intelligence, and action execution are separated.

### 2. Low Latency

The runtime pipeline is optimized for responsive interaction.

### 3. Extensibility

New gestures and actions can be added without redesigning the complete system.

### 4. Personalization

Users can train custom gestures for their own workflows.

### 5. Multimodal Interaction

Hand and voice inputs can coexist within the same interaction framework.

### 6. Local Processing

Where supported, perception and voice activation can operate locally without requiring cloud processing.

---

# 🛡️ Liveness & Security

NEXUS includes lightweight liveness/anti-spoofing signals as part of its interaction pipeline.

However:

> **NEXUS is not a biometric authentication system.**

The liveness mechanisms are intended to improve interaction reliability and reduce accidental or spoofed interaction signals.

They should **not** be used as a replacement for:

* Password authentication
* OS security
* Multi-factor authentication
* Enterprise identity systems
* Dedicated biometric authentication

---

# 🔐 Privacy

NEXUS is designed around local desktop interaction.

Camera and microphone inputs are used for interaction processing when those features are enabled.

Users should review the application's dependencies, permissions, and configuration before deploying NEXUS in sensitive environments.

Do not record or process other people's biometric or voice data without appropriate consent.

---

# 🧯 Troubleshooting

## Camera does not open

Check:

```text
files/config.py
```

and verify the configured camera index.

Try:

```text
CAM_INDEX = 0
```

or another available camera index.

---

## Cursor does not move

Check:

* Camera permissions
* OS accessibility/input permissions
* Cursor-control configuration
* Gesture detection
* Whether another application is capturing the input device

---

## Gesture recognition is unstable

Try:

* Improving lighting
* Keeping the hand inside the camera frame
* Increasing gesture samples
* Adjusting smoothing parameters
* Adjusting pinch thresholds
* Retraining the custom gesture model

---

## Wake word does not trigger

Verify:

* Microphone permissions
* Correct audio input device
* Required voice dependencies
* Wake-word configuration

---

## Custom gesture training fails

Ensure:

* Enough samples are recorded
* Gestures are visually distinct
* The hand remains visible
* Training data is generated successfully
* Required ML dependencies are installed

---

# 📈 Performance Considerations

Real-time interaction depends on several factors:

```text
Camera FPS
     ↓
Hand Detection
     ↓
Feature Processing
     ↓
Gesture Classification
     ↓
Filtering
     ↓
Action Execution
```

Performance can vary based on:

* CPU/GPU capability
* Camera resolution
* Number of hands tracked
* Lighting conditions
* Operating system
* Background applications
* Model complexity

For smoother interaction, use a reasonable webcam resolution and avoid unnecessary background processing.

---

# 🗺️ Roadmap

NEXUS is designed as an extensible research and engineering project.

### ✅ Current

* [x] Real-time hand tracking
* [x] Gesture-based cursor control
* [x] Mouse click control
* [x] Drag interaction
* [x] Scroll interaction
* [x] Precision cursor mode
* [x] Custom gesture recording
* [x] Random Forest gesture classifier
* [x] Voice wake-word integration
* [x] Action dispatcher
* [x] PySide6 dashboard
* [x] Lightweight liveness layer

### 🔄 Planned

* [ ] Improved temporal gesture recognition
* [ ] More advanced multimodal fusion
* [ ] Expanded gesture library
* [ ] Gesture visualization and analytics
* [ ] Per-user gesture calibration
* [ ] Improved cross-platform automation
* [ ] Configurable gesture profiles
* [ ] Performance telemetry
* [ ] Plugin-based action system
* [ ] Optional model upgrade path
* [ ] Improved accessibility workflows

---

# 💡 Example Use Cases

NEXUS can be useful for:

### 🖥️ Desktop Productivity

Hands-free cursor and keyboard interaction.

### 📊 Presentations

Navigate slides without touching the laptop.

### ♿ Accessibility

Explore alternative interaction methods for users who may have difficulty using traditional input devices.

### 🎨 Creative Applications

Use precision cursor mode for fine interaction.

### 🎮 Experimental HCI

Research gesture-driven human-computer interaction.

### 🏠 Hands-Free Computing

Interact with desktop applications when touching a physical device is inconvenient.

---

# 🔭 Future Vision

The long-term goal of NEXUS is to evolve from a gesture-control application into an **adaptive desktop interaction platform**.

The envisioned system can combine:

```text
Vision
  +
Voice
  +
Gesture
  +
Context
  +
Personalization
  +
AI
```

to create a more natural human-computer interface.

Instead of asking users to learn rigid commands, the system can progressively learn how users prefer to interact with their environment.

---

# 🧪 Research Direction

NEXUS provides a practical foundation for experimentation in:

* Human-Computer Interaction
* Computer Vision
* Gesture Recognition
* Machine Learning
* Multimodal Interaction
* Accessibility Engineering
* Intelligent Interfaces
* Real-Time Systems
* Desktop Automation

---

# 🤝 Contributing

Contributions, ideas, improvements, and experiments are welcome.

A typical contribution workflow:

```bash
git clone <repository>
```

Create a branch:

```bash
git checkout -b feature/my-feature
```

Make your changes, test them locally, and submit a pull request.

When contributing, please keep modules focused and avoid tightly coupling gesture detection with OS actions.

---

# 📜 License

This project is distributed under the **MIT License**.

See the repository license file for details.

---

# 🔗 Repository

<p align="center">

<a href="https://github.com/SaketharamaBana/ASIS-adaptive-screen-interaction-sysytem-NEXUS">
<img src="https://img.shields.io/badge/GitHub-NEXUS%20Repository-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub Repository"/>
</a>

</p>

**Repository:**
`SaketharamaBana/ASIS-adaptive-screen-interaction-sysytem-NEXUS`

---

# 👨‍💻 Project

**NEXUS — Adaptive Touchless Interaction & Intelligent Gesture Control System**

Built with:

```text
Python
OpenCV
MediaPipe
PySide6
scikit-learn
openWakeWord
Computer Vision
Machine Learning
Desktop Automation
```

<p align="center">
  <strong>👋 Interact naturally. 🧠 Let the system understand. ⚡ Control your desktop.</strong>
</p>
