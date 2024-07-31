import cv2
import pytesseract
import re
from datetime import datetime
import numpy as np

today = datetime.today()


def __preprocess_passport_image(image):
    # Read the file as a binary stream
    file_bytes = np.frombuffer(image.read(), np.uint8)
    # Decode the image
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    inverted = cv2.bitwise_not(thresh)

    return gray, blur, thresh, inverted


def __extract_passport_front(image, psm):
    # Initialize variables
    splitted_text = []
    passport_no = None
    name = None
    dob = None
    surname = None
    place_of_birth = None
    expiry_date = None

    passport_no_index = None
    name_indx = None
    birth_place_indx = None

    # Apply Tesseract OCR with the given PSM mode
    custom_config = f"--psm {psm}"
    data = pytesseract.image_to_string(image, config=custom_config)

    text = data.replace("\n", " new_line ")

    for txt in text.split("new_line"):
        txt = txt.strip()
        if txt:
            splitted_text.append(txt)

    # Extract the necessary information (example logic)
    for current_index, data in enumerate(splitted_text):
        if passport_no == None:
            passpost_no_match = re.search("[A-Z][0-9]{6}[1-9]", data)
            if passpost_no_match:
                passport_no_index = current_index
                passport_no = passpost_no_match.group(0)
            else:
                passpost_no_match2 = re.search("[A-Z][ ]{1}[0-9]{6}[1-9]", data)
                if passpost_no_match2:
                    passport_no_index = current_index
                    passport_no = passpost_no_match2.group(0)
                    passport_no = "".join(passport_no.split(" "))

        if "Given" in data and "Name" in data:
            name_indx = current_index
            surname_match = re.search("[A-Z]{3,}", splitted_text[name_indx - 1])
            if surname_match:
                if surname == None:
                    surname = surname_match.group(0)
            name_match = re.search("[A-Z ]{3,}", splitted_text[name_indx + 1])
            if name_match:
                if name == None:
                    name = name_match.group(0)
            else:
                name_match2 = re.search("[A-Z ]{3,}", splitted_text[name_indx + 2])
                if name_match2:
                    if name == None:
                        name = name_match2.group(0)

        if place_of_birth == None:
            if "Place" in data or "Birth" in data:
                birth_place_indx = current_index
                birth_place_splitted = splitted_text[birth_place_indx + 1].split(" ")
                birth_place_selected = ""
                for place in birth_place_splitted:
                    if place.isupper():
                        birth_place_selected += place

                place_of_birth = birth_place_selected
                birth_place_match = re.search(
                    "[A-Z ,]{3,}", splitted_text[birth_place_indx + 1]
                )
                if birth_place_match:
                    if place_of_birth == None:
                        place_of_birth = birth_place_match.group(0)

        if expiry_date == None and birth_place_indx != None:
            dates_found = re.findall("[0-9]{2}/[0-9]{2}/[0-9]{4}", data)
            if dates_found:
                expiry_date = dates_found[0] if len(dates_found) > 1 else None

    if name_indx and birth_place_indx:
        for data in splitted_text[name_indx:birth_place_indx]:
            dob_match = re.search("[0-9]{2}/[0-9]{2}/[0-9]{4}", data)
            if dob_match:
                dob = dob_match.group(0)
                dob_splitted = dob.split("/")
                if (
                    int(dob_splitted[0]) > 31
                    or int(dob_splitted[1]) > 12
                    or int(dob_splitted[2]) > today.year
                ):
                    dob = None

    return {
        "passportNo": passport_no,
        "name": name,
        "dob": dob,
        "surname": surname,
        "placeOfBirth": place_of_birth,
        "expiryDate": expiry_date,
    }


