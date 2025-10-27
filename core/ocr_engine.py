import logging
import cv2
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
import numpy as np

logger = logging.getLogger(__name__)


class OCREngine:
    """
    Simple wrapper around pytesseract with pre-processing.
    """

    def __init__(self, lang="eng"):
        self.lang = lang
        logger.debug("OCREngine initialized.")

    def preprocess(self, frame: np.ndarray) -> np.ndarray:
        """
        Apply lightweight preprocessing to improve OCR accuracy on any resolution.
        """
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Use CLAHE for adaptive contrast equalization
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            gray = clahe.apply(gray)
            # Slight denoise and sharpen
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            gray = cv2.addWeighted(gray, 1.5, gray, -0.5, 0)
            return gray
        except Exception as e:
            logger.error(f"Preprocessing error: {e}")
            return frame

    def run_ocr(self, frame: np.ndarray) -> str:
        """
        Run OCR on a given frame (any resolution).
        """
        try:
            processed = self.preprocess(frame)
            text = pytesseract.image_to_string(processed, lang=self.lang)
            text = text.strip()
            logger.debug(f"OCR result length: {len(text)} chars")
            return text
        except Exception as e:
            logger.error(f"OCR execution error: {e}")
            return ""
