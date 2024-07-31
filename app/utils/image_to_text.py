import re
from PyPDF2 import PdfReader


# Trim 'spaces' from both side of the string and remove 'Nul' values.
# @Scope: Private
def __clean_text(text):
    # Replace 'Nul' and any non-printable characters with a space
    cleaned_text = re.sub(
        r"[\x00-\x1F\x7F-\x9F]", "", text
    )  # Removes control characters
    cleaned_text = cleaned_text.replace(
        "Nul", ""
    )  # Specifically remove 'Nul' if needed
    return cleaned_text.strip()


# Extract texts from selected boxes
def image_to_text(pdf_file):
    boxes = []
    with open(pdf_file, "rb") as file:
        pdf_reader = PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            lines = page.extract_text().split("\n")
            for line in lines:
                cleaned_text = __clean_text(line)
                boxes.append({"text": cleaned_text})
    return boxes
