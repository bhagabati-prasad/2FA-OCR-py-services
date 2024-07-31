import pytesseract as docScanner
import platform

if platform.system() == "Windows":
    docScanner.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )


def doc_scanner(image):
    return docScanner.image_to_string(image, lang="eng", config="--psm 4")
