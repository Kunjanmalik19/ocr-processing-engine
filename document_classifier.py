import cv2
import numpy as np
from pdf2image import convert_from_path
import tempfile
import os


def detect_document_type(file_path):

    image = None

    # PDF handling
    if file_path.lower().endswith(".pdf"):

        try:

            pages = convert_from_path(
                file_path,
                first_page=1,
                last_page=1
            )

            image = cv2.cvtColor(
                np.array(pages[0]),
                cv2.COLOR_RGB2BGR
            )

        except Exception as e:

            print(
                f"PDF Detection Error: {e}"
            )

            return "ocr"
    else:

        image = cv2.imread(
            file_path
        )

    if image is None:

        return "ocr"

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    edges = cv2.Canny(
        gray,
        50,
        150
    )

    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 180,
        threshold=120,
        minLineLength=120,
        maxLineGap=10
    )

    horizontal = 0
    vertical = 0

    if lines is not None:

        for line in lines:

            x1, y1, x2, y2 = line[0]

            dx = abs(
                x2 - x1
            )

            dy = abs(
                y2 - y1
            )

            if dx > 100 and dy < 10:

                horizontal += 1

            elif dy > 100 and dx < 10:

                vertical += 1

    print(
        f"Horizontal Lines: {horizontal}"
    )

    print(
        f"Vertical Lines: {vertical}"
    )

    if horizontal > 20 and vertical > 10:

        print(
            "Auto Detect: Table Document"
        )

        return "table"

    print(
        "Auto Detect: OCR Classification Required"
    )

    return "ocr"