"""
Enhanced custom GUI widgets
"""
from PyQt5.QtWidgets import (QLabel, QTextEdit, QWidget, QHBoxLayout,
                            QVBoxLayout, QPushButton, QComboBox, QFrame)
from PyQt5.QtGui import QPixmap, QImage, QFont, QPalette, QColor, QTextCursor
from PyQt5.QtCore import Qt, QTimer
import cv2
import logging

logger = logging.getLogger(__name__)

class CameraPreview(QLabel):
    """Enhanced camera preview with visual feedback and borders."""

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(640, 480)
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #cccccc;
                background-color: black;
                border-radius: 4px;
            }
        """)
        self.original_style = self.styleSheet()

    def update_frame(self, frame):
        """Update preview with new frame."""
        try:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image).scaled(
                self.width(), self.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(pixmap)
        except Exception as e:
            logger.error(f"Error updating camera preview: {e}")

    def flash_capture_indicator(self):
        """Visual feedback for frame capture."""
        self.setStyleSheet("""
            QLabel {
                border: 4px solid #00ff00;
                background-color: black;
                border-radius: 4px;
            }
        """)
        QTimer.singleShot(300, lambda: self.setStyleSheet(self.original_style))

class OCRTextDisplay(QTextEdit):
    """Enhanced text display for OCR output with syntax highlighting."""

    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setPlaceholderText("OCR text will appear here...\n\nTips:\n- Ensure good lighting\n- Keep camera steady\n- Position text clearly in frame")
        self.setFont(QFont("Consolas", 10))
        self.max_chars = 5000  # Increased buffer
        self.text_buffer = ""

        # Set a pleasant color scheme
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor(248, 248, 248))
        palette.setColor(QPalette.ColorRole.Text, QColor(51, 51, 51))
        self.setPalette(palette)

    def update_text(self, text: str):
        """Update OCR text with enhanced display."""
        if text and len(text.strip()) > 3:  # More lenient threshold
            self.text_buffer = text[:self.max_chars]

            # Simple formatting for better readability
            formatted_text = self.format_ocr_text(self.text_buffer)
            self.setPlainText(formatted_text)

            # Auto-scroll to top - FIXED LINE
            self.moveCursor(QTextCursor.MoveOperation.Start)

    def format_ocr_text(self, text: str) -> str:
        """Format OCR text for better readability."""
        # Add some basic formatting
        lines = text.split('\n')
        formatted_lines = []

        for line in lines:
            stripped = line.strip()
            if stripped:
                # Indent paragraphs
                if len(stripped) > 50:  # Likely a paragraph
                    formatted_lines.append("  " + stripped)
                else:
                    formatted_lines.append(stripped)
            else:
                formatted_lines.append("")  # Keep empty lines

        return '\n'.join(formatted_lines)

class CameraControls(QWidget):
    """Enhanced camera selection and resolution controls."""
    def __init__(self):
        super().__init__()
        self.cam_selector = QComboBox()
        self.res_selector = QComboBox()
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Camera selection
        camera_label = QLabel("Camera:")
        camera_label.setToolTip("Select camera device")
        layout.addWidget(camera_label)

        self.cam_selector.setMinimumWidth(120)
        self.cam_selector.setToolTip("Select camera device")
        layout.addWidget(self.cam_selector)

        layout.addSpacing(20)

        # Resolution selection
        res_label = QLabel("Resolution:")
        res_label.setToolTip("Select camera resolution")
        layout.addWidget(res_label)

        self.res_selector.setMinimumWidth(120)
        self.res_selector.setToolTip("Select camera resolution")
        layout.addWidget(self.res_selector)

        layout.addStretch()

        # Info label
        self.info_label = QLabel("Select camera and resolution to start")
        self.info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.info_label)

        self.setLayout(layout)

class ActionButtons(QWidget):
    """Enhanced action buttons with better styling."""
    def __init__(self):
        super().__init__()
        self.snap_button = QPushButton("Snap Page")
        self.save_pdf_button = QPushButton("Save PDF")
        self.clear_button = QPushButton("Clear Pages")
        self.pages_label = QLabel("Pages captured: 0")
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Style buttons
        button_style = """
            QPushButton {
                padding: 8px 16px;
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: #f0f0f0;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """

        self.snap_button.setStyleSheet(button_style)
        self.snap_button.setToolTip("Capture current frame for PDF")

        self.save_pdf_button.setStyleSheet(button_style)
        self.save_pdf_button.setToolTip("Generate searchable PDF from captured pages")

        self.clear_button.setStyleSheet(button_style)
        self.clear_button.setToolTip("Clear all captured pages")

        layout.addWidget(self.snap_button)
        layout.addWidget(self.save_pdf_button)
        layout.addWidget(self.clear_button)
        layout.addSpacing(20)

        # Pages label with better styling
        self.pages_label.setStyleSheet("""
            QLabel {
                padding: 8px 12px;
                background-color: #e8f4fd;
                border: 1px solid #b8daff;
                border-radius: 4px;
                font-weight: bold;
                color: #004085;
            }
        """)
        layout.addWidget(self.pages_label)

        layout.addStretch()
        self.setLayout(layout)