# Structured dictionary of suggestions for video analysis metrics
# The keys correspond to the names in cv_data_dict (union_face_hands.py)

SUGGESTIONS = {
    
    "eye_gaze_time": {
        "low": "Your gaze was so glued to the camera that it might come across as a bit rigid. Remember, it's completely natural to briefly look away while formulating a complex thought.",
        "high": "I noticed you tend to look away quite often. Try to maintain more consistent eye contact with the interviewer: it will help you convey greater confidence and engagement.",
        "optimal": "Great job with your eye contact! You kept your gaze attentive and natural, showing strong confidence and mastery of the topic without looking robotic."
    },
    
    "face_tremor_time": {
        "low": "Your face appeared completely still, almost frozen. Let a bit of naturalness shine through: a slight nod every now and then shows you're relaxed and actively listening.",
        "high": "Your face shows a bit of tension or repetitive movements. Before answering, take a deep breath to relax your neck muscles and keep your head steadier.",
        "optimal": "Perfect! You maintained a stable and relaxed expression throughout your answer, conveying a great sense of calm and clarity."
    },
    
    "head_movement_time": {
        "low": "You stayed in the exact same position the entire time, which can make you seem a bit tense. Don't be afraid to accompany your words with some slight, natural head movements.",
        "high": "Your head is moving a bit too frantically. Try to maintain a steadier frontal posture: this will keep you from looking distracted or unnecessarily agitated.",
        "optimal": "Very well done! Your head movements are natural and balanced. You smoothly accompany your words, appearing dynamic yet centered."
    },
    
    "head_down": {
        "low": "You never lowered your gaze, not even to reflect, which can sometimes give off a slightly overly proud posture. Try to be softer and more natural in your neck movements.",
        "high": "You tend to look down quite often. Even if you're thinking or reading notes, make an effort to keep your chin up: you'll immediately give an impression of greater readiness and confidence.",
        "optimal": "Excellent job keeping your head up just right! This simple detail immediately communicates that you are ready, proud, and open to dialogue."
    },
    
    "hand_general_time": {
        "low": "Your hands remained hidden or still for almost the entire time. Try using them to highlight the concepts you care about most: it will help you seem more energetic and passionate.",
        "high": "Your hands were moving non-stop throughout your answer. Remember to take pauses and rest them on the desk so you don't distract the listener from what you're saying.",
        "optimal": "You have excellent spatial awareness! You use your hands just right to give rhythm to your words, appearing expressive and energetic without ever overdoing it."
    },
    
    "face_touch_time": {
        "low": "Your movements were so minimal they almost seemed timid. When you want to emphasize a key point, don't be afraid to make a slightly broader gesture to strengthen the concept.",
        "high": "You tend to bring your hands up high near your face or chest too often. Try to keep your movements confined to desk-level: you'll appear much calmer and more in control.",
        "optimal": "Measured and professional gestures! You managed to use your available space elegantly, emphasizing concepts without any abrupt or exaggerated moves."
    },
    
    "face_overlap_time": {
        "low": "You didn't brush your face for even a millisecond. While this is positive, be careful not to look too focused on 'controlling' every single movement.",
        "high": "You brought your hands to your face several times. In an interview, this instinctive gesture can convey nervousness or defensiveness. Try keeping your hands clasped on your lap when you're thinking.",
        "optimal": "Congratulations! You avoided touching your face during stressful moments, maintaining an open, clean posture with no visual barriers between you and the interviewer."
    },
    
    "hand_gravity": {
        "low": "The overall score for your gestures is quite flat. Try 'warming up' your non-verbal communication to show more enthusiasm for the position you're applying for.",
        "high": "Your overall score indicates a bit of underlying agitation in your movements. A solid posture with a few purposeful gestures is the secret to conveying true leadership.",
        "optimal": "Textbook performance! Your body language communicates professionalism and tranquility in every single movement. You are entirely in command of your space."
    },
      
    "filler_words": {
        "high": "I noticed you're relying quite a bit on filler words. Try to pause silently instead of filling the gap with a word: it will make you sound much more confident.",
        "optimal": "Great job keeping filler words to a minimum! Your speech sounds natural and articulate, showing that you are in full control of your message."
    },

    "vocal_fillers": {
        "high": "You're using vocal fillers a bit too often. When you need a moment to think, just take a silent breath. A brief pause is much more powerful than a filler sound.",
        "optimal": "Excellent vocal clarity! You managed your thinking moments perfectly without relying on distracting sounds, making your answer sound very professional."
    },

    "micro_silences": {
        "high": "Your speech has a lot of very short pauses, making it sound a bit choppy or hesitant. Try to group your words into smoother, longer phrases to improve your flow.",
        "optimal": "Your pacing is spot on! You used micro-pauses perfectly to breathe and give rhythm to your sentences, resulting in a very smooth and engaging delivery."
    },

    "long_pauses": {
        "high": "There were some very long silences in your answer. If you need time to think, it's totally fine to say, 'That's a great question, let me think for a second,' to keep the connection alive.",
        "optimal": "Perfect timing! You avoided awkward silences but still took the right amount of time to deliver a well-thought-out and continuous response."
    },

    "tremor": {
        "high": "Your voice trembled a bit during your answer, which can easily happen when we feel nervous. Before speaking, try taking a deep breath from your diaphragm to support your voice and project confidence.",
        "optimal": "Your voice sounded incredibly steady and grounded! You projected calm and confidence, making your answer sound very authoritative and reassuring."
    }


}