def extract_passport_front_data(image):
    processed_images = __preprocess_passport_image(image)
    psms = [4, 6]
    result = None

    for img_indx, image in enumerate(processed_images):
        for psm_indx, psm in enumerate(psms):
            # result = __extract_passport_front(img, psm)

            # Initialize variables
            splitted_text = []
            passport_no = None
            name = None
            dob = None
            surname = None
            place_of_birth = None
            expiry_date = None

            passport_no_index = None
            name_indx = None
            birth_place_indx = None

            # Apply Tesseract OCR with the given PSM mode
            custom_config = f"--psm {psm}"
            data = pytesseract.image_to_string(image, config=custom_config)

            text = data.replace("\n", " new_line ")

            for txt in text.split("new_line"):
                txt = txt.strip()
                if txt:
                    splitted_text.append(txt)

            # Extract the necessary information (example logic)
            for current_index, data in enumerate(splitted_text):
                if passport_no == None:
                    passpost_no_match = re.search("[A-Z][0-9]{6}[1-9]", data)
                    if passpost_no_match:
                        passport_no_index = current_index
                        passport_no = passpost_no_match.group(0)
                    else:
                        passpost_no_match2 = re.search("[A-Z][ ]{1}[0-9]{6}[1-9]", data)
                        if passpost_no_match2:
                            passport_no_index = current_index
                            passport_no = passpost_no_match2.group(0)
                            passport_no = "".join(passport_no.split(" "))

                if "Given" in data and "Name" in data:
                    name_indx = current_index
                    surname_match = re.search("[A-Z]{3,}", splitted_text[name_indx - 1])
                    if surname_match:
                        if surname == None:
                            surname = surname_match.group(0)
                    name_match = re.search("[A-Z ]{3,}", splitted_text[name_indx + 1])
                    if name_match:
                        if name == None:
                            name = name_match.group(0)
                    else:
                        name_match2 = re.search(
                            "[A-Z ]{3,}", splitted_text[name_indx + 2]
                        )
                        if name_match2:
                            if name == None:
                                name = name_match2.group(0)

                if place_of_birth == None:
                    if "Place" in data or "Birth" in data:
                        birth_place_indx = current_index
                        birth_place_splitted = splitted_text[
                            birth_place_indx + 1
                        ].split(" ")
                        birth_place_selected = ""
                        for place in birth_place_splitted:
                            if place.isupper():
                                birth_place_selected += place

                        place_of_birth = birth_place_selected
                        birth_place_match = re.search(
                            "[A-Z ,]{3,}", splitted_text[birth_place_indx + 1]
                        )
                        if birth_place_match:
                            if place_of_birth == None:
                                place_of_birth = birth_place_match.group(0)

                if expiry_date == None and birth_place_indx != None:
                    dates_found = re.findall("[0-9]{2}/[0-9]{2}/[0-9]{4}", data)
                    if dates_found:
                        expiry_date = dates_found[0] if len(dates_found) > 1 else None

            if dob == None and name_indx and birth_place_indx:
                for data in splitted_text[name_indx:birth_place_indx]:
                    dob_match = re.search("[0-9]{2}/[0-9]{2}/[0-9]{4}", data)
                    if dob_match:
                        dob = dob_match.group(0)
                        dob_splitted = dob.split("/")
                        if (
                            int(dob_splitted[0]) > 31
                            or int(dob_splitted[1]) > 12
                            or int(dob_splitted[2]) > today.year
                        ):
                            dob = None

            result = {
                "passportNo": passport_no,
                "name": name,
                "dob": dob,
                "surname": surname,
                "placeOfBirth": place_of_birth,
                "expiryDate": expiry_date,
            }

    return result
    # if img_indx == len(processed_images) - 1 and psm_indx == len(psms) - 1:


# ------ Back side of passport -------


def __extract_passport_back(image, psm):
    # init variables
    splitted_text = []
    passport_no = None
    father_name = ""
    mother_name = ""
    address = ""
    pincode = None
    # variables for keeping index of values
    father_name_index = None
    mother_name_index = None
    address_index = None
    pincode_index = None

    # Apply Tesseract OCR with the given PSM mode
    custom_config = f"--psm {psm}"
    data = pytesseract.image_to_string(image, config=custom_config)
    text = data.replace("\n", " new_line ")

    for txt in text.split("new_line"):
        txt = txt.strip()
        if txt:
            splitted_text.append(txt)

    for current_index, data in enumerate(splitted_text):
        # if passport_no == None:
        #     passpost_no_match = re.search("[A-Z][0-9]{6}[1-9]", data)
        #     if passpost_no_match:
        #         passport_no_index = current_index
        #         passport_no = passpost_no_match.group(0)
        #     else:
        #         passpost_no_match2 = re.search("[A-Z][ ]{1}[0-9]{6}[1-9]", data)
        #         if passpost_no_match2:
        #             passport_no_index = current_index
        #             passport_no = passpost_no_match2.group(0)
        #             passport_no = "".join(passport_no.split(" "))

        if not father_name:
            if "Father" in data:
                father_name_index = current_index + 1
                father_name_line_splitted = splitted_text[current_index + 1].split(" ")
                for word in father_name_line_splitted:
                    father_name += " " + word if word.isupper() else ""

        if not mother_name:
            if "Mother" in data:
                mother_name_index = current_index + 1
                mother_name_line_splitted = splitted_text[current_index + 1].split(" ")
                for word in mother_name_line_splitted:
                    mother_name += " " + word if word.isupper() else ""
            else:
                if father_name_index:
                    mother_name_line_splitted = splitted_text[
                        father_name_index + 2
                    ].split(" ")
                    for word in mother_name_line_splitted:
                        mother_name += " " + word if word.isupper() else ""

        if pincode == None:
            if "PIN" in data:
                pincode_match = re.search("[0-9]{6}", data)
                if pincode_match:
                    pincode_index = current_index
                    pincode = pincode_match.group(0)

        if address_index == None:
            if "Address" in data:
                address_index = current_index + 1

    if not address and address_index and pincode_index:
        address_array = splitted_text[address_index : pincode_index + 1]
        for parts in address_array:
            parts_splitted = parts.split(" ")
            if "PIN" in parts:
                continue
            for word in parts_splitted:
                address += " " + word if word.isupper() else ""

    output = {
        "passportNo": passport_no,
        "fatherName": father_name.strip(),
        "motherName": mother_name.strip(),
        "address": address,
        "pincode": pincode,
    }
    return output


