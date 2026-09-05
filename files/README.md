# NEXUS — Touchless Gesture Control (Core Build)

Webcam-based cursor and click control with smoothing and multiple gestures,
built as clean, separated modules instead of one script.

## Structure
```
nexus/
  config.py     - all tunable settings in one place
  filters.py    - One-Euro smoothing filter
  capture.py    - threaded webcam capture
  actions.py    - ActionDispatcher (cursor move, click, scroll, drag, zoom)
  gestures.py   - landmark -> gesture recognition + state machine
  main.py       - wires everything together, run this
```

## Setup
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
The hand tracking model downloads automatically on first run (~10MB).

## Gestures
| Gesture | Action |
|---|---|
| Move index finger | Move cursor |
| Pinch thumb+index (quick) | Left click |
| Pinch thumb+index (hold) | Drag |
| Pinch thumb+middle | Right click |
| Pinch thumb+pinky + move hand up/down | Scroll |

## Controls
- `q` — quit
- `c` — reset smoothing/gesture state (use if cursor jumps after hand leaves frame)

## Tuning
All thresholds and sensitivities live in `config.py` — no need to touch
the logic files to adjust feel.

## Known limitations
- Single hand only.
- Fixed gesture set (no custom/trainable gestures yet).
- No voice, no plugins, no multi-user profiles, no packaging.
- Debug OpenCV window only — no polished UI yet.

## Guardian Mode security scope
The liveness primitives in `liveness.py` are local convenience and
anti-tampering signals for a future face/voice profile system. They use short
face motion, blink, and audio-variation checks to raise the bar against casual
static-photo or silent-replay attacks. They are not OS authentication,
encryption, or enterprise security, and they are not defeat-proof against a
determined attacker with sophisticated presentation or replay tools.

These are natural next steps if you want to keep extending it.
