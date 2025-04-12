from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit
from PySide6.QtCore import QTimer, QThread, Signal
from PySide6.QtGui import QImage, QPixmap
import cv2
import time
from threading import Thread, Lock
from face_recognition_utils import *
from object_detection_utils import detect_objects, announce_objects
from tts_utils import speak

class RecognitionThread(QThread):
    update_face = Signal(str)
    update_objects = Signal(list)

    def __init__(self, cap, known_faces):
        super().__init__()
        self.cap = cap
        self.known_faces = known_faces
        self.running = True
        self.last_greet_time = {}
        self.lock = Lock()

    def run(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            # Face recognition throttled to every 30 seconds per face
            name = recognize_face(frame, self.known_faces)
            now = time.time()
            if name:
                if name not in self.last_greet_time or (now - self.last_greet_time[name]) > 30:
                    self.last_greet_time[name] = now
                    self.update_face.emit(name)

            # Object detection
            objects = detect_objects(frame)
            if objects:
                self.update_objects.emit(objects)

            time.sleep(1)  # Keep it responsive, reduce CPU usage

    def stop(self):
        self.running = False
        self.quit()
        self.wait()


class FaceApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("InMoov Face & Object Recognition")
        self.image_label = QLabel()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter name for new face")
        self.capture_button = QPushButton("Capture & Register Face")
        self.capture_button.clicked.connect(self.register_face)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.capture_button)
        self.setLayout(layout)

        self.cap = cv2.VideoCapture(0)
        self.known_faces = load_known_faces()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.recognition_thread = RecognitionThread(self.cap, self.known_faces)
        self.recognition_thread.update_face.connect(self.greet_person)
        self.recognition_thread.update_objects.connect(self.announce_objects)
        self.recognition_thread.start()

    def register_face(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        embedding, _ = get_face_embedding(frame)
        if embedding is not None:
            name = self.name_input.text().strip()
            if name:
                self.known_faces[name] = embedding
                save_known_faces(self.known_faces)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(qt_image))

    def greet_person(self, name):
        if name in self.known_faces:
            speak(f"Hello {name}")

    def announce_objects(self, objects):
        announce_objects(objects)

    def closeEvent(self, event):
        self.recognition_thread.stop()
        self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication([])
    window = FaceApp()
    window.show()
    app.exec()
