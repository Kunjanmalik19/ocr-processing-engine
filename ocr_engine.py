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
import zipfile


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

def get_processed_image(image_path,mode):

    if mode == "normal":
        return preprocess_normal(
            image_path
        )

    elif mode == "handwriting":
        return preprocess_handwriting(
            image_path
        )

    elif mode == "table":
        return preprocess_table(
            image_path
        )

    return image_path

# ======================================
# IMAGE OCR
# ======================================

def process_image(image_path, output_file,mode='normal'):

    try:

        if USE_PREPROCESSING:

            processed_path = get_processed_image(
                image_path,
                mode
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
        mode,
        extracted_lines
        )
        return "\n".join(
            extracted_lines
            )

    except Exception as e:

        print(
            f"Error processing image: {e}"
        )
        return None
# ======================================
# PDF OCR
# ======================================

def process_pdf(pdf_path, output_file, mode):

    try:
        extracted_lines = []

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
                        temp_image,
                        mode
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
                    extracted_lines.append(
                        text
                        )

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
        export_json(
            os.path.basename(pdf_path),
            mode,
            extracted_lines
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

        #print(
            #f"\nProcessing Page {page_num+1}"
        #)

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
    output_folder = os.path.join(
        "output",
        pdf_name
        )

    zip_path = os.path.join(
        "output",
        f"{pdf_name}.zip"
        )

    with zipfile.ZipFile(
        zip_path,
        "w",
        zipfile.ZIP_DEFLATED
        ) as zipf:
        for root, dirs, files in os.walk(
            output_folder
            ):
            for file in files:
                file_path = os.path.join(
                    root,
                    file
                )

                zipf.write(
                    file_path,
                    arcname=file
                )

    print(
        f"ZIP created: {zip_path}"
    )
    shutil.rmtree(
        output_folder,
        ignore_errors=True
        )
    
    print(
        "\nPDF Table Extraction Complete!"
    )
    return zip_path