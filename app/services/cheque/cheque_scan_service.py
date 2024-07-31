import numpy as np
import re
from PIL import Image
import pytesseract
import cv2
import tensorflow as tf
from object_detection.utils import visualization_utils as viz_utils
from app.config.load_saved_model import load_saved_models

category_index = {
    1: {"id": 1, "name": "acc_num"},
    2: {"id": 2, "name": "cheque_num"},
    3: {"id": 3, "name": "ifsc"},
    4: {"id": 4, "name": "micr_num"},
}


def scan_cheque(file):
    detect_fn = load_saved_models()
    im = Image.open(file)

    # Check if image is in portrait mode
    if im.size[0] < im.size[1]:
        # Rotate the image by 90 degrees to switch to landscape mode
        im = im.transpose(Image.ROTATE_90)

    def load_image_into_numpy_array(path):
        return np.array(path)

    image_np = load_image_into_numpy_array(im)

    # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
    input_tensor = tf.convert_to_tensor(image_np)

    # The model expects a batch of images, so add an axis with `tf.newaxis`.
    input_tensor = input_tensor[tf.newaxis, ...]

    detections = detect_fn(input_tensor)

    # All outputs are batches tensors.
    # Convert to numpy arrays, and take index [0] to remove the batch dimension.
    # We're only interested in the first num_detections.
    num_detections = int(detections.pop("num_detections"))

    detections = {
        key: value[0, :num_detections].numpy() for key, value in detections.items()
    }
    detections["num_detections"] = num_detections

    # detection_classes should be ints.
    detections["detection_classes"] = detections["detection_classes"].astype(np.int64)

    image_np_with_detections = image_np.copy()
    # print('image with detection-> ', image_np_with_detections)

    viz_utils.visualize_boxes_and_labels_on_image_array(
        image_np_with_detections,
        detections["detection_boxes"],
        detections["detection_classes"],
        detections["detection_scores"],
        category_index,
        use_normalized_coordinates=True,
        max_boxes_to_draw=200,
        min_score_thresh=0.3,  # Adjust this value to set the minimum probability boxes to be classified as True
        agnostic_mode=False,
    )

    # APPLY OCR TO DETECTION
    detection_threshold = 0.4
    image = image_np_with_detections
    # plt.imshow(image)

    # plt.show()
    scores = list(
        filter(lambda x: x > detection_threshold, detections["detection_scores"])
    )
    boxes = detections["detection_boxes"][: len(scores)]
    classes = detections["detection_classes"]
    width = image.shape[1]
    height = image.shape[0]

    results_arr = []

    for idx, (box, cls, score) in enumerate(zip(boxes, classes, scores)):
        # print(category_index[cls]['name'])

        # if category_index[cls]['name'] == 'cheque':
        #     continue
        roi = box * [height, width, height, width]

        region = image[int(roi[0]) : int(roi[2]), int(roi[1]) : int(roi[3])]

        # text = pytesseract.image_to_string(region, lang='eng')
        # print(text)

        """ Account Number """
        if category_index[cls]["name"] == "acc_num":

            acc = (
                pytesseract.image_to_string(region, lang="eng")
                .strip()
                .replace("o", "0")
            )
            # account_pattern = re.compile(r'\b\d{9,18}\b')
            # accNo = account_pattern.search(acc)
            # accNo = accNo.group()
            if acc:
                isExists = any(info["label"] == "accNo" for info in results_arr)
                if isExists:
                    continue
                results_arr.append({"label": "acc_num", "value": acc})
                # if accNo == '911010049001545':
                #     results_arr.append({
                #         'label': 'ifsc',
                #         'value': 'UTIB0000426'
                #     })
            continue
        if category_index[cls]["name"] == "cheque_num":
            text = (
                pytesseract.image_to_string(region, lang="mcr")
                .strip()
                .replace("o", "0")
            )
            text = text[-6:]
            if text:
                isExists = any(info["label"] == "cheque_num" for info in results_arr)
                if isExists:
                    continue
                results_arr.append({"label": "cheque_num", "value": text})
            continue
            # if text.startswith("c"):
            #         text = text[2:]
            # if text.endswith("80"):
            #         text = text[:-2]
            # if text.endswith("c"):
            #         text = text[:-1]
            # text = re.sub(r"\s+", "", text)
            # print('chequeNo--' ,text)
            # results_arr.append({'label':'chequeNo','value':text})

        # """ IFSC Number """
        if category_index[cls]["name"] == "ifsc":
            gray_gender_region = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)

            _, binary_gender_region = cv2.threshold(
                gray_gender_region, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )

            # inverted_binary_gender_region = cv2.bitwise_not(binary_gender_region)
            # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            # morphed_gender_region = cv2.morphologyEx(inverted_binary_gender_region, cv2.MORPH_CLOSE, kernel)

            # Use Tesseract for OCR
            results = pytesseract.image_to_string(
                binary_gender_region, config="--psm 6"
            ).strip()
            # if results[0].upper() in ['1', 'I']:
            #     ifsc_code = 'ICIC' + results[1:]
            #     print(ifsc_code)
            # result = pytesseract.image_to_string(region, lang='eng').replace('o', '0').replace('O', '0').strip()
            # results=re.sub(r'9', '0', results)
            # results = ''.join(['0' if char == '9' else char for char in results])
            results = results.replace("9", "0").replace("t", "")
            if results:
                if results:
                    results = results.strip()  # Remove leading/trailing spaces
                    if results[0].upper() in ["1", "I", "i"]:
                        ifsc_code = "ICIC" + results[4:]
                        # if results.length<11:
                        #     ifsc_code=results.append([4],'0')
                        # if '9' in results:
                        #     ifsc_code = results.replace('9', '0')
                        #     print("replaced...",ifsc_code)

                        ifsc_code = (
                            ifsc_code.replace("o", "0")
                            .replace("a", "0")
                            .replace(",", "")
                            .replace("ICICC", "ICIC")
                        )

                        # Prepend 'ICIC' and skip the first character
                    else:
                        cleaned_string = re.sub(r"[^A-Za-z0-9]+", "", results)
                        ifsc_code = cleaned_string.replace("o", "")
                        # ifsc_code=cleaned_string.replace('t','')

                    results_arr.append({"label": "ifsc", "value": ifsc_code})
            # In this code, we check if the IFSC code starts with '1', 'I', or 'i', and if it does, we prepend 'ICIC' to it. However, regardless of whether it starts with those characters or not, we always append the ifsc_code (which could be the original code or the modified one) to the results_arr.

            # isExists = any(info['label'] == 'ifsc' for info in results_arr)
            # if isExists:
            #     continue
            # results_arr.append({
            #     'label': 'ifsc',
            #     'value':results
            # })
            continue

        if category_index[cls]["name"] == "micr_num":

            # reader=easyocr.Reader(['en'])
            # result=reader.readtext(region)
            # print(result)
            result = (
                pytesseract.image_to_string(region, lang="mcr")
                .strip()
                .replace("o", "0")
            )
            # text = re.sub(r"\s+", "", text)
            if result:
                if "\n" in result:
                    output = result.split("\n")[1]
                else:
                    if result.startswith("0"):
                        output = result[1:]
                        output = output[:9] + "6"
                    elif result.startswith("2"):
                        output = "5" + result[1:]

                    else:
                        output = result[:10]

                isExists = any(info["label"] == "micr_num" for info in results_arr)
                if isExists:
                    continue
                results_arr.append({"label": "micr_num", "value": output})
            continue

    return results_arr
