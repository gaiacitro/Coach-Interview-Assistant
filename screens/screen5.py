# screens/screen5.py
import customtkinter as ctk
from config import PRINCIPAL_COLOR, SECONDARY_COLOR

class Screen5(ctk.CTkScrollableFrame):
    def __init__(self, parent, controller, data=None):
        # 1. Il frame scorrevole prende di nuovo TUTTO lo schermo (così la barra di scorrimento va a destra)
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.pack(expand=True, fill="both")

        # =========================================================
        # 2. IL TRUCCO: Creiamo una colonna centrale invisibile!
        # Tkinter la piazzerà automaticamente al centro esatto dello schermo.
        # =========================================================
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.pack(pady=30, padx=20)

        # DA QUI IN POI: Attacchiamo tutto a "center_frame" invece che a "self"!

        # TITLE SECTION
        ctk.CTkLabel(center_frame, text="Interview Report", font=("Helvetica", 32, "bold"), text_color="black").pack(anchor="w", pady=(0, 20))

        if not data:
            data = [
                {
                    "question": "Tell me about yourself.",
                    "text": "well basically i am a student and uhm i like coding.",
                    "silence_count": 2,
                    "vocal_fillers": 1,
                    "vocal_fillers_dict": {"uhm": 1},
                    "filler_words": 2,
                    "filler_words_dict": {"basically": 1, "well": 1},
                    "tremor": 1.2,
                    # AGGIUNTA DEI DATI DELLA COMPUTER VISION:
                    "cv_data": {
                        "gaze_face": {
                            "eye_gaze_time": 2.5,
                            "face_tremor_time": 0.0,
                            "head_movement_time": 1.2
                        },
                        "hand_gesture": {
                            "hand_general_time": 5.4,
                            "face_touch_time": 0.0,
                            "face_overlap_time": 0.0
                        }
                    }
                },
                {
                    "question": "What is your greatest weakness?",
                    "text": "i think like my greatest weakness is basically public speaking.",
                    "silence_count": 1,
                    "vocal_fillers": 0,
                    "vocal_fillers_dict": {},
                    "filler_words": 2,
                    "filler_words_dict": {"like": 1, "basically": 1},
                    "tremor": 2.5,
                    # AGGIUNTA DEI DATI DELLA COMPUTER VISION:
                    "cv_data": {
                        "gaze_face": {
                            "eye_gaze_time": 4.1,
                            "face_tremor_time": 3.2,
                            "head_movement_time": 2.8
                        },
                        "hand_gesture": {
                            "hand_general_time": 2.1,
                            "face_touch_time": 1.5,
                            "face_overlap_time": 0.8
                        }
                    }
                }
            ]

        # =========================================================
        # 1. FIRST PART: QUESTION BY QUESTION REPORT
        # =========================================================
        ctk.CTkLabel(center_frame, text="Questions & Answers Analysis", font=("Helvetica", 22, "bold"), text_color=PRINCIPAL_COLOR).pack(anchor="w", pady=(10, 10))

        for idx, item in enumerate(data):
            card = ctk.CTkFrame(center_frame, fg_color="#F8F9FA", corner_radius=15, border_width=1, border_color="#E0E0E0")
            card.pack(fill="x", pady=10, ipady=10, ipadx=10)

            ctk.CTkLabel(card, text=f"Q{idx+1}: {item['question']}", font=("Helvetica", 16, "bold"), text_color="black", wraplength=850, justify="left").pack(anchor="w", padx=10, pady=(10, 5))
            
            ctk.CTkLabel(card, text=f"Your answer: \"{item['text']}\"", font=("Helvetica", 14, "italic"), text_color="#555555", wraplength=850, justify="left").pack(anchor="w", padx=10, pady=(0, 5))

            ctk.CTkButton(card, text="Reformulate", font=("Helvetica", 13, "bold"), 
                          fg_color=PRINCIPAL_COLOR, text_color="black", hover_color=SECONDARY_COLOR, 
                          width=100, height=30, corner_radius=8,
                          command=lambda q=idx: print(f"Reformulating question {q+1}...")).pack(anchor="w", padx=10, pady=(0, 15))

            speech_frame = ctk.CTkFrame(card, fg_color="transparent")
            speech_frame.pack(fill="x", padx=10, pady=5)
            
            v_count = item.get('vocal_fillers', 0)
            v_dict = item.get('vocal_fillers_dict', {})
            if v_count > 0:
                v_details = "\n".join([f"    - {word} [{count}]" for word, count in v_dict.items()])
                v_string = f"{v_count}\n{v_details}"
            else:
                v_string = "0"

            f_count = item.get('filler_words', 0)
            f_dict = item.get('filler_words_dict', {})
            if f_count > 0:
                f_details = "\n".join([f"    - {word} [{count}]" for word, count in f_dict.items()])
                f_string = f"{f_count}\n{f_details}"
            else:
                f_string = "0"

            ctk.CTkLabel(speech_frame, text="🎤 Speech Analysis:", font=("Helvetica", 14, "bold"), text_color="black").grid(row=0, column=0, sticky="w", pady=2)
            ctk.CTkLabel(speech_frame, text=f"Long Pauses: {item.get('silence_count', 0)}", font=("Helvetica", 13), text_color="black").grid(row=1, column=0, sticky="w", padx=(20,0))
            
            ctk.CTkLabel(speech_frame, text=f"Vocal Fillers: {v_string}", font=("Helvetica", 13), text_color="black", justify="left").grid(row=2, column=0, sticky="w", padx=(20,0), pady=2)
            ctk.CTkLabel(speech_frame, text=f"Filler Words: {f_string}", font=("Helvetica", 13), text_color="black", justify="left").grid(row=3, column=0, sticky="w", padx=(20,0), pady=2)
            
            ctk.CTkLabel(speech_frame, text=f"Voice Tremor: {item.get('tremor', 0)} / 100", font=("Helvetica", 13), text_color="black").grid(row=4, column=0, sticky="w", padx=(20,0), pady=(5,0))

            # Recupero i dati della CV per questa domanda (o dizionari vuoti se non ci sono)
            cv_data = item.get("cv_data", {})
            cv_face = cv_data.get("gaze_face", {})
            cv_hand = cv_data.get("hand_gesture", {})

            # ==========================================
            # 👁️ GAZE AND FACE ANALYSIS
            # ==========================================
            face_frame = ctk.CTkFrame(card, fg_color="transparent")
            face_frame.pack(fill="x", padx=10, pady=(10, 5))
            
            ctk.CTkLabel(face_frame, text="👁️ Gaze and Face Analysis:", font=("Helvetica", 14, "bold"), text_color="black").grid(row=0, column=0, sticky="w", pady=2)
            
            ctk.CTkLabel(face_frame, text=f"Eyes Distracted Time: {cv_face.get('eye_gaze_time', 0.0):.1f}s", font=("Helvetica", 13), text_color="black").grid(row=1, column=0, sticky="w", padx=(20,0))
            ctk.CTkLabel(face_frame, text=f"Face Tremor/Tension Time: {cv_face.get('face_tremor_time', 0.0):.1f}s", font=("Helvetica", 13), text_color="black").grid(row=2, column=0, sticky="w", padx=(20,0))
            ctk.CTkLabel(face_frame, text=f"Head Moved/Turned Time: {cv_face.get('head_movement_time', 0.0):.1f}s", font=("Helvetica", 13), text_color="black").grid(row=3, column=0, sticky="w", padx=(20,0))

            # ==========================================
            # 🖐️ HAND AND GESTURE ANALYSIS
            # ==========================================
            hand_frame = ctk.CTkFrame(card, fg_color="transparent")
            hand_frame.pack(fill="x", padx=10, pady=(5, 10))
            
            ctk.CTkLabel(hand_frame, text="🖐️ Hand and Gesture Analysis:", font=("Helvetica", 14, "bold"), text_color="black").grid(row=0, column=0, sticky="w", pady=2)
            
            ctk.CTkLabel(hand_frame, text=f"Gesticulation Time: {cv_hand.get('hand_general_time', 0.0):.1f}s", font=("Helvetica", 13), text_color="black").grid(row=1, column=0, sticky="w", padx=(20,0))
            ctk.CTkLabel(hand_frame, text=f"Hands Above Chin Time: {cv_hand.get('face_touch_time', 0.0):.1f}s", font=("Helvetica", 13), text_color="black").grid(row=2, column=0, sticky="w", padx=(20,0))
            ctk.CTkLabel(hand_frame, text=f"Face Overlap Time (Box): {cv_hand.get('face_overlap_time', 0.0):.1f}s", font=("Helvetica", 13), text_color="black").grid(row=3, column=0, sticky="w", padx=(20,0))

        # =========================================================
        # 2. SECOND PART: OVERALL FEEDBACK AND SCORE
        # =========================================================
        ctk.CTkLabel(center_frame, text="Overall Feedback", font=("Helvetica", 22, "bold"), text_color=PRINCIPAL_COLOR).pack(anchor="w", pady=(30, 5))
        
        feedback_frame = ctk.CTkFrame(center_frame, fg_color="#F8F9FA", corner_radius=15, border_width=2, border_color="#CCCCCC")
        feedback_frame.pack(fill="x", pady=5, ipady=15, ipadx=15)

        final_score_value = 75 
        
        if final_score_value > 66:
            score_color = "#4CAF50" 
        elif final_score_value >= 33:
            score_color = "#FF9800" 
        else:
            score_color = "#F44336" 

        score_container = ctk.CTkFrame(feedback_frame, fg_color="transparent")
        score_container.pack(anchor="w", padx=20, pady=(10, 15))

        ctk.CTkLabel(score_container, text="Final Score: ", font=("Helvetica", 18, "bold"), text_color="black").pack(side="left")
        
        ctk.CTkLabel(score_container, text=f" {final_score_value} / 100 ", font=("Helvetica", 18, "bold"), 
                     fg_color=score_color, text_color="white", corner_radius=8).pack(side="left", padx=10)

        ctk.CTkLabel(feedback_frame, text="Questions to Review:", font=("Helvetica", 16, "bold"), text_color="black").pack(anchor="w", padx=20)
        
        ctk.CTkLabel(feedback_frame, text="• Q2: What is your greatest weakness? (High voice tremor detected)\n• Q4: Where do you see yourself in 5 years? (Too many filler words)", 
                     font=("Helvetica", 14), text_color="black", justify="left", wraplength=850).pack(anchor="w", padx=30, pady=(5, 15))

        ctk.CTkLabel(feedback_frame, text="Suggestions:", font=("Helvetica", 16, "bold"), text_color="black").pack(anchor="w", padx=20)
        
        ctk.CTkLabel(feedback_frame, text="🟢 Positive: Your gaze was very steady and you maintained good eye contact.\n🟢 Positive: You didn't touch your face and used hand gestures effectively to explain yourself.\n🔴 Negative: Your voice trembled significantly during some answers, try taking deep breaths.\n🔴 Negative: Try to reduce filler words like 'basically' and 'like'.", 
                     font=("Helvetica", 14), text_color="black", justify="left", wraplength=850).pack(anchor="w", padx=30, pady=(5, 10))


        # =========================================================
        # DOWNLOAD BUTTON
        # =========================================================
        ctk.CTkButton(center_frame, text="Download Report", font=("Helvetica", 16, "bold"), 
                      fg_color=PRINCIPAL_COLOR, text_color="black", hover_color=SECONDARY_COLOR, 
                      height=50, corner_radius=10,
                      command=lambda: print("Avvio generazione PDF del report...")).pack(pady=(40, 50))