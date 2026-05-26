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
* **OpenCV (`cv2`):** Handles video capturing, geometric projections via perspective solvers, matrix transformations, and UI rendering.
* **MediaPipe (`tasks.python.vision`):** Utilizes the cutting-edge `FaceLandmarker` pipeline to track 478 dense 3D facial landmarks in real time under variable lighting conditions.
* **NumPy:** Powers high-speed vector math, matrix definitions for camera intrinsics, and real-time statistical computations (standard deviation).
* ---

## 🧠 Architectural & Mathematical Foundations

### 1. 3D Head Pose Estimation (Perspective-n-Point)
To avoid the inaccuracies of standard 2D tracking, the tool solves the **Perspective-n-Point (PnP)** problem. It establishes a correspondence between a generic 3D facial model and the 2D projected pixels captured by the camera using the following camera intrinsic matrix ($K$):

$$K =  egin{bmatrix} f_x & 0 & c_x \ 0 & f_y & c_y \ 0 & 0 & 1 \end{bmatrix}$$

Where $f_x, f_y$ represent the camera's focal length (approximated from frame width), and $c_x, c_y$ represent the optical center of the image frame. The resulting rotation vector ($ ec{r}$) is transformed via Rodrigues' rotation formula into a $3 	imes 3$ rotation matrix ($R$) and decomposed into standard Euler angles:
* **Pitch ($	heta_x$):** Indicates looking up (often correlated with cognitive abstract thinking/recalling memory) or looking down.
* **Yaw ($	heta_y$):** Indicates horizontal turning (looking away from the interviewer).
* **Roll ($	heta_z$):** Indicates lateral head tilt.

### 2. Postural Instability Metric
Nervousness is rarely defined by a static head angle; instead, it manifests as high-frequency posture adjustments. The system monitors a temporal window $W$ of size $N=30$ frames (~1 second of video):

$$\sigma_{yaw} = \sqrt{rac{1}{N} \sum_{i=1}^{N} (y_i -  ar{y})^2}$$

If $\sigma_{yaw}$ or $\sigma_{pitch}$ exceeds a strictly calibrated threshold ($	au = 2.5^{\circ}$), the user's posture state shifts from **"Stable (Confidence)"** to **"Instabile (Tension)"**.

### 3. Horizontal Gaze Ratio
To ensure robust eye contact verification that remains unaffected by rapid eye blinking, the tool calculates a horizontal ratio based on three anchor landmarks: **Outer Corner (33)**, **Inner Corner (133)**, and **Iris Center (468)**.

$$	ext{Gaze Ratio} = rac{\lVert P_{	ext{Iris}} - P_{	ext{Inner Corner}} 
Vert}{\lVert P_{	ext{Outer Corner}} - P_{	ext{Iris}} 
Vert}$$

* **Direct Eye Contact:** $	ext{Gaze Ratio}  pprox 1.0$ (Iris perfectly centered).
* **Left / Right Deviation:** $	ext{Gaze Ratio} < 0.6$ or $> 1.4$.

---
## 🔮 Future Roadmap

* **Multimodal Integration:** Combine visual features with speech-to-text NLP models and audio pitch analytics to evaluate verbal fillers, speaking pace, and tone confidence.
* **Virtual Avatar Interface:** Integrate the analytics pipeline backend into a front-end rendering engine (e.g., Godot Engine) to drive an interactive virtual human assistant that responds dynamically to user eye contact.
* **Session Reporting:** Export data-driven timelines containing comprehensive performance scoring, engagement charts, and tailored behavioral tips post-interview.
