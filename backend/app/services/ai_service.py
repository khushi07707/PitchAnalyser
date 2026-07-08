import os
import logging
from typing import Dict, Any, List
from openai import OpenAI
from app.config.config import settings
from app.core.exceptions import ProcessingException

logger = logging.getLogger(__name__)

class AIService:
    @staticmethod
    def transcribe_audio(filepath: str) -> Dict[str, Any]:
        """
        Transcribe audio using OpenAI Whisper API.
        Falls back to local mock transcript if API key is not configured or fails.
        """
        if settings.OPENAI_API_KEY:
            try:
                logger.info(f"Sending {filepath} to OpenAI Whisper API...")
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                
                with open(filepath, "rb") as audio_file:
                    # Request full metadata with word & segment timestamps
                    response = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="verbose_json",
                        timestamp_granularities=["word", "segment"]
                    )
                
                # Standardize model fields
                text = getattr(response, "text", "")
                language = getattr(response, "language", "english")
                
                words = []
                raw_words = getattr(response, "words", [])
                if raw_words:
                    for w in raw_words:
                        if isinstance(w, dict):
                            words.append({"word": w.get("word"), "start": w.get("start"), "end": w.get("end")})
                        else:
                            words.append({"word": getattr(w, "word", ""), "start": getattr(w, "start", 0.0), "end": getattr(w, "end", 0.0)})
                
                segments = []
                raw_segments = getattr(response, "segments", [])
                if raw_segments:
                    for s in raw_segments:
                        if isinstance(s, dict):
                            segments.append({"text": s.get("text"), "start": s.get("start"), "end": s.get("end")})
                        else:
                            segments.append({"text": getattr(s, "text", ""), "start": getattr(s, "start", 0.0), "end": getattr(s, "end", 0.0)})
                
                # If words were not returned, split segment text heuristically
                if not words and segments:
                    words = AIService._generate_heuristic_word_timestamps(segments)
                
                logger.info(f"Whisper transcript generated successfully. Character length: {len(text)}")
                return {
                    "full_text": text,
                    "language": language,
                    "words": words,
                    "sentences": segments
                }
            except Exception as e:
                logger.error(f"OpenAI Whisper transcribing failed: {str(e)}. Falling back to local mock transcript.", exc_info=True)
        else:
            logger.info("OpenAI API Key not configured. Using local mock transcript.")
            
        return AIService._get_fallback_transcript()

    @staticmethod
    def generate_ai_feedback(transcript: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate feedback (strengths, weaknesses, suggestions) using OpenAI GPT.
        Falls back to rules-based local feedback if API key is not configured or fails.
        """
        if settings.OPENAI_API_KEY:
            try:
                logger.info("Generating AI feedback via OpenAI GPT...")
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                
                prompt = f"""
                You are a senior pitch coach and venture capitalist evaluator.
                Analyse the following pitch transcript and voice metrics, then generate a detailed evaluation.
                
                Pitch Transcript:
                "{transcript}"
                
                Voice Metrics:
                - Speaking Rate: {metrics.get('speaking_rate')} Words Per Minute
                - Pitch Mean: {metrics.get('pitch_mean')} Hz
                - Pitch Stability (Standard Deviation): {metrics.get('pitch_stability')} Hz
                - Voice Energy (RMS): {metrics.get('energy')}
                - Pauses Count: {metrics.get('pauses_count')}
                - Silence Duration: {metrics.get('silence_duration')} seconds
                - Voice Modulation Score: {metrics.get('voice_modulation')}
                - Sentiment Score (Polarity): {metrics.get('sentiment_polarity')}
                - Sentiment Subjectivity: {metrics.get('sentiment_subjectivity')}
                - Style: {metrics.get('speaking_style')}
                
                Respond ONLY with a JSON object containing the following keys (do not include markdown wrapping like ```json):
                {{
                    "strengths": ["list of 3 key strengths"],
                    "weaknesses": ["list of 3 key weaknesses"],
                    "suggestions": ["list of 3 actionable suggestions"],
                    "overall_review": "a detailed overview paragraph evaluating their delivery",
                    "presentation_tips": ["2 presentation tips"],
                    "communication_tips": ["2 communication tips"],
                    "confidence_tips": ["2 tips for boosting speaking confidence"]
                }}
                """
                
                chat_completion = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a professional business pitch evaluator."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                
                import json
                raw_response = chat_completion.choices[0].message.content or ""
                # Clean markdown blocks if LLM ignored instructions
                if raw_response.startswith("```"):
                    raw_response = raw_response.strip().strip("```").strip("json").strip()
                
                feedback_data = json.loads(raw_response)
                logger.info("AI feedback successfully generated via OpenAI GPT.")
                return feedback_data
            except Exception as e:
                logger.error(f"OpenAI GPT feedback generation failed: {str(e)}. Falling back to local feedback engine.")
        
        return AIService._get_fallback_feedback(metrics)

    @staticmethod
    def _generate_heuristic_word_timestamps(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Heuristic word splitter for segments if word-level data is missing."""
        words = []
        for seg in segments:
            seg_text = seg.get("text", "")
            seg_start = seg.get("start", 0.0)
            seg_end = seg.get("end", 0.0)
            
            words_in_seg = seg_text.strip().split()
            if not words_in_seg:
                continue
            
            duration = seg_end - seg_start
            word_duration = duration / len(words_in_seg)
            
            for idx, w in enumerate(words_in_seg):
                w_clean = w.strip(".,?!;:()\"'")
                if not w_clean:
                    continue
                words.append({
                    "word": w_clean,
                    "start": round(seg_start + (idx * word_duration), 2),
                    "end": round(seg_start + ((idx + 1) * word_duration), 2)
                })
        return words

    @staticmethod
    def _get_fallback_transcript() -> Dict[str, Any]:
        """Provides a highly realistic mock transcript for speech analytics demo."""
        text = "Hello everyone. Today, I am super excited to pitch NovaTech Solutions. We address a critical, critical pain point in small business financial management. That is, the complete inability to accurately forecast cash flows and make real-time financial decisions. Um, you know, our AI-powered platform integrates with standard accounting tools and banking APIs. It provides automated forecasting, anomaly detection, and actionable CFO recommendations. We believe, actually, that we can help founders save over fifteen hours a week, and avoid costly cash shortfalls. Thank you so much for your time."
        
        # Word items list
        raw_words = text.split()
        words = []
        current_time = 0.5
        for idx, w in enumerate(raw_words):
            word_len = len(w)
            duration = max(0.2, min(0.6, word_len * 0.07))
            words.append({
                "word": w.strip(".,?!;:()\"'").lower(),
                "start": round(current_time, 2),
                "end": round(current_time + duration, 2)
            })
            current_time += duration + 0.05
            # Simulate natural pauses
            if w.endswith(".") or w.endswith(","):
                current_time += 0.4
            elif w.lower() in ["um", "uh", "you", "know"]:
                current_time += 0.2
        
        # Sentences list
        sentences = [
            {"text": "Hello everyone.", "start": 0.5, "end": 1.6},
            {"text": "Today, I am super excited to pitch NovaTech Solutions.", "start": 2.0, "end": 5.8},
            {"text": "We address a critical, critical pain point in small business financial management.", "start": 6.2, "end": 11.5},
            {"text": "That is, the complete inability to accurately forecast cash flows and make real-time financial decisions.", "start": 12.0, "end": 19.5},
            {"text": "Um, you know, our AI-powered platform integrates with standard accounting tools and banking APIs.", "start": 20.0, "end": 26.8},
            {"text": "It provides automated forecasting, anomaly detection, and actionable CFO recommendations.", "start": 27.2, "end": 33.5},
            {"text": "We believe, actually, that we can help founders save over fifteen hours a week, and avoid costly cash shortfalls.", "start": 34.0, "end": 42.0},
            {"text": "Thank you so much for your time.", "start": 42.5, "end": 45.0}
        ]
        
        return {
            "full_text": text,
            "language": "english",
            "words": words,
            "sentences": sentences
        }

    @staticmethod
    def _get_fallback_feedback(metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Provides heuristic/rules-based feedback based on the computed librosa/NLP metrics."""
        wpm = metrics.get("speaking_rate", 140)
        pauses = metrics.get("pauses_count", 5)
        mod = metrics.get("voice_modulation", 0.5)
        polarity = metrics.get("sentiment_polarity", 0.1)
        
        strengths = ["Strong and clear introduction to the business problem."]
        weaknesses = []
        suggestions = []
        
        # WPM assessment
        if wpm < 110:
            weaknesses.append("Speaking rate is a bit slow (under 110 WPM), which could lead to listener disengagement.")
            suggestions.append("Increase your delivery pace to around 130-150 WPM to maintain energy and urgency.")
        elif wpm > 170:
            weaknesses.append("Delivery speed is very fast (over 170 WPM), making it hard to follow complex points.")
            suggestions.append("Deliberately slow down when discussing key financials or your value proposition.")
            strengths.append("High enthusiasm and prompt pacing keeps the delivery energetic.")
        else:
            strengths.append(f"Ideal speaking pace of {int(wpm)} WPM, which is very easy for investors to follow.")
        
        # Pauses assessment
        if pauses < 3:
            weaknesses.append("Lack of natural pauses in speech transitions.")
            suggestions.append("Add 1-2 second pauses after key slides to let major statements sink in.")
        else:
            strengths.append("Good usage of natural pauses to structure logical arguments.")
            
        # Voice Modulation assessment
        if mod < 0.35:
            weaknesses.append("Flat voice modulation, making the pitch sound monotone.")
            suggestions.append("Vary your vocal pitch and volume when transitioning from the 'problem' to your 'solution'.")
        else:
            strengths.append("Dynamic vocal modulation with expressive transitions.")
            
        # Sentiment assessment
        if polarity < 0.05:
            weaknesses.append("The tone feels overly analytical and lacks optimistic energy.")
            suggestions.append("Use positive adjective markers ('revolutionary', 'exceptional') to frame achievements.")
        else:
            strengths.append("Expressive, positive tone that builds enthusiasm.")
            
        # Fill list to exactly 3 items
        while len(strengths) < 3:
            strengths.append("Clear syntax and solid grammatical flow throughout.")
        while len(weaknesses) < 3:
            weaknesses.append("Slight reliance on filler phrases during structural transitions.")
        while len(suggestions) < 3:
            suggestions.append("Practice matching hand gestures to vocal emphasizes to reinforce points.")
            
        return {
            "strengths": strengths[:3],
            "weaknesses": weaknesses[:3],
            "suggestions": suggestions[:3],
            "overall_review": "The pitch demonstrates a structured articulation of value. The core problem statement was clearly emphasized. The delivery was natural, though practicing vocal control on technical statistics will make the explanation even more compelling.",
            "presentation_tips": [
                "Keep slides simple: use high-contrast text and a maximum of 4 bullet points per page.",
                "Maintain virtual eye contact by looking directly at the camera rather than the screen."
            ],
            "communication_tips": [
                "Structure your answers using the STAR method (Situation, Task, Action, Result) during potential Q&A.",
                "Vary your vocabulary: avoid repeating adjectives like 'critical' or 'huge' within the same section."
            ],
            "confidence_tips": [
                "Take a deep, slow diaphragmatic breath before starting to lower your resting pitch.",
                "Speak with conviction: phrase statements as definitive declarations rather than questions."
            ]
        }