def extract_passport_back_data(image):
    # Read the file as a binary stream
    file_bytes = np.frombuffer(image.read(), np.uint8)
    # Decode the image
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    result = __extract_passport_back(gray, 6)
    return result

    # processed_images = __preprocess_passport_image(image)

    # for img_indx, image in enumerate(processed_images):
    #     # result = __extract_passport_back(img, 6)

    #     # init variables
    #     splitted_text = []
    #     passport_no = None
    #     father_name = ""
    #     mother_name = ""
    #     address = ""
    #     pincode = None
    #     # variables for keeping index of values
    #     father_name_index = None
    #     mother_name_index = None
    #     address_index = None
    #     pincode_index = None

    #     # Apply Tesseract OCR with the given PSM mode
    #     custom_config = f"--psm 6"
    #     data = pytesseract.image_to_string(image, config=custom_config)
    #     text = data.replace("\n", " new_line ")

    #     for txt in text.split("new_line"):
    #         txt = txt.strip()
    #         if txt:
    #             splitted_text.append(txt)

    #     for current_index, data in enumerate(splitted_text):
    #         # if passport_no == None:
    #         #     passpost_no_match = re.search("[A-Z][0-9]{6}[1-9]", data)
    #         #     if passpost_no_match:
    #         #         passport_no_index = current_index
    #         #         passport_no = passpost_no_match.group(0)
    #         #     else:
    #         #         passpost_no_match2 = re.search("[A-Z][ ]{1}[0-9]{6}[1-9]", data)
    #         #         if passpost_no_match2:
    #         #             passport_no_index = current_index
    #         #             passport_no = passpost_no_match2.group(0)
    #         #             passport_no = "".join(passport_no.split(" "))

    #         if not father_name:
    #             if "Father" in data:
    #                 father_name_index = current_index + 1
    #                 father_name_line_splitted = splitted_text[current_index + 1].split(
    #                     " "
    #                 )
    #                 for word in father_name_line_splitted:
    #                     father_name += " " + word if word.isupper() else ""

    #         if not mother_name:
    #             if "Mother" in data:
    #                 mother_name_index = current_index + 1
    #                 mother_name_line_splitted = splitted_text[current_index + 1].split(
    #                     " "
    #                 )
    #                 for word in mother_name_line_splitted:
    #                     mother_name += " " + word if word.isupper() else ""
    #             else:
    #                 if father_name_index:
    #                     mother_name_line_splitted = splitted_text[
    #                         father_name_index + 2
    #                     ].split(" ")
    #                     for word in mother_name_line_splitted:
    #                         mother_name += " " + word if word.isupper() else ""

    #         if pincode == None:
    #             if "PIN" in data:
    #                 pincode_match = re.search("[0-9]{6}", data)
    #                 if pincode_match:
    #                     pincode_index = current_index
    #                     pincode = pincode_match.group(0)

    #         if address_index == None:
    #             if "Address" in data:
    #                 address_index = current_index + 1

    #     if not address and address_index and pincode_index:
    #         address_array = splitted_text[address_index : pincode_index + 1]
    #         for parts in address_array:
    #             parts_splitted = parts.split(" ")
    #             if "PIN" in parts:
    #                 continue
    #             for word in parts_splitted:
    #                 address += " " + word if word.isupper() else ""

    #     result = {
    #         "passportNo": passport_no,
    #         "fatherName": father_name.strip(),
    #         "motherName": mother_name.strip(),
    #         "address": address,
    #         "pincode": pincode,
    #     }

    #     return result
    #     # if img_indx == len(processed_images) - 1:
