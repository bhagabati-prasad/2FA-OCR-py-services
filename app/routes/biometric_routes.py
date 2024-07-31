from flask import Blueprint, request, jsonify
import traceback
import logging
import time
import os
from PIL import Image
import face_recognition
from app.services.biometrics.face_auth_service import encode_detected_face
from app.services.biometrics.fingerprint_auth_service import get_fingerprint_match_score
from app.services.biometrics.iris_auth_service import (
    get_iris_descriptors,
    hash_descriptors,
    matchIris,
    process_incoming_image,
)

# Create Blueprint for Biometric Authentication routes
biometric_auth_blueprint = Blueprint("biometric_auth", __name__)

# Logger for document APIs
biometric_logger = logging.getLogger("biometric_logger")


# Generate unique ID
def __generateUniqueId():
    return int(time.time() * 1000)


"""
# Encode Face:
Route [POST]: /api/auth/face/encode
Payload Field: file [.img]
"""


@biometric_auth_blueprint.route("/face/encode", methods=["POST"])
def encode_face():
    try:
        if "file" not in request.files:
            return "No file part"

        file = request.files["file"]

        if file.filename == "":
            return "No selected file"

        if file:
            [face_encodings, face_locations] = encode_detected_face(file)

        if not len(face_encodings):
            biometric_logger.info("No face detected.")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": True,
                        "message": "No face detected",
                        "user": None,
                    }
                ),
                400,
            )

        faceId_to_str = str(face_encodings)

        userInfo = {
            "biometric_type": "FACE",
            "face_id": faceId_to_str,
        }

        # Logging and response
        biometric_logger.info("Face encoded successfully.")
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Face encoded successfully",
                    "data": userInfo,
                }
            ),
            200,
        )

    except Exception as err:
        biometric_logger.exception("Error occurred while encoding face.")
        traceback.print_exc()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Something went wrong",
                    "message": str(err),
                    "user": None,
                }
            ),
            500,
        )


"""
# Match two faces:
Route [POST]: /api/auth/face/match
Payload Field: file: [.img], face_id: [string]
"""


@biometric_auth_blueprint.route("/face/match", methods=["POST"])
def match_faces():
    try:
        face_id_str = request.form.get("face_id")

        # Convert the string representation back to a list of NumPy arrays
        known_face_encodings = eval(face_id_str)

        if "file" not in request.files:
            return "No file part"

        file = request.files["file"]

        if file.filename == "":
            return "No selected file"
        if file:
            [face_encodings, face_locations] = encode_detected_face(file)

        # if known_face_encodings is not None:
        for (top, right, bottom, left), face_encoding in zip(
            face_locations, face_encodings
        ):
            matches = face_recognition.compare_faces(
                known_face_encodings, face_encoding
            )
            if True in matches:
                biometric_logger.info("Face matched successfully")
                return (
                    jsonify({"success": True, "message": "Face matched successfully"}),
                    200,
                )
            else:
                biometric_logger.error("Face did not match.")
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": True,
                            "message": "Face did not match",
                            "user": None,
                        }
                    ),
                    400,
                )

    except Exception as err:
        biometric_logger.info("Error in matching faces.")
        traceback.print_exc()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Something went wrong",
                    "message": str(err),
                    "user": None,
                }
            ),
            500,
        )


"""
# Encode Fingerprint:
Route [POST]: /api/auth/fingerprint/encode
Payload Field: file: [.img]
"""


