import re
import logging
from typing import Dict, Any, List, Tuple
from collections import Counter
import nltk
from textblob import TextBlob

logger = logging.getLogger(__name__)

# Programmatically ensure NLTK packages are downloaded
for resource in ["punkt", "stopwords", "averaged_perceptron_tagger"]:
    try:
        nltk.data.find(f"tokenizers/{resource}" if resource == "punkt" else f"corpora/{resource}" if resource == "stopwords" else f"taggers/{resource}")
    except LookupError:
        try:
            nltk.download(resource, quiet=True)
        except Exception as e:
            logger.warning(f"Could not download NLTK resource {resource}: {str(e)}")

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

# Define standard lists of filler words and confidence markers
FILLER_WORDS_LIST = ["um", "uh", "like", "so", "actually", "basically", "literally", "essentially", "well"]
FILLER_PHRASES_LIST = ["you know", "i mean"]

HIGH_CONFIDENCE_WORDS = {"definitely", "absolutely", "clearly", "obviously", "certainly", "guarantee", "assure", "confident", "proven", "will", "excel"}
LOW_CONFIDENCE_WORDS = {"maybe", "probably", "perhaps", "guess", "think", "hope", "try", "possible", "possibly", "might", "could", "sort of", "kind of"}

class NLPService:
    @staticmethod
    def analyze_text(text: str) -> Dict[str, Any]:
        """
        Analyze transcript text using NLTK and TextBlob:
        - Filler Words count and occurrences
        - Repeated Words (consecutive duplicates)
        - Sentiment (polarity & subjectivity)
        - Keywords
        - Confidence Indicators
        - Grammar/Style suggestions
        """
        # Parse text using TextBlob for sentiment
        blob = TextBlob(text)
        sentiment_polarity = float(blob.sentiment.polarity)
        sentiment_subjectivity = float(blob.sentiment.subjectivity)
        
        # Tokenize words & sentences
        try:
            tokens = word_tokenize(text.lower())
            sentences = sent_tokenize(text)
        except Exception:
            # Simple regex fallback if nltk tokenization fails
            tokens = re.findall(r'\b\w+\b', text.lower())
            sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]

        # 1. Detect Filler Words and Phrases
        filler_counts = Counter()
        text_lower = text.lower()
        
        # Count words
        for t in tokens:
            if t in FILLER_WORDS_LIST:
                filler_counts[t] += 1
                
        # Count multi-word phrases
        for phrase in FILLER_PHRASES_LIST:
            count = len(re.findall(r'\b' + re.escape(phrase) + r'\b', text_lower))
            if count > 0:
                filler_counts[phrase] = count

        # 2. Detect Repeated Words (consecutive duplicates)
        repeated_words: List[Tuple[str, int]] = []
        for i in range(1, len(tokens)):
            # Ignore single letter repeating punctuation if any
            if tokens[i] == tokens[i-1] and len(tokens[i]) > 1:
                # Add to repetitions
                repeated_words.append((tokens[i], i))
                
        # Format repeated words into list of dicts for JSON
        repeated_words_dict = [{"word": word, "index": idx} for word, idx in repeated_words]

        # 3. Confidence Indicators
        high_conf_count = 0
        low_conf_count = 0
        confidence_details = {"high": [], "low": []}
        
        for t in tokens:
            if t in HIGH_CONFIDENCE_WORDS:
                high_conf_count += 1
                if t not in confidence_details["high"]:
                    confidence_details["high"].append(t)
            elif t in LOW_CONFIDENCE_WORDS:
                low_conf_count += 1
                if t not in confidence_details["low"]:
                    confidence_details["low"].append(t)
                    
        # Check for hedge phrases like "sort of", "kind of" via regex
        for hedge in ["sort of", "kind of"]:
            count = len(re.findall(r'\b' + re.escape(hedge) + r'\b', text_lower))
            if count > 0:
                low_conf_count += count
                confidence_details["low"].append(hedge)

        # 4. Keyword Extraction
        keywords = []
        try:
            stop_words = set(stopwords.words('english'))
        except Exception:
            stop_words = {"the", "a", "an", "and", "or", "but", "is", "are", "was", "to", "for", "in", "of", "on", "at", "by", "with"}
            
        # Clean tokens of punctuation & stopwords
        meaningful_tokens = [
            t for t in tokens 
            if t.isalpha() and t not in stop_words and len(t) > 2
        ]
        
        # Get top 8 keywords
        keyword_counts = Counter(meaningful_tokens)
        keywords = [word for word, count in keyword_counts.most_common(8)]

        # 5. Grammar & Style Heuristics
        grammar_issues = []
        # Check for extremely long run-on sentences (e.g. > 30 words)
        for idx, sent in enumerate(sentences):
            word_count = len(sent.split())
            if word_count > 30:
                grammar_issues.append({
                    "sentence_index": idx,
                    "text": sent[:60] + "...",
                    "issue": "Run-on sentence detected. Consider splitting this into smaller sentences to improve investor clarity."
                })
            
            # Heuristically check for double negation or spelling flags
            if re.search(r'\b(don\'t|dont|not|never|no)\b.*\b(no|never|nothing|nowhere)\b', sent.lower()):
                grammar_issues.append({
                    "sentence_index": idx,
                    "text": sent[:60] + "...",
                    "issue": "Potential double negation. Revise to active, positive phrasing."
                })

        return {
            "filler_words": dict(filler_counts),
            "repeated_words": repeated_words_dict,
            "grammar_issues": grammar_issues,
            "sentiment_polarity": sentiment_polarity,
            "sentiment_subjectivity": sentiment_subjectivity,
            "keywords": keywords,
            "confidence_indicators": {
                "high_count": high_conf_count,
                "low_count": low_conf_count,
                "markers": confidence_details
            }
        }
