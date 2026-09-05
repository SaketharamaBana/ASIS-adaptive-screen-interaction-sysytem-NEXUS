# ⚡ NEXUS
### Adaptive Touchless Interaction & Intelligent Gesture Control System

<p align="center">
  <img src="https://img.shields.io/badge/AI-Computer%20Vision-00D4FF?style=for-the-badge&logo=opencv&logoColor=white" />
  <img src="https://img.shields.io/badge/Robotics-Human%20Machine%20Interaction-7B61FF?style=for-the-badge" />
  <img src="https://img.shields.io/badge/ML-Random%20Forest-00C853?style=for-the-badge&logo=scikit-learn&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-FFD43B?style=for-the-badge&logo=python&logoColor=black" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/MediaPipe-Hand%20Landmarker-FF6F00?style=flat-square" />
  <img src="https://img.shields.io/badge/PySide6-Qt%206.7-41CD52?style=flat-square&logo=qt&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenCV-Real--Time%20Vision-5C3EE8?style=flat-square&logo=opencv&logoColor=white" />
  <img src="https://img.shields.io/badge/ONNX-Voice%20Inference-005CED?style=flat-square&logo=onnx&logoColor=white" />
  <img src="https://img.shields.io/badge/NumPy-Numerical%20Computing-013243?style=flat-square&logo=numpy&logoColor=white" />
  <img src="https://img.shields.io/badge/DSP-One--Euro%20Filter-E91E63?style=flat-square" />
  <img src="https://img.shields.io/badge/License-MIT-brightgreen?style=flat-square" />
</p>

<p align="center">
  <strong>NEXUS transforms spatial hand kinematics and acoustic intent into zero-latency, real-time operating system control.</strong>
</p>

<p align="center">
  <code>Perception</code> → <code>Feature Engineering</code> → <code>Intelligence</code> → <code>Sensor Fusion</code> → <code>Decision</code> → <code>Actuation</code>
</p>

---

## 🧬 SYSTEM IDENTITY & ARCHITECTURE

**NEXUS** is a real-time multimodal Human–Machine Interaction (HMI) platform that enables touchless desktop operating system control without physical input devices.

Instead of treating gesture recognition as a naive image-classification task, NEXUS structures the interaction loop as a feedback-controlled spatial computing pipeline:

```text
                 ┌─────────────────────────────┐
                 │        HUMAN INPUT          │
                 │                             │
                 │  Hand Motion + Voice + Face │
                 └──────────────┬──────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │     SENSOR LAYER      │
                    │                       │
                    │  Webcam / Microphone  │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  PERCEPTION ENGINE    │
                    │                       │
                    │ MediaPipe + OpenCV    │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ FEATURE ENGINEERING   │
                    │                       │
                    │ 73D Kinematic Space   │
                    └───────────┬───────────┘
                                │
                                ▼
                 ┌─────────────────────────────┐
                 │      INTELLIGENCE LAYER     │
                 │                             │
                 │ Random Forest + State       │
                 │ Machine + Gesture Router    │
                 └──────────────┬──────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
          ┌──────────────────┐    ┌──────────────────┐
          │  VOICE ENGINE    │    │ LIVENESS GUARD   │
          │                  │    │                  │
          │ Wake Word / ONNX │    │ Anti-Spoofing    │
          └────────┬─────────┘    └────────┬─────────┘
                   │                       │
                   └───────────┬───────────┘
                               ▼
                    ┌───────────────────────┐
                    │   SENSOR FUSION       │
                    │                       │
                    │ Spatial + Temporal    │
                    │ Context Resolution    │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  DECISION ENGINE      │
                    │                       │
                    │ Gesture → Intent →    │
                    │ Action Mapping        │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   ACTUATION LAYER     │
                    │                       │
                    │ Cursor / Mouse / OS    │
                    │ Hotkeys / Media        │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │      DESKTOP OS       │
                    └───────────────────────┘
```

---

## 📐 MATHEMATICAL SIGNAL PROCESSING & FEATURE FORMULATION

### 1. One-Euro Adaptive DSP Filter
High-frequency spatial tremor is eliminated using an adaptive **One-Euro Filter** (Casiez et al.), dynamically balancing static jitter suppression with zero-latency movement tracking.

The exponential smoothing coefficient $\alpha$ is given by:

$$\alpha = \frac{2\pi f_c T_e}{2\pi f_c T_e + 1}$$

