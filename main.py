"""
Main entry point for DocCamOCR with splash screen reflecting real initialization
"""
import sys
import os
import logging
from PyQt5.QtWidgets import QApplication, QSplashScreen, QProgressBar
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer

# Reduce OpenCV verbosity
os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'
os.environ['OPENCV_VIDEOIO_DEBUG'] = 'FALSE'

def main():
    """Launch the main application window with splash screen and real-time progress."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("doc_cam_ocr.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting DocCamOCR application...")

    try:
        app = QApplication(sys.argv)
        app.setApplicationName("DocCamOCR")
        app.setApplicationVersion("1.0.0")

        # === Splash screen setup ===
        splash_image = os.path.join("assets", "texta.png")
        splash = None
        progress = None
        if os.path.exists(splash_image):
            pixmap = QPixmap(splash_image)
            splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint)
            splash.setMask(pixmap.mask())
            splash.show()
            app.processEvents()

            # Progress bar
            progress = QProgressBar(splash)
            progress.setGeometry(50, pixmap.height() - 50, pixmap.width() - 100, 20)
            progress.setMaximum(100)
            progress.setValue(0)
            progress.setTextVisible(True)
            app.processEvents()

        def update_progress(value, message=None):
            if progress:
                progress.setValue(value)
            if splash and message:
                splash.showMessage(message, Qt.AlignBottom | Qt.AlignCenter, Qt.white)
            app.processEvents()

        # === Real initialization steps ===

        # 1️⃣ Loading GUI modules
        update_progress(10, "Loading GUI modules...")
        from gui.main_window import DocCamApp
        update_progress(30, "GUI modules loaded.")

        # 2️⃣ Initializing OCR engine
        update_progress(40, "Initializing OCR engine...")
        from core.ocr_engine import OCREngine
        ocr_engine = OCREngine()
        update_progress(60, "OCR engine ready.")

        # 3️⃣ Initializing PDF generator
        update_progress(65, "Initializing PDF generator...")
        from core.pdf_generator import PDFGenerator
        pdf_generator = PDFGenerator()
        update_progress(80, "PDF generator ready.")

        # 4️⃣ Setting up main window and camera
        update_progress(85, "Setting up main window...")
        window = DocCamApp()
        window.ocr_engine = ocr_engine
        window.pdf_generator = pdf_generator
        update_progress(95, "Main window ready.")

        # 5️⃣ Show main window
        window.show()
        update_progress(100, "Application ready!")
        QTimer.singleShot(500, splash.close if splash else lambda: None)

        logger.info("Application started successfully")
        return app.exec()

    except Exception as e:
        logger.critical(f"Application failed to start: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
