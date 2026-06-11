import os
import fitz
from paddleocr import PaddleOCR

# ======================================
# CONFIGURATION
# ======================================

SHOW_CONFIDENCE = False

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

# ======================================
# IMAGE OCR
# ======================================

def process_image(image_path, output_file):

    try:

        result = ocr.ocr(
            image_path,
            cls=True
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:

            print("\nExtracted Text:")
            print("-" * 50)

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

                    file.write(text + "\n")

            print("-" * 50)

        print(f"Saved: {output_file}")

    except Exception as e:

        print(
            f"Error processing image: {e}"
        )

# ======================================
# PDF OCR
# ======================================

def process_pdf(pdf_path, output_file):

    try:

        document = fitz.open(pdf_path)

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:

            for page_num in range(len(document)):

                page = document[page_num]

                pix = page.get_pixmap(
                    matrix=fitz.Matrix(2, 2)
                )

                temp_image = (
                    f"temp_page_{page_num}.png"
                )

                pix.save(temp_image)

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

                        file.write(text + "\n")

                os.remove(temp_image)

        document.close()

        print(f"\nSaved: {output_file}")

    except Exception as e:

        print(
            f"Error processing PDF: {e}"
        )

# ======================================
# MENU
# ======================================

while True:

    print("\n" + "=" * 40)
    print("OCR SYSTEM")
    print("=" * 40)

    print("1. Single Image OCR")
    print("2. Process All Images")
    print("3. PDF OCR")
    print("4. Exit")

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

    # ==================================
    # EXIT
    # ==================================

    elif choice == "4":

        print("\nExiting OCR System...")
        break

    else:

        print("Invalid choice!")