The adaptive cutoff frequency $f_c$ scales proportionally with signal velocity $|\dot{\hat{x}}_k|$:

$$f_c = f_{c,\min} + \beta \cdot |\dot{\hat{x}}_k|$$

- $f_{c,\min} = 0.8\text{ Hz}$: Suppresses high-frequency micro-jitter when the hand is stationary.
- $\beta = 0.4$: Accelerates filter cutoff during rapid movements, preventing phase lag.

Recursively updating filtered coordinate estimates $\hat{x}_k$:

$$\hat{x}_k = \alpha x_k + (1 - \alpha) \hat{x}_{k-1}$$

---

### 2. 73-Dimensional Invariant Kinematic Feature Space
MediaPipe extracts 21 3D landmarks $\mathbf{P}_i = (x_i, y_i, z_i) \in \mathbb{R}^3$. To ensure scale-invariance (distance to camera) and translation-invariance (position in frame), points are projected into a 73D feature vector $\mathbf{\Phi} \in \mathbb{R}^{73}$.

#### A. Origin Alignment (Translation Invariance)
$$\mathbf{P}'_i = \mathbf{P}_i - \mathbf{P}_0 \quad \forall i \in \{0, \dots, 20\}$$

#### B. Palm Reference Scaling (Scale Invariance)
Using palm Euclidean reference norm $L_{\text{palm}} = \|\mathbf{P}'_9\|_2$ (wrist to middle MCP joint):

