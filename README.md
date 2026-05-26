# Coach-Interview-Assistant
# 🗣️ AI-Powered Oral Presentation & Interview Behavioral Analyzer

An advanced Computer Vision and Affective Computing tool designed to evaluate, score, and improve an individual's non-verbal communication skills during simulated oral examinations, public speaking events, and job interviews.

By creating a simulated video-call environment with a virtual interviewer, the system analyzes real-time webcam feeds to extract deep behavioral metrics, specifically focusing on **3D head pose estimation**, **postural stability (nervousness tracking)**, and **eye contact consistency**.

---

## 🚀 Key Features

* **High-Precision 3D Head Pose Estimation:** Extracts 6 stable 2D facial landmarks and maps them onto an anatomically calibrated 3D head model. Using geometric computer vision algorithms, it computes exact rotational degrees for **Pitch** (up/down), **Yaw** (left/right), and **Roll** (lateral tilt).
* **Biometric Nervousness & Tremor Analysis:** Implements a rolling-window FIFO (First-In, First-Out) data buffer to compute the temporal standard deviation ($\sigma$) of head movements. This detects micro-tremors, continuous posture shifting, and involuntary adjustments associated with anxiety.
* **Geometric Gaze Tracking (Gaze Ratio):** Measures horizontal eye movement by calculating the Euclidean distance between the center of the iris and the internal/external eye corners (canti). It objectively quantifies whether the user is maintaining direct eye contact with the display/interviewer or looking away.
* **Real-Time Statistical Overlay:** Features a low-latency graphical heads-up display (HUD) that maps performance states, numeric angles, and behavioral warnings directly onto the video stream.

---

## 🛠️ Tech Stack & Architecture

* **Python 3.14**
* **OpenCV:** Handles video capturing, geometric projections via perspective solvers, matrix transformations, and UI rendering.
* **MediaPipe:** Utilizes the cutting-edge `FaceLandmarker` pipeline to track 478 dense 3D facial landmarks in real time under variable lighting conditions.
* **NumPy:** Powers high-speed vector math, matrix definitions for camera intrinsics, and real-time statistical computations (standard deviation).
---

## 🧠 Architectural & Mathematical Foundations

### 1. 3D Head Pose Estimation (Perspective-n-Point)
To avoid the inaccuracies of standard 2D tracking, the tool solves the **Perspective-n-Point (PnP)** problem. It establishes a correspondence between a generic 3D facial model and the 2D projected pixels captured by the camera.
### 2. Postural Instability Metric
Nervousness is rarely defined by a static head angle; instead, it manifests as high-frequency posture adjustments.
### 3. Horizontal Gaze Ratio
To ensure robust eye contact verification that remains unaffected by rapid eye blinking, the tool calculates a horizontal ratio

---
## 🔮 Future Roadmap

* **Multimodal Integration:** Combine visual features with speech-to-text NLP models and audio pitch analytics to evaluate verbal fillers, speaking pace, and tone confidence.
* **Virtual Avatar Interface:** Integrate the analytics pipeline backend into a front-end rendering engine (e.g., Godot Engine) to drive an interactive virtual human assistant that responds dynamically to user eye contact.
* **Session Reporting:** Export data-driven timelines containing comprehensive performance scoring, engagement charts, and tailored behavioral tips post-interview.
