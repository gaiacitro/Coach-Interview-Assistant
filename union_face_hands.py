import cv2
import os
import time
import math
import threading
import urllib.request
import numpy as np
from collections import deque
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # hides TensorFlow warnings
os.environ['GLOG_minloglevel'] = '2'      # hide MediaPipe logs

class UnifiedVisionTracker:
    def __init__(self):
        # Init model paths
        self.hand_model_path = "hand_landmarker.task"
        self.face_model_path = "face_landmarker.task"
        self._check_models()
        
        base_options_hand = python.BaseOptions(model_asset_path=self.hand_model_path)
        base_options_face = python.BaseOptions(model_asset_path=self.face_model_path)

        self.hand_detector = vision.HandLandmarker.create_from_options(
            vision.HandLandmarkerOptions(
                base_options=base_options_hand, running_mode=vision.RunningMode.VIDEO, num_hands=2,
                min_hand_detection_confidence=0.5, min_hand_presence_confidence=0.5, min_tracking_confidence=0.5
            )
        )

        self.face_detector = vision.FaceLandmarker.create_from_options(
            vision.FaceLandmarkerOptions(
                base_options=base_options_face, running_mode=vision.RunningMode.VIDEO,
                output_face_blendshapes=False, output_facial_transformation_matrixes=False, num_faces=1,
                min_face_detection_confidence=0.5, min_face_presence_confidence=0.5, min_tracking_confidence=0.5
            )
        )
        
        # 3D face model for PnP algorithm
        self.face_3d_model = np.array([
            (0.0, 0.0, 0.0),            
            (0.0, -330.0, -65.0),       
            (-225.0, 170.0, -135.0),    
            (225.0, 170.0, -135.0),     
            (-150.0, -150.0, -125.0),   
            (150.0, -150.0, -125.0)     
        ], dtype=np.float64)
        
        self.running = False
        self.thread = None
        
        self.pitch_history = deque(maxlen=30)
        self.yaw_history = deque(maxlen=30)
        self.roll_history = deque(maxlen=30)

        self.calibrating = True
        self.calibration_duration = 3.0
        self.calibration_start_time = 0
        self.pitch_sum = 0
        self.yaw_sum = 0
        self.roll_sum = 0
        self.calibration_frames = 0
        self.baseline_pitch = 0
        self.baseline_yaw = 0
        self.baseline_roll = 0

        # Time trackers
        self.total_time_answer = 0.0 
        self.hand_general_time = 0.0
        self.hands_above_chin_time = 0.0
        self.box_overlap_time = 0.0
        self.eyes_turned_time = 0.0
        self.face_instability_time = 0.0
        self.head_moved_time = 0.0 
        self.head_down_time = 0.0

    def _check_models(self):
        if not os.path.exists(self.hand_model_path):
            urllib.request.urlretrieve("https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task", self.hand_model_path)
        if not os.path.exists(self.face_model_path):
            urllib.request.urlretrieve("https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task", self.face_model_path)

    def _detection_loop(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.running = False
            return

        prev_time = time.time()

        while self.running:
            success, frame = cap.read()
            if not success:
                continue
            
            current_time = time.time()
            delta_time = current_time - prev_time
            prev_time = current_time
            
            self.total_time_answer += delta_time

            frame = cv2.flip(frame, 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h_frame, w_frame, _ = frame.shape

            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            timestamp_ms = int(time.time() * 1000)
            
            hand_results = self.hand_detector.detect_for_video(mp_image, timestamp_ms)
            face_results = self.face_detector.detect_for_video(mp_image, timestamp_ms)

            if hand_results.hand_landmarks:
                self.hand_general_time += delta_time

            chin_y = None
            face_box_area = None
            min_hand_y = float('inf')
            box_touch_detected = False

            if face_results.face_landmarks:
                face_landmarks = face_results.face_landmarks[0]
                chin_y = int(face_landmarks[152].y * h_frame)
                
                xs = [int(lm.x * w_frame) for lm in face_landmarks]
                ys = [int(lm.y * h_frame) for lm in face_landmarks]
                min_x, max_x = min(xs), max(xs)
                face_width = max_x - min_x
                ear_margin = int(face_width * 0.15)
                face_box_area = (max(0, min_x - ear_margin), min(ys), min(w_frame, max_x + ear_margin), max(ys))

                p_outer = (int(face_landmarks[33].x * w_frame), int(face_landmarks[33].y * h_frame))
                p_inner = (int(face_landmarks[133].x * w_frame), int(face_landmarks[133].y * h_frame))
                p_iris = (int(face_landmarks[468].x * w_frame), int(face_landmarks[468].y * h_frame))
                
                dist_center_inner = math.hypot(p_iris[0] - p_inner[0], p_iris[1] - p_inner[1])
                dist_outer_center = math.hypot(p_outer[0] - p_iris[0], p_outer[1] - p_iris[1])
                if dist_outer_center == 0: dist_outer_center = 0.01
                
                gaze_ratio = dist_center_inner / dist_outer_center
                if gaze_ratio < 0.6 or gaze_ratio > 1.4:
                    self.eyes_turned_time += delta_time

                # PnP and Euler angles calculation
                indices = [1, 152, 33, 263, 61, 291]
                face_2d = np.array([[int(face_landmarks[idx].x * w_frame), int(face_landmarks[idx].y * h_frame)] for idx in indices], dtype=np.float64)
                
                focal_length = w_frame
                cam_matrix = np.array([[focal_length, 0, w_frame / 2], [0, focal_length, h_frame / 2], [0, 0, 1]])
                dist_matrix = np.zeros((4, 1), dtype=np.float64)
                
                success_pnp, rot_vec, _ = cv2.solvePnP(self.face_3d_model, face_2d, cam_matrix, dist_matrix)
                if success_pnp:
                    rmat, _ = cv2.Rodrigues(rot_vec)
                    angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
                    raw_pitch, raw_yaw, raw_roll = angles[0], angles[1], angles[2]

                    if raw_roll < -90: raw_roll += 180
                    elif raw_roll > 90: raw_roll -= 180
                    if raw_pitch < -90: raw_pitch += 180
                    elif raw_pitch > 90: raw_pitch -= 180

                    elapsed_time = time.time() - self.calibration_start_time
                    if self.calibrating:
                        if elapsed_time < self.calibration_duration:
                            if elapsed_time >= (self.calibration_duration - 1.0):
                                self.pitch_sum += raw_pitch
                                self.yaw_sum += raw_yaw
                                self.roll_sum += raw_roll
                                self.calibration_frames += 1
                        else:
                            if self.calibration_frames > 0:
                                self.baseline_pitch = self.pitch_sum / self.calibration_frames
                                self.baseline_yaw = self.yaw_sum / self.calibration_frames
                                self.baseline_roll = self.roll_sum / self.calibration_frames
                            self.calibrating = False
                    else:
                        pitch = raw_pitch - self.baseline_pitch
                        yaw = raw_yaw - self.baseline_yaw
                        roll = raw_roll - self.baseline_roll

                        self.pitch_history.append(pitch)
                        self.yaw_history.append(yaw)
                        self.roll_history.append(roll)

                        if len(self.yaw_history) == 30:
                            if np.std(self.yaw_history) > 15 or np.std(self.pitch_history) > 15:
                                self.face_instability_time += delta_time

                        head_state = "Frontal"
                        if pitch > 13: 
                            head_state = "Looking Down"
                        elif pitch > 7: 
                            if yaw > 30 or roll < -20:
                                head_state = "Looking Down"
                            elif yaw < -30 or roll > 20:
                                head_state = "Looking Down"
                        elif pitch < -18:
                            head_state = "Looking Up"
                        elif yaw > 30 or roll < -20:
                            head_state = "Looking Left"
                        elif yaw < -30 or roll > 20:
                            head_state = "Looking Right"

                        if head_state != "Frontal":
                            self.head_moved_time += delta_time

                        if head_state == "Looking Down":
                            self.head_down_time += delta_time

            # Hand controls
            if hand_results.hand_landmarks:
                for hand_landmarks in hand_results.hand_landmarks:
                    for lm in hand_landmarks:
                        cx, cy = int(lm.x * w_frame), int(lm.y * h_frame)
                        if cy < min_hand_y: min_hand_y = cy
                        if face_box_area and not box_touch_detected:
                            if face_box_area[0] <= cx <= face_box_area[2] and face_box_area[1] <= cy <= face_box_area[3]:
                                box_touch_detected = True

                if chin_y is not None and min_hand_y < chin_y:
                    self.hands_above_chin_time += delta_time
                
                if box_touch_detected:
                    self.box_overlap_time += delta_time

        cap.release()

    def start(self):
        # Reset trackers
        self.hand_general_time = 0.0
        self.hands_above_chin_time = 0.0
        self.box_overlap_time = 0.0
        self.eyes_turned_time = 0.0
        self.face_instability_time = 0.0
        self.head_moved_time = 0.0 
        self.total_time_answer = 0.0 
        self.head_down_time = 0.0
        
        self.pitch_sum = 0
        self.yaw_sum = 0
        self.roll_sum = 0
        self.calibration_frames = 0
        self.pitch_history.clear()
        self.yaw_history.clear()
        self.roll_history.clear()
        
        self.calibrating = True
        self.calibration_start_time = time.time()
        
        self.running = True
        self.thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        
        # Package CV data (Solo dati grezzi, niente formule qui!)
        cv_data_dict = {
            "gaze_face": {
                "total_time_answer": self.total_time_answer,
                "eye_gaze_time": self.eyes_turned_time,
                "face_tremor_time": self.face_instability_time,
                "head_movement_time": self.head_moved_time,
                "head_down": self.head_down_time
            },
            "hand_gesture": {
                "total_time_answer": self.total_time_answer,
                "hand_general_time": self.hand_general_time,
                "hands_above_chin_time": self.hands_above_chin_time, # Aggiunto per poter fare il calcolo in score.py
                "face_touch_time": max(0, self.hands_above_chin_time - self.box_overlap_time),
                "face_overlap_time": self.box_overlap_time
            }
        }
        return cv_data_dict

