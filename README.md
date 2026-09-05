# NEXUS

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/OpenCV-4.9+-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV" />
  <img src="https://img.shields.io/badge/MediaPipe-Hand%20Tracking-FF6F00?style=for-the-badge" alt="MediaPipe" />
  <img src="https://img.shields.io/badge/PySide6-Dashboard-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PySide6" />
  <img src="https://img.shields.io/badge/AI-Gesture%20Control-00C853?style=for-the-badge" alt="Gesture AI" />
</p>

<p align="center">
  <strong>Adaptive touchless interaction for desktop control</strong>
</p>

NEXUS is a multimodal human-computer interaction system that lets you control a computer using natural hand gestures, optional voice commands, and lightweight AI-assisted interaction logic. It combines webcam tracking, real-time filtering, custom gesture recognition, and desktop automation into a single touchless control experience.

<p align="center">
  <a href="#quick-start"><img src="https://img.shields.io/badge/Quick%20Start-Get%20Started-0EA5E9?style=for-the-badge" alt="Get started" /></a>
  <a href="#features"><img src="https://img.shields.io/badge/Features-Explore-8B5CF6?style=for-the-badge" alt="Explore features" /></a>
  <a href="https://github.com/SaketharamaBana/ASIS-adaptive-screen-interaction-sysytem-NEXUS" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/GitHub-Repository-111827?style=for-the-badge&logo=github&logoColor=white" alt="GitHub repository" /></a>
</p>

> Built for desktop interaction workflows where touchless control is useful, such as presentation control, accessibility, and hands-free productivity.

## At a glance

| Area | Capability |
| --- | --- |
| Input | Webcam hand tracking, mic wake word, optional face/voice liveness signals |
| Output | Cursor movement, clicks, drags, scroll, hotkeys, media controls |
| Intelligence | Gesture state machine + Random Forest custom model |
| UI | PySide6 dashboard for live monitoring and configuration |
| Platform | Windows, macOS, Linux desktop environments |

## Why NEXUS

NEXUS is designed to make gesture-driven interaction feel responsive and natural without requiring a physical controller. The project focuses on:

- low-latency cursor control
- intuitive hand gestures for everyday OS actions
- modular action routing for future expansion
- user-defined custom gestures for personalized workflows
- multimodal fusion between hand motion and voice intent

## Features

<div align="center">

| Feature | Description |
| --- | --- |
| Real-time hand tracking | MediaPipe Hand Landmarker detects and tracks hand landmarks from the webcam. |
| Gesture control | Cursor movement, click, drag, scroll, and precision mode from hand motion. |
| Voice commands | Offline wake-word detection with openWakeWord for local voice activation. |
| Custom gesture AI | Record gestures and train a Random Forest model to trigger actions. |
| Dashboard UI | Control and monitor the system from a clean PySide6 interface. |
| Modular actions | Centralized dispatcher handles cursor, mouse, hotkeys, screenshot, and media commands. |

</div>

## Core gestures

| Gesture | Trigger | Action |
| --- | --- | --- |
| Cursor move | Right index fingertip | Moves the desktop cursor |
| Left click | Thumb + index pinch | Performs left click |
| Right click | Thumb + middle pinch | Performs right click |
| Drag | Hold thumb + index pinch | Mouse drag |
| Scroll | Thumb + pinky pinch + vertical motion | Mouse wheel scroll |
| Precision mode | Left-hand pinch | Slower, more controlled cursor movement |
| Custom action | Trained gesture model | Executes bound action |

## Workflow

```text
Camera + Microphone
      ↓
Hand / Voice Perception
      ↓
Gesture State + Feature Filtering
      ↓
Action Dispatcher
      ↓
Desktop Cursor + Mouse + Hotkeys + Media Control
```

## Built-in actions

NEXUS routes gestures through a shared action layer, making it easy to trigger real desktop functions from either a gesture or a custom binding.

| Action | Example trigger | Result |
| --- | --- | --- |
| Left click | Thumb + index pinch | Simulates a left mouse click |
| Right click | Thumb + middle pinch | Simulates a right mouse click |
| Drag | Hold pinch | Presses and holds the mouse for drag operations |
| Scroll | Thumb + pinky pinch + vertical movement | Scrolls the active window |
| Play / Pause | Custom gesture binding | Sends media play/pause command |
| Mute | Custom gesture binding | Toggles system volume mute |
| Screenshot | Custom gesture binding | Takes a screenshot |
| Hotkey | `hotkey:ctrl,shift,s` | Executes custom keyboard shortcut |
| Precision move | Left-hand pinch | Slows cursor motion for fine control |

Custom actions are defined through the binding system and are interpreted by the shared `ActionDispatcher`.

## Quick start

### 1) Clone and install

```bash
git clone https://github.com/SaketharamaBana/ASIS-adaptive-screen-interaction-sysytem-NEXUS.git
cd ASIS-adaptive-screen-interaction-sysytem-NEXUS
python -m venv .venv
```

Windows:

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

### 2) Run NEXUS

```bash
# GUI dashboard
python main.py

# Debug view
python main.py --cli
```

### 3) Controls

- `q` — quit
- `c` — reset smoothing and gesture state

## Custom gesture training

You can extend NEXUS with your own gestures through the local trainer.

1. Open the dashboard and go to the Trainer tab.
2. Enter a gesture label such as `wave` or `peace`.
3. Record multiple samples from the camera.
4. Train the model.
5. Bind the trained gesture to a hotkey or media action.

Command-line example:

```bash
cd files
python recorder.py wave --samples 5 --frames 15
python trainer.py
```

The generated gesture data is stored locally in `gesture_data/` and is not part of the main codebase.

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

Most tuning parameters live in [`files/config.py`](files/config.py). This includes:

- camera index and frame settings
- pinch thresholds
- drag delays
- scroll sensitivity
- smoothing filter parameters
- custom gesture confidence thresholds

## Troubleshooting

- Camera not opening: try a different `CAM_INDEX` in `files/config.py`
- Model download fails: verify internet connectivity and try again
- Cursor is not responding: check OS accessibility and input permissions
- Wake-word does not trigger: confirm microphone access and installed dependencies
- Custom training fails: record enough gesture samples before training the model

## Safety note

NEXUS is a research-oriented interaction system and is not a complete biometric security solution. The liveness modules provide lightweight anti-spoofing signals, but they should not be treated as a standalone authentication system.

## License

Distributed under the MIT License.

## Repository

- GitHub: https://github.com/SaketharamaBana/ASIS-adaptive-screen-interaction-sysytem-NEXUS
