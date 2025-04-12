from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit
from PySide6.QtCore import QTimer
from PySide6.QtGui import QImage, QPixmap
import cv2
from face_recognition_utils import *
from object_detection_utils import detect_objects, announce_objects
from tts_utils import speak

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

    def register_face(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        embedding, loc = get_face_embedding(frame)
        if embedding is not None:
            name = self.name_input.text().strip()
            if name:
                self.known_faces[name] = embedding
                save_known_faces(self.known_faces)
                speak(f"Face registered for {name}")

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        embedding, loc = get_face_embedding(frame)
        if embedding is not None:
            name = match_face(embedding, self.known_faces)
            top, right, bottom, left = loc
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            if name != "Unknown":
                speak(f"Hello, {name}")

        # Object detection
        objects = detect_objects(frame)
        announce_objects(objects)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        img = QImage(rgb_frame.data, w, h, ch * w, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(img))

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication([])
    win = FaceApp()
    win.show()
    app.exec()
