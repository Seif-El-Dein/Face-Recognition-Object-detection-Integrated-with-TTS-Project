from ultralytics import YOLO
import cv2
import numpy as np
from tts_utils import speak

model = YOLO("yolov5n.pt")  # Or yolov8n.pt

spoken_items = set()

def detect_objects(frame):
    results = model(frame)
    labels = results[0].names
    detected = set()
    for result in results[0].boxes.data.tolist():
        x1, y1, x2, y2, conf, cls = result
        label = labels[int(cls)]
        detected.add(label)
    return list(detected)

def announce_objects(items):
    global spoken_items
    for item in items:
        if item not in spoken_items:
            speak(f"I see a {item}")
            spoken_items.add(item)
