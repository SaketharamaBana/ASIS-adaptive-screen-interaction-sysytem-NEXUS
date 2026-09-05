# NEXUS

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/OpenCV-4.9+-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV" />
  <img src="https://img.shields.io/badge/MediaPipe-Hand%20Tracking-FF6F00?style=for-the-badge" alt="MediaPipe" />
  <img src="https://img.shields.io/badge/PySide6-GUI-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PySide6" />
  <img src="https://img.shields.io/badge/ML-Random%20Forest-00C853?style=for-the-badge" alt="Random Forest" />
</p>

<p align="center">
  <strong>Adaptive touchless interaction system for desktop control</strong>
</p>

NEXUS is a real-time multimodal desktop interaction system that turns hand motion,
voice, and lightweight liveness checks into cursor and system actions. It is
built around MediaPipe hand tracking, a One Euro smoothing filter, explicit
gesture state logic, and an optional custom gesture trainer for user-defined
commands.

> Use this project only on a machine where you are comfortable granting camera,
> microphone, and simulated input access.

## Highlights

- Real-time hand tracking with MediaPipe Hand Landmarker
- Smooth cursor control using a One Euro filter
- Pointer, click, drag, right-click, and scroll gestures
- Precision mode with a left-hand pinch modifier
- Offline wake-word detection for "Hey Jarvis"
- Custom gesture recording and Random Forest training
- Live desktop dashboard built with PySide6
- Gesture-to-action routing through a central ActionDispatcher

## Architecture

```text
Webcam + Microphone
        │
        ▼
Hand Tracking + Voice Input
        │
        ▼
Filtering + Gesture State + Custom ML
        │
        ▼
Action Dispatcher
        │
        ▼
Cursor / Mouse / Scroll / Hotkeys / Media Controls
```

## Supported interaction patterns

- Right hand index fingertip tracks the cursor
- Quick thumb-index pinch triggers left click
- Held thumb-index pinch triggers drag
- Thumb-middle pinch triggers right click
- Thumb-pinky pinch + vertical motion triggers scroll
- Left-hand pinch enables precision cursor mode
- Custom trained gestures can trigger hotkeys or media commands

## Requirements

- Python 3.10+
- Webcam
- Optional microphone for wake-word detection
- Windows/macOS/Linux desktop environment

## Installation

Clone the repository:

```bash
git clone https://github.com/SaketharamaBana/ASIS-adaptive-screen-interaction-sysytem-NEXUS.git
cd ASIS-adaptive-screen-interaction-sysytem-NEXUS
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
cd files
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The MediaPipe hand model downloads automatically on first launch.

## Run the project

From the `files/` directory:

```bash
# Recommended: GUI dashboard
python main.py

# Debug mode with OpenCV window
python main.py --cli
```

Controls in debug mode:

- `q` — quit
- `c` — reset smoothing and gesture state

## Custom gesture training

The trainer is designed for local user-defined gestures.

1. Open the dashboard and go to the Trainer tab.
2. Enter a gesture name.
3. Record multiple samples from the camera.
4. Train the Random Forest classifier.
5. Bind the recognized gesture to an action.

You can also use the command-line recorder:

```bash
cd files
python recorder.py wave --samples 5 --frames 15
python trainer.py
```

This writes local data to `gesture_data/` and keeps it outside the Git-tracked project files.

## Project structure

```text
ASIS-adaptive-screen-interaction-sysytem-NEXUS/
├── README.md
├── .gitignore
└── files/
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
    ├── requirements.txt
    ├── NEXUS.spec
    └── ui/
        └── dashboard.py
```

## Configuration

Most runtime behavior is controlled in [`files/config.py`](files/config.py), including:

- camera selection
- gesture thresholds
- drag timing
- scroll sensitivity
- smoothing parameters
- custom gesture confidence

## Troubleshooting

- Camera not detected: try a different `CAM_INDEX` in `files/config.py`
- Hand model download fails: check your internet connection and retry
- Cursor not moving: verify OS permissions and accessibility input access
- Wake-word not triggering: confirm your microphone is connected and available to Python
- Training not working: record enough samples before training the model

## Safety and notes

NEXUS is a research-oriented interaction tool and is not a full security system.
The liveness checks are intended as low-cost replay-resistance signals, not a
complete biometric authentication mechanism.

## License

This project is distributed under the MIT license.

## Repository

- GitHub: https://github.com/SaketharamaBana/ASIS-adaptive-screen-interaction-sysytem-NEXUS
