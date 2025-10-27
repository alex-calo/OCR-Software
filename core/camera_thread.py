import cv2
from PyQt5.QtCore import QThread, pyqtSignal
import logging

logger = logging.getLogger(__name__)

class CameraThread(QThread):
    frame_ready = pyqtSignal(object)  # Emits captured frame (np.ndarray)
    error = pyqtSignal(str)           # Emits error messages

    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self._running = False
        self.cap = None

    def run(self):
        """Thread loop to capture frames from the camera."""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                self.error.emit(f"Cannot open camera {self.camera_index}")
                return
            self._running = True
            while self._running:
                ret, frame = self.cap.read()
                if not ret:
                    self.error.emit(f"Failed to read frame from camera {self.camera_index}")
                    break
                self.frame_ready.emit(frame)
                self.msleep(30)  # ~30 FPS
        except Exception as e:
            self.error.emit(str(e))
        finally:
            if self.cap:
                self.cap.release()
            logger.info(f"Camera {self.camera_index} thread stopped.")

    def stop(self):
        """Stop the camera thread safely."""
        self._running = False
        self.wait()

    def switch_camera(self, new_index):
        """
        Switch to a different camera device.
        Stops the current capture and restarts with the new index.
        """
        logger.info(f"Switching camera from {self.camera_index} to {new_index}")
        self.stop()
        self.camera_index = new_index
        self.start()
