# ocr_trainer.py
"""
Enhanced OCR training utility with comprehensive dictionary validation and spelling correction
"""
import json
import re
from pathlib import Path
from typing import Set, List, Tuple, Dict
from config import SAVE_DIR
import os

class OCRTrainer:
    def __init__(self, language_model=None):
        self.language_model = language_model
        self.training_file = Path(SAVE_DIR) / "ocr_training_data.json"
        self.english_dictionary = self._load_english_dictionary()
        self.load_training_data()
        print(f"OCR Trainer initialized with {len(self.english_dictionary)} words in dictionary")

    def _load_english_dictionary(self) -> Set[str]:
        """Load comprehensive English dictionary from word_list.txt."""
        dictionary = set()

        # Try multiple possible locations for the word list
        possible_paths = [
            Path(SAVE_DIR) / "word_list.txt",  # In save directory
            Path(__file__).parent / "word_list.txt",  # Same directory as this file
            Path(__file__).parent.parent / "word_list.txt",  # Parent directory
            Path("word_list.txt")  # Current working directory
        ]

        word_list_path = None
        for path in possible_paths:
            if path.exists():
                word_list_path = path
                break

        if word_list_path and word_list_path.exists():
            try:
                with open(word_list_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        word = line.strip().lower()
                        if word and len(word) > 1:  # Only add words with 2+ characters
                            dictionary.add(word)
                print(f"Successfully loaded {len(dictionary)} words from {word_list_path}")
            except Exception as e:
                print(f"Error loading dictionary from {word_list_path}: {e}")
                dictionary = self._get_fallback_dictionary()
        else:
            print("Word list file not found. Using fallback dictionary.")
            dictionary = self._get_fallback_dictionary()

        return dictionary

    def _get_fallback_dictionary(self) -> Set[str]:
        """Provide a fallback dictionary if word_list.txt is not found."""
        fallback_words = {
            "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
            "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
            "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
            "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
            "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
            "when", "make", "can", "like", "time", "no", "just", "him", "know", "take",
            "people", "into", "year", "your", "good", "some", "could", "them", "see",
            "other", "than", "then", "now", "look", "only", "come", "its", "over", "think",
            "also", "back", "after", "use", "two", "how", "our", "work", "first", "well",
            "way", "even", "new", "want", "because", "any", "these", "give", "day", "most", "us"
        }
        print(f"Using fallback dictionary with {len(fallback_words)} words")
        return fallback_words

    def validate_with_dictionary(self, text: str) -> Dict[str, float]:
        """
        Comprehensive text validation against English dictionary.
        Returns detailed confidence metrics.
        """
        if not text or len(text.strip()) < 3:
            return self._get_empty_confidence_metrics()

        # Extract words from text
        words = self._extract_words(text)
        if not words:
            return self._get_empty_confidence_metrics()

        # Calculate various confidence metrics
        word_confidence = self._calculate_word_confidence(words)
        sequence_confidence = self._calculate_sequence_confidence(words)
        length_confidence = self._calculate_length_confidence(words)
        capitalization_confidence = self._calculate_capitalization_confidence(text)

        # Combined confidence score
        overall_confidence = (
            word_confidence * 0.5 +
            sequence_confidence * 0.3 +
            length_confidence * 0.1 +
            capitalization_confidence * 0.1
        )

        return {
            "overall_confidence": round(overall_confidence, 3),
            "word_confidence": round(word_confidence, 3),
            "sequence_confidence": round(sequence_confidence, 3),
            "length_confidence": round(length_confidence, 3),
            "capitalization_confidence": round(capitalization_confidence, 3),
            "valid_word_count": len([w for w in words if self._is_valid_word(w)]),
            "total_word_count": len(words),
            "valid_word_ratio": round(word_confidence, 3)
        }

    def _get_empty_confidence_metrics(self) -> Dict[str, float]:
        """Return empty confidence metrics for invalid text."""
        return {
            "overall_confidence": 0.0,
            "word_confidence": 0.0,
            "sequence_confidence": 0.0,
            "length_confidence": 0.0,
            "capitalization_confidence": 0.0,
            "valid_word_count": 0,
            "total_word_count": 0,
            "valid_word_ratio": 0.0
        }

    def _extract_words(self, text: str) -> List[str]:
        """Extract clean words from text, preserving hyphenated words."""
        # Replace punctuation with spaces, keep hyphens for compound words
        clean_text = re.sub(r'[^\w\s-]', ' ', text.lower())
        words = [word for word in clean_text.split() if len(word) > 1]  # Ignore single characters
        return words

    def _is_valid_word(self, word: str) -> bool:
        """Check if a word is in the dictionary or a valid variation."""
        word_lower = word.lower()

        # Exact match
        if word_lower in self.english_dictionary:
            return True

        # Handle common suffixes and variations
        return self._check_word_variations(word_lower)

    def _check_word_variations(self, word: str) -> bool:
        """Check for common word variations and suffixes."""
        if len(word) < 3:
            return False

        # Check for plural 's'
        if word.endswith('s') and word[:-1] in self.english_dictionary:
            return True

        # Check for 'ing' suffix
        if word.endswith('ing'):
            # Check direct stem
            if word[:-3] in self.english_dictionary:
                return True
            # Check stem + 'e' (like 'making' from 'make')
            if word[:-3] + 'e' in self.english_dictionary:
                return True

        # Check for 'ed' suffix
        if word.endswith('ed'):
            if word[:-2] in self.english_dictionary:  # 'worked' from 'work'
                return True
            if word[:-1] in self.english_dictionary:  # 'loved' from 'love' (keep 'e')
                return True

        # Check for 'er' suffix
        if word.endswith('er') and word[:-2] in self.english_dictionary:
            return True

        # Check for 'ly' suffix
        if word.endswith('ly') and word[:-2] in self.english_dictionary:
            return True

        # Check for 'ness' suffix
        if word.endswith('ness') and word[:-4] in self.english_dictionary:
            return True

        return False

    def _calculate_word_confidence(self, words: List[str]) -> float:
        """Calculate confidence based on valid word ratio."""
        if not words:
            return 0.0

        valid_count = sum(1 for word in words if self._is_valid_word(word))
        return valid_count / len(words)

    def _calculate_sequence_confidence(self, words: List[str]) -> float:
        """Calculate confidence based on sequences of valid words."""
        if not words:
            return 0.0

        max_sequence = 0
        current_sequence = 0
        total_sequences = 0
        sequence_lengths = []

        for word in words:
            if self._is_valid_word(word):
                current_sequence += 1
                max_sequence = max(max_sequence, current_sequence)
            else:
                if current_sequence > 0:
                    sequence_lengths.append(current_sequence)
                    total_sequences += 1
                current_sequence = 0

        # Don't forget the last sequence
        if current_sequence > 0:
            sequence_lengths.append(current_sequence)
            total_sequences += 1

        if not sequence_lengths:
            return 0.0

        # Calculate average sequence length and normalize
        avg_sequence = sum(sequence_lengths) / len(sequence_lengths)
        return min(avg_sequence / 5.0, 1.0)  # Normalize: 5+ word sequences get max score

    def _calculate_length_confidence(self, words: List[str]) -> float:
        """Calculate confidence based on word lengths and distribution."""
        if len(words) < 3:
            return 0.2  # Very short text gets low score

        # Calculate average word length
        avg_length = sum(len(word) for word in words) / len(words)

        # Normalize: ideal average length is 5-7 characters
        if 4 <= avg_length <= 8:
            length_score = 1.0
        else:
            length_score = max(0.1, 1.0 - abs(avg_length - 6) / 10)

        return length_score

    def _calculate_capitalization_confidence(self, text: str) -> float:
        """Calculate confidence based on proper capitalization."""
        sentences = re.split(r'[.!?]+', text)
        valid_sentences = 0
        total_sentences = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 1:
                total_sentences += 1
                if sentence[0].isupper():
                    valid_sentences += 1

        if total_sentences == 0:
            return 0.5  # Neutral score for no clear sentences

        return valid_sentences / total_sentences

    def correct_spelling(self, text: str) -> Tuple[str, float]:
        """
        Advanced spelling correction using Levenshtein distance.
        Returns (corrected_text, improvement_score)
        """
        if not text:
            return text, 0.0

        words = text.split()
        corrected_words = []
        improvements = 0
        total_correctable = 0

        for i, word in enumerate(words):
            original_word = word
            corrected_word = self._correct_single_word(word, i, words)

            if corrected_word != original_word:
                improvements += 1
                corrected_words.append(corrected_word)
            else:
                corrected_words.append(word)

            # Only count words that are candidates for correction
            if self._is_correctable_word(original_word):
                total_correctable += 1

        improvement_score = improvements / total_correctable if total_correctable > 0 else 0.0
        corrected_text = ' '.join(corrected_words)

        return corrected_text, improvement_score

    def _is_correctable_word(self, word: str) -> bool:
        """Check if a word is a candidate for correction."""
        clean_word = re.sub(r'[^\w]', '', word.lower())
        return (len(clean_word) >= 3 and
                clean_word not in self.english_dictionary and
                not clean_word.isdigit())

    def _correct_single_word(self, word: str, position: int, all_words: List[str]) -> str:
        """Correct a single word using context-aware spelling correction."""
        clean_word = re.sub(r'[^\w]', '', word.lower())

        # Skip if too short, already correct, or is a number
        if len(clean_word) < 3 or clean_word in self.english_dictionary or clean_word.isdigit():
            return word

        # Find closest matches
        candidates = self._find_candidate_words(clean_word)

        if not candidates:
            return word  # No good candidates found

        # Use context to choose the best candidate
        best_candidate = self._select_best_candidate(candidates, position, all_words)

        if best_candidate:
            # Preserve original capitalization
            if word[0].isupper():
                best_candidate = best_candidate.capitalize()
            return best_candidate
        else:
            return word

    def _find_candidate_words(self, word: str, max_distance: int = 2) -> List[Tuple[str, int]]:
        """Find candidate words within maximum Levenshtein distance."""
        candidates = []

        for dict_word in self.english_dictionary:
            # Quick length check to avoid expensive calculation
            if abs(len(dict_word) - len(word)) > max_distance:
                continue

            distance = self._levenshtein_distance(word, dict_word)
            if distance <= max_distance:
                candidates.append((dict_word, distance))

        # Sort by distance and return top candidates
        candidates.sort(key=lambda x: x[1])
        return candidates[:5]  # Return top 5 candidates

    def _select_best_candidate(self, candidates: List[Tuple[str, int]],
                             position: int, all_words: List[str]) -> str:
        """Select the best candidate using context and distance."""
        if not candidates:
            return None

        # If only one candidate, use it
        if len(candidates) == 1:
            return candidates[0][0]

        # Use the closest match (first in sorted list)
        return candidates[0][0]

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def calculate_comprehensive_confidence(self, text: str) -> Dict[str, any]:
        """
        Calculate comprehensive confidence scores for text.
        Returns detailed analysis including corrected text.
        """
        # Get dictionary validation metrics
        validation_metrics = self.validate_with_dictionary(text)

        # Get spelling correction
        corrected_text, improvement_score = self.correct_spelling(text)

        # Text structure analysis
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        avg_line_length = sum(len(line) for line in lines) / len(lines) if lines else 0
        structure_score = min(avg_line_length / 60, 1.0)  # Normalize line length

        # Calculate enhanced overall confidence
        enhanced_confidence = (
            validation_metrics["overall_confidence"] * 0.6 +
            improvement_score * 0.2 +
            structure_score * 0.2
        )

        # Determine quality level
        if enhanced_confidence >= 0.8:
            quality = "HIGH"
        elif enhanced_confidence >= 0.6:
            quality = "MEDIUM"
        elif enhanced_confidence >= 0.4:
            quality = "LOW"
        else:
            quality = "POOR"

        return {
            "original_text": text,
            "corrected_text": corrected_text,
            "quality": quality,
            "overall_confidence": round(enhanced_confidence, 3),
            "validation_metrics": validation_metrics,
            "improvement_score": round(improvement_score, 3),
            "structure_score": round(structure_score, 3),
            "line_count": len(lines),
            "word_count": validation_metrics["total_word_count"],
            "should_keep": enhanced_confidence >= 0.3  # Minimum threshold to keep result
        }

    def load_training_data(self):
        """Load previous training data."""
        if self.training_file.exists():
            try:
                with open(self.training_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for text in data.get('training_texts', []):
                        if self.language_model:
                            self.language_model.train_on_text(text)
                print(f"Loaded training data from {self.training_file}")
            except Exception as e:
                print(f"Error loading training data: {e}")

    def add_training_text(self, text: str, min_confidence: float = 0.6) -> Tuple[bool, Dict]:
        """
        Add new text to training data only if it meets confidence threshold.
        Returns (success, confidence_data)
        """
        confidence_data = self.calculate_comprehensive_confidence(text)

        if confidence_data["overall_confidence"] >= min_confidence:
            # Use corrected text for training
            training_text = confidence_data["corrected_text"]

            if self.language_model:
                self.language_model.train_on_text(training_text)

            # Save to file
            data = {'training_texts': []}
            if self.training_file.exists():
                try:
                    with open(self.training_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except:
                    pass

            data['training_texts'].append(training_text)

            try:
                with open(self.training_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"Error saving training data: {e}")

            return True, confidence_data
        else:
            return False, confidence_data

    def get_dictionary_info(self) -> Dict[str, any]:
        """Get information about the loaded dictionary."""
        sample_words = list(self.english_dictionary)[:20]  # First 20 words
        return {
            "total_words": len(self.english_dictionary),
            "sample_words": sample_words,
            "avg_word_length": sum(len(word) for word in self.english_dictionary) / len(self.english_dictionary)
        }