@biometric_auth_blueprint.route("/fingerprint/encode", methods=["POST"])
def encode_fingerprint():
    try:
        # Ensure the request contains 'file' field
        if "file" not in request.files:
            return jsonify({"status": 400, "error": "No file part"}), 400

        file = request.files["file"]

        # Ensure the file is not empty
        if file.filename == "":
            return jsonify({"status": 400, "error": "No selected file"}), 400
        # create_subfolders()

        # Ensure the file type is allowed
        allowed_files = ["jpg", "png", "JPEG", "jpeg"]
        if file.filename.split(".")[-1] not in allowed_files:
            biometric_logger.info(
                "File type is not allowed. It must be in jpg, png, or JPEG format."
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "error": True,
                        "message": "File type is not allowed. It must be in jpg, png, or JPEG format.",
                    }
                ),
                400,
            )

        random_user_id = __generateUniqueId()

        im = Image.open(file)
        # Save the image
        filename = f"{random_user_id}_fingerprint{os.path.splitext(file.filename)[1]}"
        # im.save(os.path.join(app.config['FINGERPRINT_FOLDER'], filename))
        # im.save(os.path.join(fingerprint_folder_path, filename))

        userInfo = {
            "file_name": filename,
            "biometric_type": "FINGERPRINT",
        }

        biometric_logger.info("Successfully encoded fingerprint")
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Fingerprint encoded successfully",
                    "data": userInfo,
                }
            ),
            200,
        )

    except Exception as err:
        biometric_logger.info("Error in encoing fingerprint.")
        traceback.print_exc()
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Something went wrong",
                    "message": str(err),
                    "user": None,
                }
            ),
            500,
        )


"""
# Match two fingerprints:
Route [POST]: /api/auth/fingerprint/match
Payload Field: incoming_fingerprint: [File.img], registered_fingerprint: [File.img]
"""


@biometric_auth_blueprint.route("/fingerprint/match", methods=["POST"])
def match_fingerprints():
    try:
        # read incoming image file string data
        incoming_img = request.files["incoming_fingerprint"].read()

        # read registered image file string data from form-data
        registered_img = request.files["registered_fingerprint"].read()

        [score, result] = get_fingerprint_match_score(incoming_img, registered_img)

        if score > 10:
            biometric_logger.info("Fingerprint matched successfully")
            return (
                jsonify(
                    {"success": True, "message": "Fingerprint matched successfully"}
                ),
                200,
            )

        else:
            logging.info("Fingerprint did not match")
            return (
                jsonify(
                    {
                        "sussess": False,
                        "error": True,
                        "message": "Fingerprint did not match",
                    }
                ),
                400,
            )

    except Exception as err:
        biometric_logger.info("Error in matching fingerprint")
        traceback.print_exc()
        return (
            jsonify(
                {"success": False, "error": "Something went wrong", "message": str(err)}
            ),
            500,
        )


"""
# Encode Iris:
Route [POST]: /api/auth/iris/encode
Payload Field: file: [.img]
"""


@biometric_auth_blueprint.route("/iris/encode", methods=["POST"])
def encode_iris():
    try:
        file = request.files["file"]

        if file:
            [kp, des] = get_iris_descriptors(file)

        hash_des = hash_descriptors(des)

        userInfo = {
            "biometric_type": "IRIS",
            "iris_id": hash_des,
        }

        biometric_logger.info("Successfully encoded iris")
        return (
            jsonify(
                {
                    "sussess": True,
                    "message": "Iris encoded successfully",
                    "data": userInfo,
                }
            ),
            200,
        )

    except Exception as err:
        biometric_logger.info("Error in encoding Iris.")
        traceback.print_exc()
        return (
            jsonify(
                {
                    "sussess": False,
                    "error": "Something went wrong",
                    "message": str(err),
                }
            ),
            500,
        )


"""
# Match Iris:
Route [POST]: /api/auth/iris/match
Payload Field: file: [.img]
"""


@biometric_auth_blueprint.route("/iris/match", methods=["POST"])
def match_iris():
    try:
        file = request.files["file"]
        incoming_image = process_incoming_image(file)
        hash_des_input = request.form.get("iris_id")  # Update this line

        if matchIris(incoming_image, hash_des_input):
            biometric_logger.info("Iris matched successfully.")
            return (
                jsonify({"status": "success", "message": "Iris matched successfully"}),
                200,
            )
        else:
            biometric_logger.info("Iris did not match")
            return jsonify({"status": "failed", "message": "iris did not match"}), 400

    except Exception as err:
        biometric_logger.info("error in matching Iris")
        traceback.print_exc()
        return (
            jsonify(
                {"status": False, "error": "Something went wrong", "message": str(err)}
            ),
            500,
        )
