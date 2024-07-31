from PIL import Image
import numpy as np
import face_recognition


def encode_detected_face(file):
    image = Image.open(file)
    image = image.convert("RGB")

    image_np = np.array(image)

    face_locations = face_recognition.face_locations(image_np)
    face_encodings = face_recognition.face_encodings(image_np, face_locations)

    return [face_encodings, face_locations]
