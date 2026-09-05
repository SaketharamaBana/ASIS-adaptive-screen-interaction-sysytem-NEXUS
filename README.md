# NEXUS

## Adaptive touchless interaction for desktop computers

NEXUS is a real-time, multimodal human-computer interaction system that lets
you control a desktop with hand gestures. It combines webcam-based hand
tracking, adaptive cursor smoothing, gesture state management, optional
custom gesture classification, and an offline "Hey Jarvis" wake-word
detector.

> NEXUS controls the operating-system cursor and mouse. Run it only when you
> are comfortable granting the application camera, microphone, and input
> control access.

## What it can do

- Track up to two hands with MediaPipe Hand Landmarker.
- Move the cursor with the right index fingertip.
- Left-click with a quick thumb-and-index pinch.
- Drag by holding a thumb-and-index pinch.
- Right-click with a thumb-and-middle-finger pinch.
- Scroll by holding a thumb-and-pinky pinch and moving vertically.
- Enable a left-hand precision modifier for slower cursor movement.
- Smooth cursor movement with a One Euro filter.
- Use an optional PySide6 dashboard with live camera preview and controls.
- Listen locally for the "Hey Jarvis" wake word with openWakeWord.
- Record, train, and use user-defined gestures with a Random Forest model.
- Resolve recent cursor positions for deictic voice references such as
  "click here".

## How it works

```text
Camera + microphone
        |
        v
MediaPipe hand landmarks + wake-word detection
        |
        v
Filtering, gesture state, custom model, and temporal fusion
        |
        v
Action dispatcher
        |
        v
Cursor, mouse, scroll, hotkeys, and media controls
```

The standard gesture pipeline uses normalized hand landmarks and explicit
state transitions, so a held pinch becomes a drag rather than repeated
clicks. Cursor updates are dispatched on a separate thread to keep vision
processing responsive.

## Requirements

- Windows, macOS, or Linux with a working webcam
- Python 3.10 or newer
- A microphone for the optional wake-word feature
- OS permissions for camera, microphone, and simulated input

The default dashboard is most useful on a desktop environment. Headless
servers and environments without a display, camera, or audio device are not
supported.

## Installation

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/SaketharamaBana/ASIS-adaptive-screen-interaction-sysytem-NEXUS.git
cd ASIS-adaptive-screen-interaction-sysytem-NEXUS

python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS/Linux
source .venv/bin/activate
```

Install the application dependencies. The source files and dependency
manifest are currently kept in `files/`:

```bash
cd files
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The MediaPipe hand-landmarker model is downloaded automatically on the first
run into `files/hand_landmarker.task`. The downloaded model is ignored by
Git.

## Running NEXUS

From the `files/` directory:

```bash
# Launch the PySide6 dashboard (recommended)
python main.py

# Launch the OpenCV debug view without the dashboard
python main.py --cli
```

Press `q` in the OpenCV debug window to quit. Press `c` to reset cursor
smoothing and gesture state.

If the camera is not detected, change `CAM_INDEX` in
[`files/config.py`](files/config.py). The same file contains thresholds for
pinches, drag timing, scroll sensitivity, cursor smoothing, and custom
gesture confidence.

## Training custom gestures

Custom gestures are recorded locally and are not committed to the repository.
The dashboard exposes the complete workflow:

1. Open the **Trainer** tab.
2. Enter a gesture name.
3. Record several camera samples.
4. Train the Random Forest classifier.
5. Open **Bindings** and assign an action.

The command-line recorder can also be used from `files/`:

```bash
python recorder.py wave --samples 5 --frames 15
python trainer.py
```

Training writes `gesture_data/manifest.json`, sample data, and the trained
model under `gesture_data/`. These files are intentionally ignored because
they are local user data.

Supported custom actions include media play/pause, mute, screenshots,
left/right click, and custom hotkeys such as:

```text
hotkey:ctrl,shift,s
```

## Project structure

```text
ASIS-adaptive-screen-interaction-sysytem-NEXUS/
├── README.md
└── files/
    ├── main.py             # Dashboard and OpenCV entry points
    ├── config.py           # Runtime thresholds and model settings
    ├── capture.py          # Threaded webcam capture
    ├── filters.py          # One Euro cursor smoothing
    ├── gestures.py         # Gesture recognition and state transitions
    ├── actions.py          # Cursor and operating-system actions
    ├── fusion.py           # Cursor history and voice/gesture alignment
    ├── liveness.py         # Face and voice liveness signals
    ├── voice.py            # Offline openWakeWord integration
    ├── recorder.py         # Custom gesture sample collection
    ├── trainer.py          # Feature extraction and model training
    ├── requirements.txt    # Python dependencies
    └── ui/dashboard.py     # PySide6 dashboard
```

## Troubleshooting

- **Camera does not open:** close other camera applications and try another
  `CAM_INDEX` in `files/config.py`.
- **Model download fails:** check internet access, then run NEXUS again after
  the connection is restored.
- **No cursor or mouse actions:** check OS accessibility/input permissions and
  ensure another application is not intercepting the device.
- **Wake-word detection fails:** verify the microphone is available and that
  the audio dependencies installed successfully. The hand gesture pipeline
  can still be used without voice input.
- **Custom gesture training fails:** record samples for at least one gesture
  before starting training; multiple gesture classes provide a more useful
  classifier.

## Development notes

NEXUS is an evolving project. The application currently focuses on local
desktop interaction and does not provide identity verification or guaranteed
anti-spoofing security. Liveness helpers are replay-resistance signals, not a
security boundary.

Contributions and issue reports are welcome through the
[GitHub repository](https://github.com/SaketharamaBana/ASIS-adaptive-screen-interaction-sysytem-NEXUS).
