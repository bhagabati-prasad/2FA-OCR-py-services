import numpy as np
import cv2


def process_img(image_file):
    if image_file:
        # Read the file as a binary stream
        file_bytes = np.frombuffer(image_file.read(), np.uint8)

        # Decode the image
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # Grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Gaussian blur
        blur = cv2.GaussianBlur(gray, (3, 3), 0)

        # Otsu's threshold
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # Morph open to remove noise and invert image
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
        invert = 255 - opening

        return {
            "image": image,
            "gray": gray,
            "blur": blur,
            "thresh": thresh,
            "invert": invert,
        }
