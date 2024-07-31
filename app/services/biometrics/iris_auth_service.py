import cv2
import numpy as np
import hashlib


def __compute_keypoints_and_descriptors(image):
    detector = cv2.SIFT_create()
    kp, des = detector.detectAndCompute(image, None)
    return kp, des


def hash_descriptors(descriptors):
    # Convert descriptors to a string and then calculate its hash
    return hashlib.sha256(str(descriptors).encode()).hexdigest()


def get_iris_descriptors(file):
    im_bytes = file.read()
    incoming_image = cv2.imdecode(
        np.frombuffer(im_bytes, np.uint8), cv2.IMREAD_UNCHANGED
    )
    kp, des = __compute_keypoints_and_descriptors(incoming_image)

    return [kp, des]


def process_incoming_image(file):
    im_bytes = file.read()
    incoming_image = cv2.imdecode(
        np.frombuffer(im_bytes, np.uint8), cv2.IMREAD_UNCHANGED
    )
    return incoming_image


def matchIris(incoming_image, hash_des_input):
    detector = cv2.SIFT_create()
    kp, des = detector.detectAndCompute(incoming_image, None)

    hash_des = hash_descriptors(des)

    # Compare hash values
    return hash_des == hash_des_input
