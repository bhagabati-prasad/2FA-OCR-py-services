import cv2
import numpy as np


def get_fingerprint_match_score(incoming_img, registered_img):
    # convert string data to numpy array
    file_bytes = np.frombuffer(incoming_img, np.uint8)
    # convert numpy array to image
    incoming_image = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)

    # convert string data to numpy array
    file_bytes_registered = np.frombuffer(registered_img, np.uint8)
    # convert numpy array to image
    registered_image = cv2.imdecode(file_bytes_registered, cv2.IMREAD_UNCHANGED)

    detector = cv2.SIFT_create()

    kp1, des1 = detector.detectAndCompute(incoming_image, None)
    kp2, des2 = detector.detectAndCompute(registered_image, None)

    bf = cv2.FlannBasedMatcher()
    matches = bf.knnMatch(des1, des2, k=2)

    good_matches = []

    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good_matches.append(m)

    score = (len(good_matches) / len(kp1)) * 100

    result = cv2.drawMatches(
        incoming_image, kp1, registered_image, kp2, good_matches, None, flags=2
    )

    return [score, result]
