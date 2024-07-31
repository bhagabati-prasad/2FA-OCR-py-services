import re


def replace_special_chars(text, replacement=""):
    # Define the pattern to match special characters
    pattern = r"[^\w\s]"

    # Replace all special characters with the specified replacement character
    cleaned_text = re.sub(pattern, replacement, text)

    return cleaned_text
