import re

# from app.utils.filter_text import replace_special_chars


# Extract Aadhaar FRONT side
def extract_front_aadhaar(text):
    # init variables
    splitted_text = []
    aadhaar_no = None
    name = None
    dob = None
    gender = None

    for txt in text.split("new_line"):
        txt = txt.strip()
        if txt:
            splitted_text.append(txt)

    # Date of Birth and Name
    if dob is None:
        dob_match = re.search("[0-9]{2}/[0-9]{2}/[0-9]{2,4}", text)
        if dob_match:
            # DOB
            dob = dob_match.group(0)
            # Name
            if dob:
                dob_index = next(
                    (i for i, s in enumerate(splitted_text) if dob in s), -1
                )
                name_match = re.search("[A-Za-z ]{2,}", splitted_text[dob_index - 1])
                if name_match:
                    name = name_match.group(0).strip()

    # Aadhaar Number
    if aadhaar_no is None:
        aadhaar_no_match = re.search("[0-9]{4} [0-9]{4} [0-9]{4}", text)
        if aadhaar_no_match:
            aadhaar_no = aadhaar_no_match.group(0)
            #   TODO: Cross-verify: o/p -> split -> arr.len == 3 && arr[i].len == 4 && number

    # Gender
    if gender is None:
        gender_match = re.search("(male|female)", text.lower())
        if gender_match:
            gender = gender_match.group(0)

    output = {"name": name, "aadhaarNumber": aadhaar_no, "dob": dob, "gender": gender}

    return output


# Extract Aadhaar BACK side
def extract_aadhaar_back_data(text):
    # init variables
    splitted_text = []
    address = None
    pincode = None

    for txt in text.split("new_line"):
        txt = txt.strip()
        if txt:
            splitted_text.append(txt)

    if address is None:
        startIndx = None
        endIndx = None
        for item in splitted_text:
            pincode_match = re.search("[0-9]{6}", item)
            if pincode_match:
                endIndx = splitted_text.index(item)
                pincode = pincode_match.group(0)

            if "Address" in item:
                startIndx = splitted_text.index(item)

        address = splitted_text[startIndx : endIndx + 1]
        if address:
            address = " ".join(address)
            indx = address.find("Address")
            address = address.replace("Address", "")
            address = address.replace(":", "")
            address = address.replace("-", "")
            # address = replace_special_chars(address, "")
            address = address.replace(pincode, "")
            address = address[indx:]

        return {"address": address.strip(), "pincode": pincode}
