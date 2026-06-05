# screens/screen5.py
import customtkinter as ctk
from utils import (
    generate_report_text,
    DEFAULT_INTERVIEW_DATA,
    add_dot,
    generate_suggestions,
    get_questions_to_review
)  
from tkinter import filedialog
from score import speech_performance_evaluation, cv_performance_evaluation, calculate_perfection_score
from config import (
    CARD_BG, 
    CARD_BORDER, 
    TEXT_MAIN,
    TEXT_SUB,
    BTN_BG, 
    BTN_TEXT, 
    BTN_HOVER,
    APP_FONT
)
import threading
from ai_helper import get_reformulated_text 

def get_threshold_segments(canvas_w, canvas_h, thresholds):
    """
    Generates segments of a colored bar based on percentage thresholds.
    Returns a list of (x_start, x_end, color)
    """
    min_red, min_yellow, max_yellow, max_red = thresholds
    red_color = "#F44336"
    orange_color = "#FF9800"
    green_color = "#4CAF50"
    
    segments = []
    
    # converts percentage thresholds to pixel positions on the canvas
    def pct_to_px(pct):
        return (pct / 100.0) * canvas_w
    
    threshold_points = [0, min_red, min_yellow, max_yellow, max_red, 100]
    threshold_colors = [red_color, orange_color, green_color, orange_color, red_color]
    
    for i in range(len(threshold_points) - 1):
        x_start = pct_to_px(threshold_points[i])
        x_end = pct_to_px(threshold_points[i + 1])
        color = threshold_colors[i]
        
        if x_end > x_start: # only add segment if it has a positive width
            segments.append((x_start, x_end, color))
    
    return segments