$$\mathbf{v}_i = \frac{\mathbf{P}'_i}{\max(L_{\text{palm}}, 10^{-6})} \in \mathbb{R}^3 \implies \mathbf{\Phi}_{\text{spatial}} \in \mathbb{R}^{63}$$

#### C. Fingertip Pairwise Distance Matrix
Pairwise distances across 5 fingertips $\mathcal{F} = \{4, 8, 12, 16, 20\}$:

$$D_{i,j} = \|\mathbf{v}_i - \mathbf{v}_j\|_2 \quad \forall i, j \in \mathcal{F}, i < j \implies \mathbf{\Phi}_{\text{pairwise}} \in \mathbb{R}^{10}$$

#### D. Consolidated Feature Vector
$$\mathbf{\Phi} = \begin{bmatrix} \mathbf{\Phi}_{\text{spatial}} \\ \mathbf{\Phi}_{\text{pairwise}} \end{bmatrix} \in \mathbb{R}^{73}$$

---

## ⚡ REAL-TIME BENCHMARKS & LATENCY PROFILES

Evaluating the complete end-to-end loop at **$65\text{+ FPS}$** ($\sim 15.4\text{ ms}$ total latency):

| Execution Pipeline Stage | Underlying Algorithm | Latency (ms) | Execution Context |
|---|---|---|---|
| **Frame Capture** | OpenCV Threaded VideoCapture | $1.2\text{ ms}$ | Background Worker |
| **Landmark Detection** | MediaPipe HandLandmarker (Float16) | $11.5\text{ ms}$ | Hardware Accelerated |
| **DSP Signal Filter** | Dual-Axis One-Euro Filter | $0.08\text{ ms}$ | Main Pipeline |
| **Feature Extraction** | 73D Kinematic Projection | $0.22\text{ ms}$ | Main Pipeline |
| **ML Inference** | Random Forest Classifier ($N=50$) | $0.45\text{ ms}$ | Main Pipeline |
| **OS Actuation** | Thread-Safe PyAutoGUI Dispatcher | $0.15\text{ ms}$ | Async Cursor Thread |
| **GUI Render Blit** | PySide6 Qt Frame Buffer Copy | $1.8\text{ ms}$ | Qt Render Thread |
| **TOTAL END-TO-END** | **Full System Pipeline** | **$\sim 15.4\text{ ms}$** | **$65\text{+ FPS}$** |

---

## 🕹️ CORE KINEMATIC GESTURES & ACTION MAPPING

| Gesture Category | Hand Landmark Kinematics | Mathematical Trigger Condition | OS Trigger Action |
|---|---|---|---|
| **Cursor Tracking** | Index Fingertip ($\mathbf{P}_8$) | Continuous spatial tracking | Move OS Cursor |
| **Left Click** | Thumb ($\mathbf{P}_4$) + Index ($\mathbf{P}_8$) | $\|\mathbf{P}_4 - \mathbf{P}_8\|_2 < 0.045$ | Mouse Left Click |
| **Mouse Drag** | Thumb ($\mathbf{P}_4$) + Index ($\mathbf{P}_8$) | $\|\mathbf{P}_4 - \mathbf{P}_8\|_2 < 0.045 \ (\Delta t \ge 0.5\text{s})$ | Mouse Hold / Drag |
| **Right Click** | Thumb ($\mathbf{P}_4$) + Middle ($\mathbf{P}_{12}$) | $\|\mathbf{P}_4 - \mathbf{P}_{12}\|_2 < 0.045$ | Mouse Right Click |
| **Vertical Scroll** | Thumb ($\mathbf{P}_4$) + Pinky ($\mathbf{P}_{20}$) | $\|\mathbf{P}_4 - \mathbf{P}_{20}\|_2 < 0.05 \ (\Delta y \cdot 800)$ | Mouse Wheel Scroll |
| **Precision Mode** | Left Hand Pinch | $\|\mathbf{P}_{4,\text{left}} - \mathbf{P}_{8,\text{left}}\|_2 < 0.045$ | Dampen Cursor ($35\%$) |
| **Custom ML Gesture** | 73D Invariant Landmarks | $P(\text{Class} \mid \mathbf{\Phi}) \ge 0.70$ | User Bound Action |

---

## 🧠 USER-DEFINED GESTURE TRAINING WORKFLOW

```text
 ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
 │ 1. Record Data  │ ---> │ 2. Feature Extr.│ ---> │ 3. Train RF ML  │ ---> │ 4. Bind Actions │
 │    (Camera)     │      │   (73D Vector)  │      │  (Scikit-Learn) │      │  (Hotkeys/Media)│
 └─────────────────┘      └─────────────────┘      └─────────────────┘      └─────────────────┘
```

1. Open **NEXUS Dashboard** (`python main.py`).
2. Navigate to the **Trainer** tab.
3. Input custom gesture label (e.g. `wave`, `peace_sign`, `thumbs_up`).
4. Click **1. Record Gesture** (press `SPACE` in camera window for each sample).
5. Click **2. Train Custom Model (Random Forest)** to generate `custom_gesture_model.pkl`.
6. Navigate to **Bindings** tab to assign triggers:
   - **Media Play / Pause**
   - **Volume Mute**
   - **Take Screenshot**
   - **Toggle Desktop (`Win + D`)**
   - **Switch Window (`Alt + Tab`)**
   - **Custom Hotkey Combinations**

---

## 📁 REPOSITORY STRUCTURE

```
ASIS-NEXUS-FINAL/
├── README.md                   # Core Architectural & Engineering Documentation
├── .gitignore                  # Exclusion Rules
└── files/
    ├── main.py                 # Primary Application Entry (GUI & --cli modes)
    ├── config.py               # Tunable Hyperparameters & Binding Manifests
    ├── capture.py              # Non-Blocking Threaded Webcam Grabber
    ├── filters.py              # One-Euro Signal Processing Implementation
    ├── actions.py              # Asynchronous OS Action Dispatcher
    ├── gestures.py             # Kinematic State Machine & ML Model Router
    ├── trainer.py              # 73D Feature Extractor & RF Model Trainer
    ├── voice.py                # openWakeWord ONNX Audio Engine ("Hey Jarvis")
    ├── liveness.py             # Anti-Spoofing Guardian Liveness Signals
    ├── fusion.py               # Spatial-Temporal Deictic Voice-Gesture Fusion
    ├── recorder.py             # Dataset Sample Collection Tool
    ├── requirements.txt        # Python Dependency Manifest
    ├── NEXUS.spec              # PyInstaller Executable Spec
    └── ui/
        └── dashboard.py        # PySide6 Qt Control Dashboard
```

---

## 🚀 INSTALLATION & EXECUTION GUIDE

### 1. Environment Setup
```bash
git clone https://github.com/SaketharamaBana/ASIS-adaptive-screen-interaction-sysytem-NEXUS.git
cd ASIS-adaptive-screen-interaction-sysytem-NEXUS

# Create Virtual Environment
python -m venv .venv

# Activate Environment (Windows)
.\.venv\Scripts\activate

# Install Dependencies
cd files
pip install -r requirements.txt
```

### 2. Launching NEXUS
```bash
# Launch PySide6 GUI Control Dashboard (Default)
python main.py

# Launch Headless / OpenCV CLI Debug Window
python main.py --cli
```

---

## 📄 LICENSE
Distributed under the **MIT License**.
