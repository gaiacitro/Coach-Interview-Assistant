# screens/screen5.py
import customtkinter as ctk
from config import PRINCIPAL_COLOR, SECONDARY_COLOR

class Screen5(ctk.CTkScrollableFrame):
    def __init__(self, parent, controller, data=None):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Expand the scrollable frame to fill the screen
        self.pack(expand=True, fill="both", padx=30, pady=30)

        # TITLE SECTION
        ctk.CTkLabel(self, text="Interview Report", font=("Helvetica", 32, "bold"), text_color="black").pack(anchor="w", pady=(0, 20))

        # ---------------------------------------------------------
        # MOCK DATA FOR TESTING GRAPHICS
        # If 'data' is empty (i.e., we are just testing the screen), use these:
        # ---------------------------------------------------------
        if not data:
            data = [
                {
                    "question": "Tell me about yourself.",
                    "text": "well basically i am a student and uhm i like coding.",
                    "silence_count": 2,
                    "vocal_fillers": 1,
                    "filler_words": 2,
                    "tremor": 1.2
                },
                {
                    "question": "What is your greatest weakness?",
                    "text": "i think like my greatest weakness is basically public speaking.",
                    "silence_count": 1,
                    "vocal_fillers": 0,
                    "filler_words": 2,
                    "tremor": 2.5
                }
            ]

        # =========================================================
        # 1. FIRST PART: QUESTION BY QUESTION REPORT
        # =========================================================
        ctk.CTkLabel(self, text="Questions & Answers Analysis", font=("Helvetica", 22, "bold"), text_color=PRINCIPAL_COLOR).pack(anchor="w", pady=(10, 10))

        for idx, item in enumerate(data):
            # Create a "Card" for each question, light gray to stand out from the white background
            card = ctk.CTkFrame(self, fg_color="#F8F9FA", corner_radius=15, border_width=1, border_color="#E0E0E0")
            card.pack(fill="x", pady=10, ipady=10, ipadx=10)

            # Question
            ctk.CTkLabel(card, text=f"Q{idx+1}: {item['question']}", font=("Helvetica", 16, "bold"), text_color="black", wraplength=550, justify="left").pack(anchor="w", padx=10, pady=(10, 5))
            
            # User's answer
            ctk.CTkLabel(card, text=f"Your answer: \"{item['text']}\"", font=("Helvetica", 14, "italic"), text_color="#555555", wraplength=550, justify="left").pack(anchor="w", padx=10, pady=(0, 10))

            # --- AI Data: Speech ---
            speech_frame = ctk.CTkFrame(card, fg_color="transparent")
            speech_frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(speech_frame, text="🎤 Speech Analysis:", font=("Helvetica", 14, "bold"), text_color="black").grid(row=0, column=0, sticky="w", pady=2)
            ctk.CTkLabel(speech_frame, text=f"Long Pauses: {item.get('silence_count', 0)}", font=("Helvetica", 13), text_color="black").grid(row=1, column=0, sticky="w", padx=(20,0))
            ctk.CTkLabel(speech_frame, text=f"Vocal Fillers (uhm, er): {item.get('vocal_fillers', 0)}", font=("Helvetica", 13), text_color="black").grid(row=2, column=0, sticky="w", padx=(20,0))
            ctk.CTkLabel(speech_frame, text=f"Filler Words (like, so): {item.get('filler_words', 0)}", font=("Helvetica", 13), text_color="black").grid(row=3, column=0, sticky="w", padx=(20,0))
            ctk.CTkLabel(speech_frame, text=f"Voice Tremor (Jitter): {item.get('tremor', 0.0):.2f}%", font=("Helvetica", 13), text_color="black").grid(row=4, column=0, sticky="w", padx=(20,0))

            # --- AI Data: Computer Vision (Face and Hands) - PLACEHOLDER ---
            cv_frame = ctk.CTkFrame(card, fg_color="transparent")
            cv_frame.pack(fill="x", padx=10, pady=(10, 5))
            
            ctk.CTkLabel(cv_frame, text="👁️ Computer Vision Analysis:", font=("Helvetica", 14, "bold"), text_color="black").grid(row=0, column=0, sticky="w", pady=2)
            ctk.CTkLabel(cv_frame, text="[Face Tracking data will go here]", font=("Helvetica", 13), text_color="gray").grid(row=1, column=0, sticky="w", padx=(20,0))
            ctk.CTkLabel(cv_frame, text="[Hand Tracking data will go here]", font=("Helvetica", 13), text_color="gray").grid(row=2, column=0, sticky="w", padx=(20,0))

            # Reformulate Button (Bottom right of the card)
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(fill="x", padx=10, pady=(10, 0))
            
            ctk.CTkButton(btn_frame, text="Reformulate", font=("Helvetica", 14, "bold"), 
                          fg_color=PRINCIPAL_COLOR, text_color="black", hover_color=SECONDARY_COLOR, 
                          width=120, height=35, corner_radius=8,
                          command=lambda q=idx: print(f"Reformulating question {q+1}...")).pack(side="right")


        # =========================================================
        # 2. SECOND PART: OVERALL FEEDBACK AND SCORE
        # =========================================================
        ctk.CTkLabel(self, text="Overall Feedback", font=("Helvetica", 22, "bold"), text_color=PRINCIPAL_COLOR).pack(anchor="w", pady=(30, 10))
        
        feedback_frame = ctk.CTkFrame(self, fg_color="#F8F9FA", corner_radius=15, border_width=1, border_color="#E0E0E0")
        feedback_frame.pack(fill="x", pady=5, ipady=15, ipadx=15)

        # 2.A Final Score
        ctk.CTkLabel(feedback_frame, text="Final Score: [INSERT FINAL SCORE LOGIC HERE]", 
                     font=("Helvetica", 18, "bold"), text_color="black").pack(anchor="w", pady=(0, 15))

        # 2.B Questions to review
        ctk.CTkLabel(feedback_frame, text="Questions to Review:", font=("Helvetica", 16, "bold"), text_color="black").pack(anchor="w")
        ctk.CTkLabel(feedback_frame, text="• Q2: What is your greatest weakness? (High voice tremor detected)\n• Q4: Where do you see yourself in 5 years? (Too many filler words)", 
                     font=("Helvetica", 14), text_color="black", justify="left").pack(anchor="w", padx=20, pady=(5, 15))

        # 2.C Suggestions
        ctk.CTkLabel(feedback_frame, text="Suggestions:", font=("Helvetica", 16, "bold"), text_color="black").pack(anchor="w")
        ctk.CTkLabel(feedback_frame, text="🟢 Positive: Your gaze was very steady and you maintained good eye contact.\n🟢 Positive: You didn't touch your face and used hand gestures effectively to explain yourself.\n🔴 Negative: Your voice trembled significantly during some answers, try taking deep breaths.\n🔴 Negative: Try to reduce filler words like 'basically' and 'like'.", 
                     font=("Helvetica", 14), text_color="black", justify="left").pack(anchor="w", padx=20, pady=(5, 0))


        # =========================================================
        # BACK TO HOME BUTTON
        # =========================================================
        ctk.CTkButton(self, text="Back to Home", font=("Helvetica", 16, "bold"), 
                      fg_color="black", text_color="white", hover_color="#333333", 
                      height=50, corner_radius=10,
                      command=lambda: self.controller.show_screen("Screen1")).pack(pady=(40, 20))