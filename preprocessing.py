import cv2
import os
DEBUG_FOLDER = "debug"

os.makedirs(DEBUG_FOLDER, exist_ok=True)

def preprocess_normal(image_path):

    img = cv2.imread(image_path)

    gray = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2GRAY
    )

    output_path = os.path.join(
        DEBUG_FOLDER,
        "normal_processed.png"
    )

    cv2.imwrite(
        output_path,
        gray
    )

    return output_path

def preprocess_handwriting(image_path):

    print(
        "Running handwriting preprocessing..."
    )

    img = cv2.imread(
        image_path
    )

    gray = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2GRAY
    )

    gray = cv2.resize(
        gray,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC
    )

    gray = cv2.fastNlMeansDenoising(
        gray
    )

    output_path = os.path.join(
        DEBUG_FOLDER,
        "handwriting_processed.png"
    )

    cv2.imwrite(
        output_path,
        gray
    )

    return output_path
def preprocess_table(image_path):

    img = cv2.imread(image_path)

    gray = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2GRAY
    )

    processed = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        15,
        4
    )

    output_path = os.path.join(
        DEBUG_FOLDER,
        "table_processed.png"
    )

    cv2.imwrite(
        output_path,
        processed
    )

    return output_path