class Screen5(ctk.CTkScrollableFrame):
    def __init__(self, parent, controller, data=None):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        self.pack(expand=True, fill="both") 
        
        # font initialization
        big_title_font = ctk.CTkFont(family=APP_FONT, size=34, weight="bold")
        section_title_font = ctk.CTkFont(family=APP_FONT, size=24, weight="bold")
        question_font = ctk.CTkFont(family=APP_FONT, size=18, weight="bold")
        answer_font = ctk.CTkFont(family=APP_FONT, size=15, slant="italic")
        box_title_font = ctk.CTkFont(family=APP_FONT, size=16, weight="bold")
        regular_font = ctk.CTkFont(family=APP_FONT, size=14)
        buttons_font = ctk.CTkFont(family=APP_FONT, size=16, weight="bold")

        # internal container frame with card style
        center_frame = ctk.CTkFrame(self, 
                                    fg_color=CARD_BG, 
                                    border_color=CARD_BORDER, 
                                    border_width=5, 
                                    corner_radius=20)
        center_frame.pack(pady=40, padx=40, ipadx=40, ipady=40, expand=True, fill="both")

        # title section
        ctk.CTkLabel(center_frame, text="Interview Report", font=big_title_font, text_color=TEXT_MAIN).pack(anchor="center", pady=(40, 40))

        # if no data is passed, use the default mock data for demonstration
        if not data:
            data = DEFAULT_INTERVIEW_DATA

        ## first part: question by question analysis with reformulated answer and CV data
        ctk.CTkLabel(center_frame, text="Questions & Answers Analysis", font=section_title_font, text_color=TEXT_SUB).pack(anchor="w", pady=(10, 20), padx=20)

        all_question_scores = []  #list to track the scores for each question

        for idx, item in enumerate(data):
            card = ctk.CTkFrame(center_frame, fg_color="white", corner_radius=15, border_width=2, border_color="#E8ECE8")
            card.pack(fill="x", pady=15, padx=20, ipady=15, ipadx=15)

            ctk.CTkLabel(card, text=f"Q{idx+1}: {item['question']}", font=question_font, text_color=TEXT_MAIN, wraplength=850, justify="left").pack(anchor="w", padx=10, pady=(10, 5))
            
            ctk.CTkLabel(card, text=f"Your answer: \"{item['text']}\"", font=answer_font, text_color="#555555", wraplength=850, justify="left").pack(anchor="w", padx=10, pady=(0, 5))
            
            cv_data = item.get("cv_data", {})
            cv_face = cv_data.get("gaze_face", {})
            response_time = cv_face.get("total_time_answer", 0.0)            
            ctk.CTkLabel(card, text=f"Response time: {response_time:.1f} sec", font=regular_font, text_color="#888888").pack(anchor="w", padx=10, pady=(0, 5))

           #empty space for the reformulated answer to be inserted later
            rephrased_label = ctk.CTkLabel(card, text="", font=answer_font, text_color=TEXT_MAIN, wraplength=850, justify="left")
            rephrased_label.pack(anchor="w", padx=10, pady=(0, 10))

            #buttons for reformulation 
            btn_reformulate = ctk.CTkButton(card, text="Reformulate", font=buttons_font, 
                                          fg_color=BTN_BG, text_color=BTN_TEXT, hover_color=BTN_HOVER, 
                                          width=140, height=35, corner_radius=10)
            
            # Let's connect the button by passing the text, the new label, and the button itself
            btn_reformulate.configure(command=lambda t=item['text'], lbl=rephrased_label, btn=btn_reformulate: self.handle_reformulate_click(t, lbl, btn))
            btn_reformulate.pack(anchor="w", padx=10, pady=(0, 20))

            stats_container = ctk.CTkFrame(card, fg_color="transparent")
            stats_container.pack(fill="x", padx=10, pady=5)
            canvas_w = 320
            canvas_h = 16

            v_count = item.get('vocal_fillers', 0)
            v_dict = item.get('vocal_fillers_dict', {})
            v_string = f"{v_count}\n" + "\n".join([f"    - {w} [{c}]" for w, c in v_dict.items()]) if v_count > 0 else "0" ###### si può togliere?

            f_count = item.get('filler_words', 0)
            f_dict = item.get('filler_words_dict', {})
            f_string = f"{f_count}\n" + "\n".join([f"    - {w} [{c}]" for w, c in f_dict.items()]) if f_count > 0 else "0" ###### si può togliere?

            cv_data = item.get("cv_data", {})
            cv_face = cv_data.get("gaze_face", {})
            cv_hand = cv_data.get("hand_gesture", {})

            # ---- speech frame ----
            speech_frame = ctk.CTkFrame(stats_container, fg_color="#F3F6F3", corner_radius=20)
            speech_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10, ipadx=15, ipady=15)
            
            ctk.CTkLabel(speech_frame, text="🎤 Speech Analysis", font=box_title_font, text_color=TEXT_SUB).pack(anchor="center", pady=(20, 15))
            
            # Qui riceviamo TUTTI i dati da score.py, compreso il risultato finale!
            report_speech = speech_performance_evaluation(item)

            val_long = report_speech.get("long_pauses", {})
            val_micro = report_speech.get("micro_silences", {})
            val_vocal = report_speech.get("vocal_fillers", {})
            val_filler = report_speech.get("filler_words", {})
            val_tremor = report_speech.get("tremor", {})

            # statistics with colored dots
            add_dot(speech_frame, f"Long Pauses: {val_long.get('real_value', 0)}", val_long)
            add_dot(speech_frame, f"Micro Silences: {val_micro.get('real_value', 0)}", val_micro)
            add_dot(speech_frame, f"Vocal Fillers: {val_vocal.get('real_value', 0)}", val_vocal)
            add_dot(speech_frame, f"Filler Words: {val_filler.get('real_value', 0)}", val_filler)
            add_dot(speech_frame, f"Voice Tremor: {val_tremor.get('real_value', 0):.0f} / 100", val_tremor)

            # total speech gravity
            ctk.CTkLabel(speech_frame, text="TOTAL SPEECH GRAVITY", font=box_title_font, text_color="#333333").pack(anchor="center", pady=(15, 5))
            
            speech_percent = int(max(0, report_speech.get("speech_gravity", 0.0)))

            # customized colored bar
            bar_canvas_s = ctk.CTkCanvas(speech_frame, width=canvas_w, height=canvas_h + 10, bg="#F3F6F3", highlightthickness=0)
            bar_canvas_s.pack(anchor="center", pady=(0, 0))

            # thresholds for speech_gravity
            speech_gravity_thresholds = (5.0, 30.0, 60.0, 85.0)
            segments_s = get_threshold_segments(canvas_w, canvas_h, speech_gravity_thresholds)
            
            bar_canvas_s.create_arc(0, 0, canvas_h, canvas_h, start=90, extent=180, fill=segments_s[0][2], outline=segments_s[0][2])
            bar_canvas_s.create_arc(canvas_w - canvas_h, 0, canvas_w, canvas_h, start=-90, extent=180, fill=segments_s[-1][2], outline=segments_s[-1][2])
            
            for x_start, x_end, color in segments_s:
                adjusted_start = max(x_start, canvas_h / 2)
                adjusted_end = min(x_end, canvas_w - canvas_h / 2)
                if adjusted_end > adjusted_start:
                    bar_canvas_s.create_rectangle(adjusted_start, 0, adjusted_end, canvas_h, fill=color, outline=color)

            # black marker line
            marker_x_s = (speech_percent / 100) * canvas_w
            bar_canvas_s.create_line(marker_x_s, -2, marker_x_s, canvas_h + 10, fill="black", width=4)

            # percentage number below the bar
            ctk.CTkLabel(speech_frame, text=f"{speech_percent}%", font=box_title_font, text_color="black").pack(anchor="center", pady=(0, 5))
            
            
            # ---- gaze/face frame ----
            face_frame = ctk.CTkFrame(stats_container, fg_color="#F3F6F3", corner_radius=20)
            face_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10, ipadx=15, ipady=15)
            cv_data = item.get("cv_data", {})
            
            report_cv = cv_performance_evaluation(cv_data)
            
            val_eyes = report_cv.get("eye_gaze", {})
            val_head = report_cv.get("head_movement", {})
            val_down = report_cv.get("head_down", {})
            
            val_gest = report_cv.get("hand_general", {})
            val_touch = report_cv.get("face_touch", {})
            val_overlap = report_cv.get("face_overlap", {})
            val_tremor = report_cv.get("face_tremor", {})

            # title
            ctk.CTkLabel(face_frame, text="👁️ Gaze Analysis", font=box_title_font, text_color=TEXT_SUB).pack(anchor="center", pady=(20, 15))

            add_dot(face_frame, f"Eyes Distracted: {cv_face.get('eye_gaze_time', 0.0):.1f}s", val_eyes)
            add_dot(face_frame, f"Head Turn: {cv_face.get('head_movement_time', 0.0):.1f}s", val_head)
            add_dot(face_frame, f"Head Down: {cv_face.get('head_down', 0.0):.1f}s", val_down)
            add_dot(face_frame, f"Nodding: {cv_face.get('face_tremor_time', 0.0):.1f}s", val_tremor)

            # total gaze gravity 
            ctk.CTkLabel(face_frame, text="TOTAL GAZE GRAVITY", font=box_title_font, text_color="#333333").pack(anchor="center", pady=(15, 5))

            gaze_percent = int(report_cv.get('head_total', 0.0))
            gaze_percent_clamped = max(0, min(100, gaze_percent)) # Limita tra 0 e 100 per non far uscire la lineetta dal disegno
            
            # customized colored bar
            canvas_w = 320
            canvas_h = 16
            bar_canvas = ctk.CTkCanvas(face_frame, width=canvas_w, height=canvas_h + 10, bg="#F3F6F3", highlightthickness=0)
            bar_canvas.pack(anchor="center", pady=(0, 0))

            # thresholds for head_total: (5.0, 25.0, 60.0, 85.0)
            head_total_thresholds = (5.0, 25.0, 60.0, 85.0)
            segments = get_threshold_segments(canvas_w, canvas_h, head_total_thresholds)
            
            bar_canvas.create_arc(0, 0, canvas_h, canvas_h, start=90, extent=180, fill=segments[0][2], outline=segments[0][2])
            bar_canvas.create_arc(canvas_w - canvas_h, 0, canvas_w, canvas_h, start=-90, extent=180, fill=segments[-1][2], outline=segments[-1][2])
            
            # draw segments with adjusted margins for the rounded arcs
            for x_start, x_end, color in segments:
                adjusted_start = max(x_start, canvas_h / 2)
                adjusted_end = min(x_end, canvas_w - canvas_h / 2)
                
                if adjusted_end > adjusted_start:
                    bar_canvas.create_rectangle(adjusted_start, 0, adjusted_end, canvas_h, fill=color, outline=color)

            # black marker line
            marker_x = (gaze_percent_clamped / 100) * canvas_w
            bar_canvas.create_line(marker_x, -2, marker_x, canvas_h + 10, fill="black", width=4)

            # percentage number below the bar
            ctk.CTkLabel(face_frame, text=f"{gaze_percent}%", font=box_title_font, text_color="black").pack(anchor="center", pady=(0, 5))
            
            
            # ---- hand frame ----
            hand_frame = ctk.CTkFrame(stats_container, fg_color="#F3F6F3", corner_radius=20)
            hand_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10, ipadx=15, ipady=15)
            
            # title
            ctk.CTkLabel(hand_frame, text="🖐️ Gesture Analysis", font=box_title_font, text_color=TEXT_SUB).pack(anchor="center", pady=(20, 15))
            
            # principal statistics with colored dots
            add_dot(hand_frame, f"Gesticulation: {cv_hand.get('hand_general_time', 0.0):.1f}s", val_gest)
            add_dot(hand_frame, f"Big gestures: {cv_hand.get('face_touch_time', 0.0):.1f}s", val_touch)
            add_dot(hand_frame, f"Touching Face: {cv_hand.get('face_overlap_time', 0.0):.1f}s", val_overlap)
            
            # total hand gesture gravity
            ctk.CTkLabel(hand_frame, text="TOTAL GESTURE GRAVITY", font=box_title_font, text_color="#333333").pack(anchor="center", pady=(15, 5))

            hand_percent = int(report_cv.get('hand_gravity', 0.0))
            hand_percent_clamped = max(0, min(100, hand_percent))
            
            # colored bar with thresholds for hand_gravity
            bar_canvas_h = ctk.CTkCanvas(hand_frame, width=canvas_w, height=canvas_h + 10, bg="#F3F6F3", highlightthickness=0)
            bar_canvas_h.pack(anchor="center", pady=(0, 0))
            
            # thresholds for hand_gravity: (5.0, 35.0, 55.0, 80.0)
            hand_gravity_thresholds = (5.0, 35.0, 55.0, 80.0)
            segments_h = get_threshold_segments(canvas_w, canvas_h, hand_gravity_thresholds)
            
            # draw rounded arcs at the two ends
            bar_canvas_h.create_arc(0, 0, canvas_h, canvas_h, start=90, extent=180, fill=segments_h[0][2], outline=segments_h[0][2])
            bar_canvas_h.create_arc(canvas_w - canvas_h, 0, canvas_w, canvas_h, start=-90, extent=180, fill=segments_h[-1][2], outline=segments_h[-1][2])
            
            # draw segments with adjusted margins for the rounded arcs
            for x_start, x_end, color in segments_h:
                # adjust margins for the rounded arcs
                adjusted_start = max(x_start, canvas_h / 2)
                adjusted_end = min(x_end, canvas_w - canvas_h / 2)
                
                if adjusted_end > adjusted_start:
                    bar_canvas_h.create_rectangle(adjusted_start, 0, adjusted_end, canvas_h, fill=color, outline=color)

            # black marker line
            marker_x_h = (hand_percent_clamped / 100) * canvas_w
            bar_canvas_h.create_line(marker_x_h, -2, marker_x_h, canvas_h + 10, fill="black", width=4)

            # percentage number below the bar
            ctk.CTkLabel(hand_frame, text=f"{hand_percent}%", font=box_title_font, text_color="black").pack(anchor="center", pady=(0, 5))
            
            q_score_frame = ctk.CTkFrame(card, fg_color="transparent")
            q_score_frame.pack(pady=(15, 10), anchor="center")
            
            ctk.CTkLabel(q_score_frame, text="Score: ", font=box_title_font, text_color="#333333").pack(side="left")
            
            # --- conversion to perfection score (0-100) ---
            perf_speech = calculate_perfection_score(speech_percent, speech_gravity_thresholds)
            perf_gaze = calculate_perfection_score(gaze_percent_clamped, head_total_thresholds)
            perf_hand = calculate_perfection_score(hand_percent_clamped, hand_gravity_thresholds)
            
            # Now we calculate the average of the perfection scores (0 -> total failure, 100 -> absolute perfection)
            score_value = int((perf_speech + perf_gaze + perf_hand) / 3.0) 
            
            all_question_scores.append(score_value)
            all_question_scores.append(score_value)  

            if score_value > 66:
                score_color = "#12BA4B"
            elif score_value >= 33:
                score_color = "#FF9800" 
            else:
                score_color = "#F44336"

            ctk.CTkLabel(q_score_frame, text=f" {score_value} / 100 ", font=question_font, 
                         fg_color=score_color, text_color="white", corner_radius=8, width=80, height=30).pack(side="left", padx=5)
            
            
        ## second part: overall feedback and suggestions
        ctk.CTkLabel(center_frame, text="Overall Feedback", font=section_title_font, text_color=TEXT_SUB).pack(anchor="w", pady=(40, 10), padx=20)
        
        feedback_frame = ctk.CTkFrame(center_frame, fg_color="white", corner_radius=15, border_width=2, border_color="#E8ECE8")
        feedback_frame.pack(fill="x", padx=20, pady=5, ipady=20, ipadx=20)

        # Calculate the final score as the average of all the question scores
        final_score_value = int(sum(all_question_scores) / len(all_question_scores)) if all_question_scores else 0 
        
        if final_score_value > 66:
            score_color = "#12BA4B" 
        elif final_score_value >= 33:
            score_color = "#FF9800" 
        else:
            score_color = "#F44336" 

        score_container = ctk.CTkFrame(feedback_frame, fg_color="transparent")
        score_container.pack(anchor="w", padx=10, pady=(20, 20))

        ctk.CTkLabel(score_container, text="Final Score: ", font=box_title_font, text_color="#333333").pack(side="left")
        
        ctk.CTkLabel(score_container, text=f" {final_score_value} / 100 ", font=question_font, 
                     fg_color=score_color, text_color="white", corner_radius=8, width=100, height=35).pack(side="left", padx=10)

        ctk.CTkLabel(feedback_frame, text="Questions to Review:", font=box_title_font, text_color=TEXT_SUB).pack(anchor="w", padx=10)
        
        review_text = get_questions_to_review(data)

        ctk.CTkLabel(feedback_frame, text=review_text, 
                     font=regular_font, text_color="#333333", justify="left", wraplength=850).pack(anchor="w", padx=20, pady=(5, 20))
        
        ctk.CTkLabel(feedback_frame, text="Suggestions:", font=box_title_font, text_color=TEXT_SUB).pack(anchor="w", padx=10)
        
        suggestions_list = generate_suggestions(data)
        
        if suggestions_list:
            for suggestion_text, color in suggestions_list:
                
                sugg_row = ctk.CTkFrame(feedback_frame, fg_color="transparent")
                sugg_row.pack(anchor="w", padx=20, pady=2)
                
                
                pallino_symbol = "●"
                ctk.CTkLabel(sugg_row, text=f"{pallino_symbol} ", font=regular_font, text_color=color).pack(side="left")
                
                # Testo suggestion
                ctk.CTkLabel(sugg_row, text=suggestion_text, font=regular_font, text_color="#333333", wraplength=800, justify="left").pack(side="left", fill="both", expand=True)
        else:
            
            ctk.CTkLabel(feedback_frame, text="No specific suggestions at this time.", 
                         font=regular_font, text_color="#888888").pack(anchor="w", padx=20, pady=5)

        ## download report button
        
        ctk.CTkButton(center_frame, text="Download Report", font=buttons_font, 
                      fg_color=TEXT_MAIN, text_color="white", hover_color=TEXT_SUB, 
                      width=250, height=55, corner_radius=15,
                      command=lambda: self.export_report(data, final_score_value)).pack(pady=(50, 20))


    def export_report(self, data, final_score):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt"), ("All files", "*.*")],
            title="Save Interview Report",
            initialfile="Interview_Report.txt"
        )
        
        if not file_path:
            return
        report_text = generate_report_text(data, final_score)
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(report_text)
        except Exception as e:
            print(f"error during report download: {e}") 

    def handle_reformulate_click(self, original_text, rephrased_label_widget, button_widget):
        button_widget.configure(state="disabled", text="Thinking...", text_color="gray")

        def background_task():
            rephrased_text = get_reformulated_text(original_text)
            if rephrased_text:
                # if successful, update the label with the reformulated text and change the button state
                self.after(0, lambda: rephrased_label_widget.configure(
                    text=f"✨ Suggested: \"{rephrased_text}\""
                ))
                # disable the button and change its text to indicate success
                self.after(0, lambda: button_widget.configure(text="Reformulated!", fg_color="#E0E0E0", state="disabled"))
            else:
                # if there was an error, re-enable the button and show an error message
                self.after(0, lambda: button_widget.configure(state="normal", text="Error. Try again", text_color="red"))

        # activate the background task in a separate thread to avoid freezing the UI
        threading.Thread(target=background_task, daemon=True).start()