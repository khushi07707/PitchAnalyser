import logging
import uuid
import json
from sqlalchemy.orm import Session
from app.models.upload import Upload
from app.models.transcript import Transcript
from app.models.analysis import AnalysisResult
from app.models.feedback import Feedback
from app.models.report import Report
from app.services.ai_service import AIService
from app.services.audio_service import AudioService
from app.services.nlp_service import NLPService
from app.core.exceptions import ProcessingException

logger = logging.getLogger(__name__)

class ReportService:
    @staticmethod
    def process_and_generate_report(db: Session, upload_id: uuid.UUID) -> Report:
        """
        Synchronously coordinates the entire speech and textual analysis pipeline.
        Updates DB status accordingly.
        """
        upload = db.query(Upload).filter(Upload.id == upload_id).first()
        if not upload:
            logger.error(f"Failed to trigger analysis: Upload ID {upload_id} not found.")
            return None

        # 1. Update status to processing
        upload.status = "processing"
        db.commit()

        try:
            logger.info(f"Starting pipeline execution for Upload ID: {upload_id}")
            
            # 2. Transcription (Whisper)
            transcription_result = AIService.transcribe_audio(upload.filepath)
            
            # Save Transcript
            db_transcript = Transcript(
                upload_id=upload.id,
                full_text=transcription_result["full_text"],
                language=transcription_result["language"],
                words_json=transcription_result["words"],
                sentences_json=transcription_result["sentences"]
            )
            db.add(db_transcript)
            
            # Calculate word counts
            words_list = transcription_result["words"]
            word_count = len(words_list) if words_list else len(transcription_result["full_text"].split())

            # 3. Audio Analysis (Librosa)
            audio_metrics = AudioService.analyze_audio(upload.filepath, word_count)
            
            # Update upload duration
            upload.duration = audio_metrics["duration"]
            db.commit()

            # 4. NLP Analysis (NLTK, TextBlob)
            nlp_metrics = NLPService.analyze_text(transcription_result["full_text"])

            # 5. Save Analysis Results
            db_analysis = AnalysisResult(
                upload_id=upload.id,
                speaking_rate=audio_metrics["speaking_rate"],
                pitch_mean=audio_metrics["pitch_mean"],
                pitch_stability=audio_metrics["pitch_stability"],
                energy=audio_metrics["energy"],
                pauses_count=audio_metrics["pauses_count"],
                silence_duration=audio_metrics["silence_duration"],
                voice_modulation=audio_metrics["voice_modulation"],
                
                filler_words=nlp_metrics["filler_words"],
                repeated_words=nlp_metrics["repeated_words"],
                grammar_issues=nlp_metrics["grammar_issues"],
                sentiment_polarity=nlp_metrics["sentiment_polarity"],
                sentiment_subjectivity=nlp_metrics["sentiment_subjectivity"],
                keywords=nlp_metrics["keywords"],
                confidence_indicators=nlp_metrics["confidence_indicators"],
                speaking_style=audio_metrics["speaking_style"]
            )
            db.add(db_analysis)

            # Combine metrics for AI Feedback Generation
            combined_metrics = {
                "speaking_rate": audio_metrics["speaking_rate"],
                "pitch_mean": audio_metrics["pitch_mean"],
                "pitch_stability": audio_metrics["pitch_stability"],
                "energy": audio_metrics["energy"],
                "pauses_count": audio_metrics["pauses_count"],
                "silence_duration": audio_metrics["silence_duration"],
                "voice_modulation": audio_metrics["voice_modulation"],
                "speaking_style": audio_metrics["speaking_style"],
                "sentiment_polarity": nlp_metrics["sentiment_polarity"],
                "sentiment_subjectivity": nlp_metrics["sentiment_subjectivity"]
            }

            # 6. AI Feedback Generation (GPT / local fallback)
            feedback_data = AIService.generate_ai_feedback(
                transcription_result["full_text"], 
                combined_metrics
            )
            
            db_feedback = Feedback(
                upload_id=upload.id,
                strengths=feedback_data["strengths"],
                weaknesses=feedback_data["weaknesses"],
                suggestions=feedback_data["suggestions"],
                overall_review=feedback_data["overall_review"],
                presentation_tips=feedback_data["presentation_tips"],
                communication_tips=feedback_data["communication_tips"],
                confidence_tips=feedback_data["confidence_tips"]
            )
            db.add(db_feedback)

            # 7. Score Calculation
            scores = ReportService.calculate_scores(audio_metrics, nlp_metrics, word_count)
            
            db_report = Report(
                upload_id=upload.id,
                user_id=upload.user_id,
                clarity_score=scores["clarity_score"],
                confidence_score=scores["confidence_score"],
                engagement_score=scores["engagement_score"],
                communication_score=scores["communication_score"],
                voice_quality_score=scores["voice_quality_score"],
                overall_score=scores["overall_score"]
            )
            db.add(db_report)

            # 8. Mark upload as completed
            upload.status = "completed"
            db.commit()
            
            logger.info(f"Pipeline successfully completed for Upload ID: {upload_id}")
            return db_report

        except Exception as e:
            logger.error(f"Pipeline execution failed for Upload ID {upload_id}: {str(e)}", exc_info=True)
            db.rollback()
            upload.status = "failed"
            db.commit()
            raise ProcessingException(f"Pipeline analysis execution failed: {str(e)}")

    @staticmethod
    def calculate_scores(audio_metrics: dict, nlp_metrics: dict, total_words: int) -> dict:
        """
        Calculate individual metrics out of 100.
        """
        wpm = audio_metrics["speaking_rate"]
        duration = audio_metrics["duration"]
        silence = audio_metrics["silence_duration"]
        pauses = audio_metrics["pauses_count"]
        modulation = audio_metrics["voice_modulation"]
        pitch_std = audio_metrics["pitch_stability"]
        pitch_mean = audio_metrics["pitch_mean"]
        
        filler_count = sum(nlp_metrics["filler_words"].values())
        repeated_count = len(nlp_metrics["repeated_words"])
        grammar_count = len(nlp_metrics["grammar_issues"])
        polarity = nlp_metrics["sentiment_polarity"]
        subjectivity = nlp_metrics["sentiment_subjectivity"]
        
        conf_markers = nlp_metrics["confidence_indicators"]
        high_conf = conf_markers["high_count"]
        low_conf = conf_markers["low_count"]

        # --- 1. CLARITY SCORE (WPM + Silence + Grammar) ---
        # Ideal speaking pace is between 130 and 160 WPM
        wpm_score = 100.0 - abs(wpm - 145.0) * 0.8
        wpm_score = max(20.0, min(100.0, wpm_score))
        
        # Silence ratio penalty
        silence_ratio = silence / duration if duration > 0 else 0
        silence_score = 100.0 - (silence_ratio * 120.0)
        silence_score = max(20.0, min(100.0, silence_score))
        
        # Grammar deductions (5 points per error)
        grammar_score = max(50.0, 100.0 - (grammar_count * 5.0))
        
        clarity_score = (wpm_score * 0.4) + (silence_score * 0.3) + (grammar_score * 0.3)

        # --- 2. CONFIDENCE SCORE (Filler Words + Hesitations + Tone stability) ---
        # Filler word density penalty
        filler_ratio = filler_count / total_words if total_words > 0 else 0
        filler_score = 100.0 - (filler_ratio * 350.0)
        filler_score = max(30.0, min(100.0, filler_score))
        
        # Hesitation words count penalty
        hesitation_score = 100.0 - (low_conf * 4.0) + (high_conf * 2.0)
        hesitation_score = max(30.0, min(100.0, hesitation_score))
        
        # Monotone/Erratic pitch penalty
        # Pitch standard deviation between 12-25Hz is optimal for vocal confidence
        if pitch_std < 8.0:
            pitch_conf_score = max(40.0, 100.0 - (8.0 - pitch_std) * 8.0)
        elif pitch_std > 35.0:
            pitch_conf_score = max(40.0, 100.0 - (pitch_std - 35.0) * 2.0)
        else:
            pitch_conf_score = 100.0
            
        confidence_score = (filler_score * 0.4) + (hesitation_score * 0.3) + (pitch_conf_score * 0.3)

        # --- 3. ENGAGEMENT SCORE (Voice Modulation + Sentiment Polarity) ---
        # Direct vocal expressiveness (modulation)
        mod_score = max(20.0, min(100.0, modulation))
        
        # Sentiment polarity (ideal is expressive positive pitch: polarity > 0.05)
        # Polarity maps [-1, 1] to [40, 100]
        sentiment_score = 50.0 + (polarity * 50.0)
        sentiment_score = max(30.0, min(100.0, sentiment_score))
        
        engagement_score = (mod_score * 0.6) + (sentiment_score * 0.4)

        # --- 4. COMMUNICATION SCORE (Style + Repeated words + Vocabulary) ---
        # Classify style weights
        style_scores = {
            "Dynamic & Expressive": 98.0,
            "Engaged & Confident": 92.0,
            "Fast-Paced": 70.0,
            "Deliberate / Slow": 75.0,
            "Monotone": 45.0
        }
        style_score = style_scores.get(audio_metrics["speaking_style"], 75.0)
        
        # Repetition penalty
        repetition_score = max(40.0, 100.0 - (repeated_count * 8.0))
        
        # Subjectivity penalty (0.4-0.6 is balanced. Purely dry (0) or emotional (1) is penalized)
        subj_diff = abs(subjectivity - 0.5)
        subj_score = 100.0 - (subj_diff * 60.0)
        
        communication_score = (style_score * 0.4) + (repetition_score * 0.3) + (subj_score * 0.3)

        # --- 5. VOICE QUALITY SCORE (Energy variance + Pitch Range stability) ---
        # Stable voice energy (energy_std relative to energy_mean)
        # We want high energy std deviation to represent expressive stress, but not highly erratic volume spikes
        voice_quality_score = 50.0 + (modulation * 0.5)
        voice_quality_score = max(40.0, min(100.0, voice_quality_score))

        # --- 6. OVERALL SCORE (Weighted average) ---
        overall_score = (
            (clarity_score * 0.20) + 
            (confidence_score * 0.25) + 
            (engagement_score * 0.20) + 
            (communication_score * 0.20) + 
            (voice_quality_score * 0.15)
        )

        return {
            "clarity_score": round(clarity_score, 1),
            "confidence_score": round(confidence_score, 1),
            "engagement_score": round(engagement_score, 1),
            "communication_score": round(communication_score, 1),
            "voice_quality_score": round(voice_quality_score, 1),
            "overall_score": round(overall_score, 1)
        }
