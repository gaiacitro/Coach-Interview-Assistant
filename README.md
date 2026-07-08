# Coach-Interview-Assistant
# 🗣️ AI-Powered Interview Behavioral Analyzer
Coach-Interview-Assistant is an innovative, Al-powered desktop application designed to elevate professional and academic interview training by evaluating candidate performance through multimodal behavioral analysis. The application is designed to replace subjective interview preparation with real-time, data-driven behavioral analysis, democratizing access to elite, evidence-based interview coaching without the steep financial or hardware barriers of advanced VR tools

---

## 🚀 Key Features

* * **Multimodal Behavioral Analysis:**  Integrates Computer Vision and Natural Language Processing to extract real-time spatial, temporal, and acoustic metrics.
  * **Visual Tracking:** Monitors visual metrics like gaze stability, head kinematics (nodding, shaking), and gesture dynamics, including spontaneous facial self-touches and excessive upper-body gesticulation.
  * **Acoustic & Speech Evaluation:** Tracks acoustic signals such as vocal tremor (local jitter), speech fluency, micro-silences, long pauses, vocal fillers ("uhm", "er"), filler words ("basically", "like"), and Words Per Minute (WPM).
  * **Generative AI Coaching:** Features a "Reformulate" option that utilizes an LLM to fix grammatical errors and eliminate vocal stutters, providing actionable linguistic coaching without altering the candidate's personal communication style.
  * **Detailed Feedback Dashboard:** Generates a comprehensive results dashboard detailing performance for each individual question, utilizing a color-coded dot system (Green, Yellow, Red) and dynamic, targeted suggestions.
    
---

## 🛠️ Tech Stack & Architecture

The system architecture relies on a carefully selected technology stack to ensure robust tracking, low-latency processing, and seamless integration:
* **Python 3.10**
* **Computer Vision & Landmark Tracking:** MediaPipe, OpenCV, NumPy.
* **Audio & Speech Processing:** Faster-Whisper, Parselmouth / Praat, pydub.
* **Generative AI & Decision Logic:** Google Gemini LLM API (gemini-2.5-flash).
* **GUI & Frontend Management:** CustomTkinter, pywebview, HTML/JS.

---

## 🧠 How It Works

### 1. Data Acquisition
The application continuously captures video and audio in real-time during the simulated interview.
### 2. Multimodal Extraction
The media streams are processed asynchronously across three independent pipelines (Visual, Linguistic, and Acoustic) to extract raw behavioral metrics like gaze, speech pauses, and spoken text.
### 3. Normalization & Classification
Raw metrics are mathematically normalized (e.g., converted to rates per minute) and evaluated against scientifically backed thresholds to assign immediate color-coded feedback (Green, Yellow, or Red dots).
### 4. Final Evaluation
The system synthesizes these discrete parameters into weighted Gravity Scores, which are ultimately translated into a standard 0-100 Perfection Score to provide the user with a clear, classical grade.

---

## 🧑‍💻 User Experience
  * **Context Setup**: Users can configure their session by selecting either a professional job interview or a university oral exam environment.
  * **Immersive Simulation**: The simulation leverages an embedded HTML/JS web view to render an Al avatar that guides the session using a dual-state video system (speaking and listening).
  * **Final Report**: Candidates can view their Final Score out of 100, read categorized lists of positive reinforcements and constructive critiques, and download their complete analytical breakdown as a standard .txt report for offline review.

---

## 🔮 Future Roadmap

* **Micro-Expression Analysis:** Expand the Computer Vision pipeline to detect and analyze subtle facial micro-expressions during speech delivery.
* **Full-Body Posture Tracking:** Integrate full-body pose estimation to evaluate overall upper-body posture, sitting balance, and spinal alignment.
* **Semantic & Sentiment Analysis:** Utilize Large Language Models (LLMs) beyond structural text cleanup to perform real-time sentiment analysis, scoring the relevance, confidence, and persuasive power of the candidate's actual content.
* **Historical Progress Analytics:** Implement multi-session tracking dashboards to visualize performance trends and improvement metrics over time.
