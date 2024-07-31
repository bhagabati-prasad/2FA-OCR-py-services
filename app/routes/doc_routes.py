from flask import Blueprint, request, jsonify
import traceback
import logging
import os
import tempfile
from app.utils.process_img import process_img
from app.utils.doc_scanner import doc_scanner
from app.utils.image_to_text import image_to_text
from app.services.docs.aadhaar_service import (
    extract_front_aadhaar,
    extract_aadhaar_back_data,
)
from app.services.docs.pan_service import extract_pan
from app.services.docs.passport_service import (
    extract_passport_front_data,
    extract_passport_back_data,
)
from app.services.docs.payslip_service import get_payslip_info
from app.services.docs.vehicle_quotation_service import extract_vehicle_details
from app.services.docs.account_statement_service import (
    extract_basic_info,
    get_daily_transactions,
    filter_monthly_expenses,
)

# Create Blueprint for Document scanner routes
doc_blueprint = Blueprint("document", __name__)

# Logger for document APIs
docs_logger = logging.getLogger("docs_logger")

"""
# Aadhaar front extract:
Route [POST]: /api/doc/extract/aadhaar-front
Payload Field: file [.img]
"""


@doc_blueprint.route("/extract/aadhaar-front", methods=["POST"])
def aadhaar_front_route():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 204

        pdf_file = request.files["file"]

        if pdf_file:
            processed_img = process_img(pdf_file)
            # Perform text extraction
            data = doc_scanner(processed_img["thresh"])
            text = data.replace("\n", " new_line ")

            aadhaar_data = extract_front_aadhaar(text)

            if (
                aadhaar_data["name"] == None
                or aadhaar_data["aadhaarNumber"] == None
                or aadhaar_data["dob"] == None
                or aadhaar_data["gender"] == None
            ):
                data = doc_scanner(processed_img["gray"])
                text = data.replace("\n", " new_line ")

                aadhaar_data = extract_front_aadhaar(text)

            docs_logger.info("Extracting Aadhaar FRONT details.")

            return jsonify({"status": True, "data": aadhaar_data}), 200

    except Exception as e:
        docs_logger.exception(
            "Error occurred while extracting Aadhaar Card FRONT side."
        )
        traceback.print_exc()
        return (
            jsonify(
                {"status": False, "error": "Something went wrong", "message": str(e)}
            ),
            500,
        )


"""
# Aadhaar back extract:
Route [POST]: /api/doc/extract/aadhaar-back
Payload Field: file [.img]
"""


@doc_blueprint.route("/extract/aadhaar-back", methods=["POST"])
def aadhaar_back_route():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 204

        pdf_file = request.files["file"]

        if pdf_file:
            processed_img = process_img(pdf_file)
            # Perform text extraction
            data = doc_scanner(processed_img["gray"])
            text = data.replace("\n", " new_line ")

            aadhaar_data = extract_aadhaar_back_data(text)

            docs_logger.info("Extracting Aadhaar BACK details.")

            return jsonify({"status": True, "data": aadhaar_data}), 200

    except Exception as e:
        docs_logger.exception("Error occurred while extracting Aadhaar Card BACK side.")
        traceback.print_exc()
        return (
            jsonify(
                {"status": False, "error": "Something went wrong", "message": str(e)}
            ),
            500,
        )


"""
# PAN extract:
Route [POST]: /api/doc/extract/pan
Payload Field: file [.img]
"""


@doc_blueprint.route("/extract/pan", methods=["POST"])
def pan_route():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 204

        pdf_file = request.files["file"]

        if pdf_file:
            processed_img = process_img(pdf_file)
            # Perform text extraction
            data = doc_scanner(processed_img["gray"])
            text = data.replace("\n", " new_line ")

            pan_data = extract_pan(text)

            docs_logger.info("Extracting PAN details.")

            return jsonify({"status": True, "data": pan_data}), 200

    except Exception as e:
        docs_logger.exception("Error occurred while extracting PAN Card.")
        traceback.print_exc()
        return (
            jsonify(
                {"status": False, "error": "Something went wrong", "message": str(e)}
            ),
            500,
        )


"""
# Passport Front extract:
Route [POST]: /api/doc/extract/passport-front
Payload Field: file [.img]
"""


