import os
if os.path.exists("path_to_your_model/shape_predictor_68_face_landmarks.dat"):
    print("Model file found!")
else:
    print("Model file not found!")
