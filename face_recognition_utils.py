import face_recognition
import json
import os
import numpy as np

DB_PATH = "assets/known_faces.json"

def load_known_faces():
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r") as f:
            data = json.load(f)
            faces = {}
            for name, embedding in data.items():
                try:
                    # Ensure the embedding is a valid numeric array
                    faces[name] = np.array(embedding, dtype=np.float64)
                except ValueError as e:
                    print(f"Error processing embedding for {name}: {e}")
            return faces
    return {}

def save_known_faces(data):
    serializable = {name: embedding.tolist() for name, embedding in data.items()}
    with open(DB_PATH, "w") as f:
        json.dump(serializable, f)

def get_face_embedding(frame):
    rgb = frame[:, :, ::-1]
    locations = face_recognition.face_locations(rgb)
    if locations:
        encoding = face_recognition.face_encodings(rgb, locations)
        if encoding:
            print(f"Generated face embedding: {encoding[0].shape}")  # This should print (128,)
            return encoding[0], locations[0]  # First face only
    return None, None


def match_face(embedding, known_faces, tolerance=0.5):
    for name, known_embedding in known_faces.items():
        # Calculate Euclidean distance between the face embeddings
        distance = np.linalg.norm(embedding - known_embedding)
        if distance < tolerance:
            return name  # Match found
    return "Unknown"  # No match found

def recognize_face(frame, known_faces, tolerance=0.5):
    embedding, _ = get_face_embedding(frame)
    if embedding is not None:
        return match_face(embedding, known_faces, tolerance)
    return None

# def load_known_faces():
#     if os.path.exists(KNOWN_FACES_FILE):
#         with open(KNOWN_FACES_FILE, "r") as f:
#             return json.load(f)
#     return {}

# Example of using the functions
if __name__ == "__main__":
    # Load known faces from the database
    known_faces = load_known_faces()
    print(f"Loaded known faces: {known_faces}")

    # Simulating a frame with a detected face (this should be replaced with actual frame data)
    frame = np.random.rand(480, 640, 3)  # Example random frame
    embedding, location = get_face_embedding(frame)

    if embedding is not None:
        # Match the detected face with the known faces
        name = match_face(embedding, known_faces)
        print(f"Detected face: {name}")
    else:
        print("No face detected in the frame.")
