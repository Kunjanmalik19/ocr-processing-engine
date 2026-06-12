import os
import fitz
from paddleocr import PaddleOCR
from preprocessing import (
    preprocess_normal,
    preprocess_handwriting,
    preprocess_table
)
from table_export import process_table
from json_export import export_json
from ocr_engine import (
    process_image,
    process_pdf,
    process_pdf_tables
)


# ======================================
# CONFIGURATION
# ======================================
OCR_MODE = "normal"
SHOW_CONFIDENCE = False
USE_PREPROCESSING = True

INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"

SUPPORTED_EXTENSIONS = (
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tiff"
)

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ======================================
# ======================================
# MENU
# ======================================

while True:

    print("\n" + "=" * 40)
    print("OCR SYSTEM")
    print("=" * 40)

    print("OCR Modes:")
    print("1. Normal")
    print("2. Handwriting")
    print("3. Table")

    mode = input(
        "\nChoose OCR Mode: "
    ).strip()

    if mode == "1":

        OCR_MODE = "normal"

    elif mode == "2":

        OCR_MODE = "handwriting"

    elif mode == "3":

        OCR_MODE = "table"

    else:

        print("Invalid OCR Mode!")
        continue

    print("\nOperations:")
    print("1. Single Image OCR")
    print("2. Process All Images")
    print("3. PDF OCR")
    print("4. PDF Table Extraction")
    print("5. Exit")

    choice = input(
        "\nEnter your choice: "
    ).strip()

    # ==================================
    # SINGLE IMAGE OCR
    # ==================================

    if choice == "1":

        filename = input(
            "Enter image filename: "
        ).strip()

        image_path = os.path.join(
            INPUT_FOLDER,
            filename
        )

        if not os.path.exists(image_path):

            print("File not found!")
            continue

        output_file = os.path.join(
            OUTPUT_FOLDER,
            f"{os.path.splitext(filename)[0]}_result.txt"
        )

        if OCR_MODE == "table":

            process_table(
                image_path
            )

        else:

            process_image(
                image_path,
                output_file,
                ORC_MODE
            )

    # ==================================
    # MULTIPLE IMAGE OCR
    # ==================================

    elif choice == "2":

        files_found = False

        for filename in os.listdir(
            INPUT_FOLDER
        ):

            if filename.lower().endswith(
                SUPPORTED_EXTENSIONS
            ):

                files_found = True

                image_path = os.path.join(
                    INPUT_FOLDER,
                    filename
                )

                output_file = os.path.join(
                    OUTPUT_FOLDER,
                    f"{os.path.splitext(filename)[0]}_result.txt"
                )

                print(
                    f"\nProcessing: {filename}"
                )

                if OCR_MODE == "table":

                    process_table(
                        image_path
                    )

                else:

                    process_image(
                        image_path,
                        output_file,
                        OCR_MODE
                    )

        if not files_found:

            print(
                "No supported images found in input folder."
            )

    # ==================================
    # PDF OCR
    # ==================================

    elif choice == "3":

        filename = input(
            "Enter PDF filename: "
        ).strip()

        pdf_path = os.path.join(
            INPUT_FOLDER,
            filename
        )

        if not os.path.exists(pdf_path):

            print("PDF file not found!")
            continue

        output_file = os.path.join(
            OUTPUT_FOLDER,
            f"{os.path.splitext(filename)[0]}_result.txt"
        )

        process_pdf(
            pdf_path,
            output_file
        )
    elif choice == "4":
        filename = input(
        "Enter PDF filename: "
        ).strip()
        pdf_path = os.path.join(
        INPUT_FOLDER,
        filename
    )
        if not os.path.exists(
        pdf_path
        ):
            print(
                "PDF file not found!"
        )
            continue
        process_pdf_tables(
            pdf_path
            )
    # ==================================
    # EXIT
    # ==================================

    elif choice == "5":

        print("\nExiting OCR System...")
        break

    else:

        print("Invalid choice!")