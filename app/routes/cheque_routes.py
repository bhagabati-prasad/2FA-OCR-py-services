from flask import Blueprint, request, jsonify
import traceback
import logging
from app.services.cheque.cheque_scan_service import scan_cheque

# Create Blueprint for Biometric Authentication routes
cheque_scan_blueprint = Blueprint("cheque_scan", __name__)

# Logger for document APIs
cheque_logger = logging.getLogger("cheque_logger")


"""
# Scan Cheque:
Route [POST]: /api/cheque/scan
Payload Field: file [.img]
"""


@cheque_scan_blueprint.route("/scan", methods=["POST"])
def scan_cheque_route():
    try:
        if request.method != "POST":
            return jsonify({"status": 405, "error": "Method not allowed."}), 405

        file = request.files["file"]
        if file:
            allowed_files = ["jpg", "png", "JPEG", "jpeg", "tif"]
            if file.filename.split(".")[-1] not in allowed_files:
                cheque_logger.info("File type is not allowed")
                return (
                    jsonify(
                        {
                            "status": False,
                            "error": "File type is not allowed. It must be in jpg, png, or JPEG format.",
                        }
                    ),
                    400,
                )

            results_arr = scan_cheque(file)
            cheque_logger.info("Successfully scanned the cheque.")
            return jsonify({"status": True, "data": results_arr}), 200

        else:
            cheque_logger.info("Failed to upload file. Please try again")
            return (
                jsonify(
                    {
                        "status": False,
                        "error": True,
                        "message": "Failed to upload file. Please try again.",
                    }
                ),
                500,
            )
    except TimeoutError:
        cheque_logger.info(
            "Processing timed out. Please try again with a clearer image."
        )
        return (
            jsonify(
                {
                    "status": False,
                    "error": True,
                    "message": "Processing timed out. Please try again with a clearer image.",
                }
            ),
            500,
        )

    except Exception as e:
        cheque_logger.info(
            "Unable to read the cheque. Please upload clear image again.",
        )
        traceback.print_exc()
        return (
            jsonify(
                {
                    "status": False,
                    "error": "Something went wrong",
                    "message": "Unable to read the cheque. Please upload clear image again.",
                }
            ),
            500,
        )
