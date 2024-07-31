import re


# Extract PAN data
def extract_pan(text):
    # init variables
    splitted_text = []
    pan_no_index = None
    pan_no = None
    name = None
    dob = None

    for txt in text.split("new_line"):
        txt = txt.strip()
        if txt:
            splitted_text.append(txt)

    # Date of Birth
    dob_match = re.search("[0-9]{2}/[0-9]{2}/[0-9]{2,4}", text)
    if dob_match:
        dob = dob_match.group(0)

    for str in splitted_text:
        # PAN Number
        pan_no_match = re.search("[A-Za-z]{5}[0-9]{4}[A-Za-z]{1}", text)
        if pan_no_match:
            pan_no = pan_no_match.group(0)
            if pan_no in str:
                pan_no_index = splitted_text.index(str)

        curr_indx = splitted_text.index(str)
        if pan_no and pan_no_index is not None and curr_indx > pan_no_index:
            # Name
            if "name" in str.lower():
                name_index = splitted_text.index(str)
                guessed_name = splitted_text[name_index + 1]
                extract_only_upper_match = re.search("[A-Z ]+", guessed_name)

                if extract_only_upper_match and name is None:
                    name = extract_only_upper_match.group(0)
            elif str.isupper() and name is None:
                name = str

    response = {"panNumber": pan_no, "name": name, "dob": dob}

    return response
