"""
Configuration constants and settings for DocCamOCR with USB camera optimizations
"""

import os
import sys
import logging
from pathlib import Path
from PyQt5.QtCore import QSettings
from logging.handlers import RotatingFileHandler

# Application info
APP_NAME = "DocCamOCR"
APP_VERSION = "2.0"
ORGANIZATION = "YorkUniversity"

# File paths
SAVE_DIR = Path.home() / "Documents" / "DocCamOCR"
SAVE_DIR.mkdir(exist_ok=True)

# Camera settings - Simplified for reliability
DEFAULT_RESOLUTION = (640, 480)
SUPPORTED_RESOLUTIONS = [
    (640, 480),    # Most compatible
    (800, 600),
    (1280, 720),
    (1920, 1080)
]
MAX_CAMERAS = 10
CAMERA_FPS = 30

# Simple backend selection
def get_camera_backends(camera_index: int):
    """Simple backend selection without complex hardware detection."""
    import platform
    if platform.system() == 'Windows':
        return ['DSHOW', 'MSMF', 'ANY']
    else:
        return ['ANY']

def get_optimal_camera_backends(camera_index: int) -> list:
    """Get optimal camera backends with USB camera optimizations."""
    system = sys.platform

    # System-specific default backends optimized for USB cameras
    system_defaults = {
        'win32': ['DSHOW', 'MSMF', 'ANY'],  # DSHOW is most reliable for USB on Windows
        'darwin': ['AVFOUNDATION', 'ANY'],   # AVFoundation for macOS
        'linux': ['V4L2', 'ANY']             # V4L2 for Linux USB cameras
    }

    # Camera-specific overrides from hardware detection
    camera_profiles = detect_camera_hardware()
    camera_specific = camera_profiles.get(camera_index, {})

    # Combine system defaults with camera-specific optimizations
    backends = camera_specific.get('backends', system_defaults.get(system, ['ANY']))

    # Remove duplicates while preserving order
    seen = set()
    return [b for b in backends if not (b in seen or seen.add(b))]

# OCR settings
TESSERACT_CONFIG = r"--oem 3 --psm 6 -l eng"
OCR_PROCESSING_FPS = 5

# PDF settings
PDF_MARGIN = 10
PDF_PAGE_WIDTH = 210
PDF_IMAGE_WIDTH = 190

# OCR Preprocessing Settings
OCR_PREPROCESSING = {
    "blur_kernel_size": 3,
    "clahe_clip_limit": 2.0,
    "clahe_grid_size": 8,
    "adaptive_threshold_block": 11,
    "adaptive_threshold_c": 2,
    "use_roi": True,
    "roi_margin": 0.1
}

# Tesseract OCR Paths
TESSERACT_PATHS = {
    "windows": [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
    ],
    "darwin": "/usr/local/bin/tesseract",
    "linux": "/usr/bin/tesseract"
}

def get_tesseract_path():
    """Get the appropriate Tesseract path for the current platform."""
    system = sys.platform
    if system.startswith('win'):
        for path in TESSERACT_PATHS["windows"]:
            if os.path.exists(path):
                return path
        return TESSERACT_PATHS["windows"][0]
    elif system == 'darwin':
        return TESSERACT_PATHS["darwin"]
    else:
        return TESSERACT_PATHS["linux"]

TESSERACT_PATH = get_tesseract_path()

def validate_tesseract_path() -> bool:
    """Validate Tesseract installation and accessibility."""
    try:
        import pytesseract
        tesseract_version = pytesseract.get_tesseract_version()
        logger.info(f"Tesseract version: {tesseract_version}")
        return True
    except Exception as e:
        logger.error(f"Tesseract validation failed: {e}")
        return False

# USB Camera Specific Settings
USB_CAMERA_SETTINGS = {
    "warm_up_frames": 5,           # Number of frames to discard during warm-up
    "frame_timeout": 3.0,          # Timeout for frame reading
    "retry_attempts": 3,           # Number of retry attempts
    "buffer_size": 1,              # Camera buffer size
    "preferred_fps": 30,           # Preferred FPS
    "exposure_compensation": 0.5,  # Exposure compensation
}

class AppSettings:
    def __init__(self):
        self.settings = QSettings(ORGANIZATION, APP_NAME)

    def get_camera_index(self) -> int:
        return self.settings.value("camera/index", 0, type=int)

    def set_camera_index(self, index: int):
        self.settings.setValue("camera/index", index)

    def get_resolution(self) -> str:
        return self.settings.value("camera/resolution", "640x480", type=str)

    def set_resolution(self, resolution: str):
        self.settings.setValue("camera/resolution", resolution)

    def get_save_directory(self) -> str:
        return self.settings.value("files/save_directory", str(SAVE_DIR), type=str)

    def set_save_directory(self, directory: str):
        self.settings.setValue("files/save_directory", directory)

# OCR configurations
TESSERACT_CONFIGS = {
    "default": "--oem 3 --psm 6",
    "single_line": "--oem 3 --psm 7",
    "single_word": "--oem 3 --psm 8",
    "sparse_text": "--oem 3 --psm 11",
    "uniform_block": "--oem 3 --psm 6"
}

TESSERACT_CONFIG = TESSERACT_CONFIGS["uniform_block"]

# Enhanced OCR Settings
OCR_ENHANCEMENT = {
    "preprocessing_strategies": 4,
    "min_confidence_threshold": 50,
    "max_processing_fps": 3,
    "spell_check_enabled": True,
    "grammar_check_enabled": True,
    "text_correction_enabled": True,
    "ensemble_voting": True,
}

# Language Settings
LANGUAGE_SETTINGS = {
    "primary_language": "eng",
    "fallback_languages": ["eng", "fra", "spa"],
    "custom_dictionary": [
        "homo", "deus", "yuval", "harari", "history", "tomorrow", "brief",
        "document", "camera", "ocr", "york", "university"
    ]
}

def setup_logging():
    """Setup application logging."""
    log_file = SAVE_DIR / "app.log"

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # File handler
    file_handler = RotatingFileHandler(
        log_file, maxBytes=1024*1024, backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logging.info("Logging setup completed")