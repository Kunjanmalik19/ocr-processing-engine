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
# LOAD OCR MODEL
# ======================================

print("Loading OCR model...")

ocr = PaddleOCR(
    use_angle_cls=True,
    lang='en'
)

print("OCR model loaded successfully!")

def get_processed_image(image_path):

    if OCR_MODE == "normal":
        return preprocess_normal(
            image_path
        )

    elif OCR_MODE == "handwriting":
        return preprocess_handwriting(
            image_path
        )

    elif OCR_MODE == "table":
        return preprocess_table(
            image_path
        )

    return image_path

# ======================================
# IMAGE OCR
# ======================================

def process_image(image_path, output_file):

    try:

        if USE_PREPROCESSING:

            processed_path = get_processed_image(
                image_path
            )

            result = ocr.ocr(
                processed_path,
                cls=True
            )

            #os.remove(
                #processed_path
            #)

        else:

            result = ocr.ocr(
                image_path,
                cls=True
            )
        extracted_lines = []
        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:

            print("\nExtracted Text:")
            print("-" * 50)

            for line in result[0]:

                text = line[1][0]
                extracted_lines.append(text)
                if SHOW_CONFIDENCE:

                    confidence = line[1][1]

                    print(
                        f"{text} | Confidence: {confidence:.2f}"
                    )

                    file.write(
                        f"{text} | Confidence: {confidence:.2f}\n"
                    )

                else:

                    print(text)

                    file.write(
                        text + "\n"
                    )

            print("-" * 50)

        print(
            f"Saved: {output_file}")
        export_json(
        os.path.basename(image_path),
        OCR_MODE,
        extracted_lines
        )
        

    except Exception as e:

        print(
            f"Error processing image: {e}"
        )
# ======================================
# PDF OCR
# ======================================

def process_pdf(pdf_path, output_file):

    try:

        document = fitz.open(
            pdf_path
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:

            for page_num in range(
                len(document)
            ):

                page = document[
                    page_num
                ]

                pix = page.get_pixmap(
                    matrix=fitz.Matrix(
                        2,
                        2
                    )
                )

                temp_image = (
                    f"temp_page_{page_num}.png"
                )

                pix.save(
                    temp_image
                )

                if USE_PREPROCESSING:

                    processed_path = get_processed_image(
                        temp_image
                    )

                    result = ocr.ocr(
                        processed_path,
                        cls=True
                    )

                    #os.remove(
                        #processed_path
                    #)

                else:

                    result = ocr.ocr(
                        temp_image,
                        cls=True
                    )

                print(
                    f"\n===== PAGE {page_num + 1} ====="
                )

                file.write(
                    f"\n===== PAGE {page_num + 1} =====\n"
                )

                for line in result[0]:

                    text = line[1][0]

                    if SHOW_CONFIDENCE:

                        confidence = line[1][1]

                        print(
                            f"{text} | Confidence: {confidence:.2f}"
                        )

                        file.write(
                            f"{text} | Confidence: {confidence:.2f}\n"
                        )

                    else:

                        print(text)

                        file.write(
                            text + "\n"
                        )

                os.remove(
                    temp_image
                )

        document.close()

        print(
            f"\nSaved: {output_file}"
        )

    except Exception as e:

        print(
            f"Error processing PDF: {e}"
        )

def process_pdf_tables(
    pdf_path
):

    import fitz
    import shutil

    temp_folder = "temp_pages"

    os.makedirs(
        temp_folder,
        exist_ok=True
    )

    document = fitz.open(
        pdf_path
    )

    pdf_name = os.path.splitext(
        os.path.basename(
            pdf_path
        )
    )[0]

    for page_num in range(
        len(document)
    ):

        page = document[
            page_num
        ]

        pix = page.get_pixmap(
            matrix=fitz.Matrix(
                2,
                2
            )
        )

        image_path = os.path.join(
            temp_folder,
            f"page_{page_num+1}.png"
        )

        pix.save(
            image_path
        )

        print(
            f"\nProcessing Page {page_num+1}"
        )

        process_table(
            image_path,
            document_name=pdf_name,
            page_number=page_num + 1
        )

    document.close()

    shutil.rmtree(
        temp_folder,
        ignore_errors=True
    )

    print(
        "\nPDF Table Extraction Complete!"
    )
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
                output_file
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
                        output_file
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