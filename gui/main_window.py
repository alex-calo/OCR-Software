import logging
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QTextEdit, QFileDialog, QComboBox
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import numpy as np
from core.camera_thread import CameraThread
from core.ocr_engine import OCREngine
from core.pdf_generator import PDFGenerator
import cv2

logger = logging.getLogger(__name__)


class DocCamApp(QMainWindow):
    """
    Main application window for DocCam OCR.
    """

    def __init__(self):
        super().__init__()
        logger.info("Initializing DocCamApp...")
        self.setWindowTitle("DocCam OCR")
        self.setGeometry(100, 100, 1100, 700)

        # Core components
        self.ocr_engine = OCREngine()
        self.pdf_generator = PDFGenerator()
        self.current_frame = None
        self.last_ocr_text = ""

        # === Layout setup ===
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)

        # Left: camera feed
        self.camera_layout = QVBoxLayout()
        self.camera_label = QLabel("Camera feed will appear here")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_layout.addWidget(self.camera_label)

        # Buttons and camera switch
        self._init_controls()
        self.layout.addLayout(self.camera_layout)

        # Right: OCR text view
        self.text_view = QTextEdit()
        self.text_view.setReadOnly(True)
        self.text_view.setPlaceholderText("OCR results will appear here...")
        self.layout.addWidget(self.text_view)

        # Camera thread
        self.camera_thread = CameraThread()
        self.camera_thread.frame_ready.connect(self.update_frame)
        self.camera_thread.error.connect(self.handle_camera_error)

        logger.info("UI setup completed successfully")

    def _init_controls(self):
        """Initialize the camera control buttons and switcher."""
        controls_layout = QHBoxLayout()

        self.start_button = QPushButton("Start Camera")
        self.stop_button = QPushButton("Stop Camera")
        self.capture_button = QPushButton("Capture + OCR")
        self.export_pdf_button = QPushButton("Export PDF")

        # Camera switch dropdown
        self.camera_selector = QComboBox()
        self.camera_selector.setToolTip("Select camera device")
        self._populate_camera_list()

        controls_layout.addWidget(self.start_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addWidget(self.capture_button)
        controls_layout.addWidget(self.export_pdf_button)
        controls_layout.addWidget(self.camera_selector)

        self.camera_layout.addLayout(controls_layout)

        # Connect buttons
        self.start_button.clicked.connect(self.start_camera)
        self.stop_button.clicked.connect(self.stop_camera)
        self.capture_button.clicked.connect(self.capture_and_ocr)
        self.export_pdf_button.clicked.connect(self.export_pdf)
        self.camera_selector.currentIndexChanged.connect(self.switch_camera)

    def _populate_camera_list(self):
        """Detect available cameras (0-4) and populate dropdown."""
        self.camera_selector.clear()
        for index in range(5):
            cap = cv2.VideoCapture(index)
            if cap.isOpened():
                self.camera_selector.addItem(f"Camera {index}", index)
                cap.release()
        if self.camera_selector.count() == 0:
            self.camera_selector.addItem("No camera detected", -1)

    def start_camera(self):
        try:
            if not self.camera_thread.isRunning():
                self.camera_thread.start()
                logger.info("Camera started.")
        except Exception as e:
            logger.error(f"Error starting camera: {e}")

    def stop_camera(self):
        try:
            if self.camera_thread.isRunning():
                self.camera_thread.stop()
                logger.info("Camera stopped.")
        except Exception as e:
            logger.error(f"Error stopping camera: {e}")

    def switch_camera(self, index):
        """Switch camera when dropdown changes."""
        if self.camera_selector.count() == 0:
            return
        new_index = self.camera_selector.currentData()
        if new_index == -1:
            return
        try:
            self.camera_thread.switch_camera(new_index)
            logger.info(f"Switched to camera {new_index}")
        except Exception as e:
            logger.error(f"Failed to switch camera: {e}")

    def update_frame(self, frame: np.ndarray):
        """Display frame in QLabel."""
        try:
            self.current_frame = frame
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_BGR888)
            self.camera_label.setPixmap(QPixmap.fromImage(q_img))
        except Exception as e:
            logger.error(f"Error displaying camera frame: {e}")

    def capture_and_ocr(self):
        """Capture current frame and process OCR."""
        if self.current_frame is None:
            logger.warning("No frame available for OCR.")
            return
        try:
            text = self.ocr_engine.run_ocr(self.current_frame)
            self.last_ocr_text = text
            self.text_view.setText(text if text else "[No text detected]")
            logger.info("OCR completed successfully.")
        except Exception as e:
            logger.error(f"OCR failed: {e}")

    def export_pdf(self):
        """Generate PDF from OCR text."""
        if not self.last_ocr_text.strip():
            logger.warning("No OCR text available to export.")
            return
        try:
            save_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
            if save_path:
                self.pdf_generator.generate_pdf(self.last_ocr_text, save_path)
                logger.info(f"PDF exported to {save_path}")
        except Exception as e:
            logger.error(f"PDF export failed: {e}")

    def handle_camera_error(self, msg: str):
        logger.error(f"Camera error: {msg}")

    def closeEvent(self, event):
        logger.info("Application closing - performing cleanup...")
        try:
            self.stop_camera()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
        logger.info("Cleanup completed successfully")
        event.accept()