@doc_blueprint.route("/extract/passport-front", methods=["POST"])
def passport_front_route():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 204

        pdf_file = request.files["file"]

        if pdf_file:
            passport_data = extract_passport_front_data(pdf_file)

            docs_logger.info("Extracting Passport Front details.")

            return jsonify({"status": True, "data": passport_data}), 200

    except Exception as e:
        docs_logger.exception("Error occurred while extracting Passport.")
        traceback.print_exc()
        return (
            jsonify(
                {"status": False, "error": "Something went wrong", "message": str(e)}
            ),
            500,
        )


"""
# Passport Back extract:
Route [POST]: /api/doc/extract/passport-back
Payload Field: file [.img]
"""


@doc_blueprint.route("/extract/passport-back", methods=["POST"])
def passport_back_route():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 204

        pdf_file = request.files["file"]

        if pdf_file:
            passport_data = extract_passport_back_data(pdf_file)

            docs_logger.info("Extracting Passport Back details.")

            return jsonify({"status": True, "data": passport_data}), 200

    except Exception as e:
        docs_logger.exception("Error occurred while extracting Passport.")
        traceback.print_exc()
        return (
            jsonify(
                {"status": False, "error": "Something went wrong", "message": str(e)}
            ),
            500,
        )


"""
# Payslip extract:
Route [POST]: /api/doc/extract/payslip
Payload Field: file [.pdf]
"""


@doc_blueprint.route("/extract/payslip", methods=["POST"])
def payslip_route():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 204

        pdf_file = request.files["file"]

        if pdf_file.filename == "":
            return jsonify({"error": "No selected file"})

        if pdf_file:
            payslip_data = get_payslip_info(pdf_file)

            docs_logger.info("Extracting payslip details.")

            return jsonify(payslip_data), 200

    except Exception:
        docs_logger.exception("Error occurred while extracting Payslip.")
        traceback.print_exc()
        return jsonify({"error": "Something went wrong", "message": Exception}), 500


"""
# Vehicle Quotation extract:
Route [POST]: /api/doc/extract/vehicle-quotation
Payload Field: file [.pdf]
"""


@doc_blueprint.route("/extract/vehicle-quotation", methods=["POST"])
def vehicle_quotation_route():
    # temp_file_path = None
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 204
        pdf_file = request.files["file"]
        if pdf_file.filename == "":
            return jsonify({"error": "No selected file"})
        if pdf_file:
            vehicle_data = extract_vehicle_details(pdf_file)

            docs_logger.info("Extracting vehicle quotation details.")

            return jsonify({"vehicleData": vehicle_data}), 200

    except Exception as e:
        docs_logger.exception("Error occurred while extracting Vehicle Quotation.")
        traceback.print_exc()
        return jsonify({"error": "Something went wrong", "message": str(e)}), 500


"""
# Account Statement extract:
Route [POST]: /api/doc/extract/account-statement
Payload Field: file [.pdf]
"""


@doc_blueprint.route("/extract/account-statement", methods=["POST"])
def account_statement_route():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 204
        pdf_file = request.files["file"]
        if pdf_file.filename == "":
            return jsonify({"error": "No selected file"})
        if pdf_file:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file_path = temp_file.name
                pdf_file.save(temp_file)
                temp_file.close()
                extracted_data = image_to_text(temp_file_path)
                # Filtering Data
                basic_info = extract_basic_info(extracted_data)
                daily_transactions = get_daily_transactions(extracted_data)
                monthly_expenses, total_debit, total_credit = (
                    filter_monthly_expenses(daily_transactions)
                    if len(daily_transactions)
                    else []
                )

                os.unlink(temp_file_path)

            docs_logger.info("Extracting account statement details.")

            return (
                jsonify(
                    {
                        "basicInfo": basic_info,
                        "monthlyExpenses": monthly_expenses,
                        "dailyTransactions": daily_transactions,
                        "totalDebit": total_debit,
                        "totalCredit": total_credit,
                    }
                ),
                200,
            )

    except Exception:
        docs_logger.exception("Error occurred while extracting Account Statement.")
        traceback.print_exc()
        return jsonify({"error": "Something went wrong", "message": Exception}), 500
