from flask import Flask
from flask import render_template
from flask import request

from ocr_engine import process_image
from table_export import process_table
from flask import send_file
from ocr_engine import (
    process_image,
    process_pdf,
    process_pdf_tables
)

import os
import shutil
import time
from analytics import (
    update_stats,
    get_stats,
    get_success_rate,
    log_error
)
from document_classifier import detect_document_type
import zipfile
MAX_FILE_SIZE = 100 * 1024 * 1024

app = Flask(__name__)

UPLOAD_FOLDER = "input"
ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "bmp",
    "tiff",
    "pdf"
}
def allowed_file(filename):

    return (
        "." in filename
        and
        filename.rsplit(
            ".",
            1
        )[1].lower() in ALLOWED_EXTENSIONS
    )



os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

@app.route("/")
def home():

    return render_template(
        "index.html"
        
    )

@app.route("/admin")
def admin():

    return render_template(
        "admin.html",
        stats=get_stats(),
        success_rate=get_success_rate()
    )
@app.route(
    "/download/<path:filename>"
)
def download_file(
    filename
):

    return send_file(
        filename,
        as_attachment=True
    )

@app.route("/input/<filename>")
def serve_input_file(filename):

    return send_file(
        os.path.join(
            UPLOAD_FOLDER,
            filename
        )
    )

@app.route(
    "/uploads/<filename>"
)
def uploaded_file_preview(
    filename
):

    return send_file(
        os.path.join(
            UPLOAD_FOLDER,
            filename
        )
    )
@app.route(
    "/process",
    methods=["POST"]
)
def process():

    start_time = time.time()
    average_confidence = None

    uploaded_files = request.files.getlist(
        "file"
    )


    if len(uploaded_files) == 0:
        
        return render_template(
            "index.html",
            result="Please select files."
        )

    mode = request.form["mode"]

    multiple_files = len(
        uploaded_files
    ) > 1

    try:
        processed_files = []

        confidence_scores = []

        # ======================
        # VALIDATION
        # ======================

        for uploaded_file in uploaded_files:

            if not allowed_file(
                uploaded_file.filename
            ):

                return render_template(
                    "index.html",
                    result="Unsupported file type."
                    
                )

            uploaded_file.seek(
                0,
                os.SEEK_END
            )

            file_size = uploaded_file.tell()

            uploaded_file.seek(0)

            if file_size > MAX_FILE_SIZE:

                return render_template(
                    "index.html",
                    result="File exceeds 100 MB limit."
                    
                )

        # ======================
        # MULTIPLE FILES
        # ======================

        if multiple_files :

            batch_folder = os.path.join(
                "output",
                "batch_results"
            )

            os.makedirs(
                batch_folder,
                exist_ok=True
            )
            processed_summary = []

            for uploaded_file in uploaded_files:

                file_path = os.path.join(
                    UPLOAD_FOLDER,
                    uploaded_file.filename
                )

                uploaded_file.save(
                    file_path
                )
                current_mode = mode

                if mode == "auto":

                    current_mode = detect_document_type(
                        file_path
                    )

                    processed_summary.append(
                        f"{uploaded_file.filename} → {current_mode}"
                    )


                    print(
                        f"{uploaded_file.filename} -> {current_mode}"
                    )
                    if current_mode == "table":

                        if uploaded_file.filename.lower().endswith(".pdf"):

                            zip_path, confidence = process_pdf_tables(
                                file_path
                            )

                            confidence_scores.append(
                                confidence
                            )


                            with zipfile.ZipFile(
                                zip_path,
                                "r"
                            ) as table_zip:

                                table_zip.extractall(
                                    batch_folder
                                )
                            print(
                                "Batch folder contents:",
                                os.listdir(batch_folder)
                            )

                            os.remove(
                                zip_path
                            )

                        else:

                            output_folder, confidence = process_table(
                                file_path,
                                document_name=os.path.splitext(
                                    uploaded_file.filename
                                )[0]
                            )

                            confidence_scores.append(
                                confidence
                            )
                            for file in os.listdir(
                                output_folder
                            ):

                                shutil.copy(
                                    os.path.join(
                                        output_folder,
                                        file
                                    ),
                                    batch_folder
                                )

                            shutil.rmtree(
                                output_folder,
                                ignore_errors=True
                            )

                        processed_summary.append(
                            f"{uploaded_file.filename} → table"
                        )

                        processed_files.append(
                            uploaded_file.filename
                        )

                        continue
                output_file = os.path.join(
                    batch_folder,
                    f"{os.path.splitext(uploaded_file.filename)[0]}_result.txt"
                )

                is_pdf = uploaded_file.filename.lower().endswith(
                    ".pdf"
                )

                if is_pdf:

                    pdf_confidence = process_pdf(
                        file_path,
                        output_file,
                        current_mode
                    )

                    processed_files.append(
                        uploaded_file.filename
                    )

                    if pdf_confidence is not None:

                        confidence_scores.append(
                            pdf_confidence
                        )

                else:

                    if current_mode == "ocr":

                        normal_result, normal_confidence = process_image(
                            file_path,
                            output_file,
                            "normal"
                        )

                        if normal_confidence < 90:

                            print(
                                "Low confidence detected. Trying handwriting OCR..."
                            )

                            handwriting_result, handwriting_confidence = process_image(
                                file_path,
                                output_file,
                                "handwriting"
                            )

                            if handwriting_confidence > normal_confidence:

                                result = handwriting_result

                                average_confidence = handwriting_confidence

                                current_mode = "handwriting"

                            else:

                                result = normal_result

                                average_confidence = normal_confidence

                                current_mode = "normal"

                        else:

                            result = normal_result

                            average_confidence = normal_confidence

                            current_mode = "normal"

                    else:

                        result, average_confidence = process_image(
                            file_path,
                            output_file,
                            current_mode
                        )

                    processed_files.append(
                        uploaded_file.filename
                    )

                    confidence_scores.append(
                        average_confidence
                    )

                json_name = (
                    f"{os.path.splitext(uploaded_file.filename)[0]}.json"
                    )

                json_source = os.path.join(
                    "output",
                    json_name
                    )

                json_destination = os.path.join(
                    batch_folder,
                    json_name
                )


                if os.path.exists(
                json_source
                ):

                    shutil.copy(
                        json_source,
                        json_destination
                        )
            zip_file = os.path.join(
                "output",
                "batch_results.zip"
            )


            with zipfile.ZipFile(
                zip_file,
                "w",
                zipfile.ZIP_DEFLATED
            ) as zipf:

                for root, dirs, files in os.walk(
                    batch_folder
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

            shutil.rmtree(
                batch_folder,
                ignore_errors=True
            )
            average_confidence = None

            if confidence_scores:

                average_confidence = round(
                    sum(confidence_scores) /
                    len(confidence_scores),
                    2
                )

            result = (
                "Processed Files:\n\n"
                +
                "\n".join(
                    [f"✓ {name}" for name in processed_files]
                )
                +
                "\n\nZIP package ready for download."
            )

            update_stats(True)

            processing_time = round(
                time.time() - start_time,
                2
            )

            return render_template(
                "index.html",
                result=result,
                zip_file=zip_file,
                processing_time=processing_time,
                average_confidence=average_confidence,
                detected_mode=None,
                processed_summary=processed_summary,
                uploaded_filenames=[
                    f.filename
                    for f in uploaded_files
                
                ]
            )

        # ======================
        # SINGLE FILE
        # ======================

        uploaded_file = uploaded_files[0]

        file_path = os.path.join(
            UPLOAD_FOLDER,
            uploaded_file.filename
        )

        uploaded_file.save(
            file_path
        )
        if mode == "auto":

            mode = detect_document_type(
                file_path
            )

            print(
                f"Detected Mode: {mode}"
            )
            print(
                f"Mode after detection = {mode}"
            )

        is_pdf = uploaded_file.filename.lower().endswith(
            ".pdf"
        )

        output_file = os.path.join(
            "output",
            f"{os.path.splitext(uploaded_file.filename)[0]}_result.txt"
        )
        print(
            f"Entering table check with mode = {mode}"
        )


        if mode == "table":

            file_name = os.path.splitext(
                uploaded_file.filename
            )[0]

            if is_pdf:

                zip_file, average_confidence = process_pdf_tables(
                    file_path
                )

                result = (
                    "PDF table extraction completed."
                )

            else:

                table_result = process_table(
                    file_path,
                    document_name=file_name
                )

                if table_result is None:

                    return render_template(
                        "index.html",
                        result="No table detected in image."
    )

                output_folder, average_confidence = table_result

                zip_file = os.path.join(
                    "output",
                    f"{file_name}.zip"
                )

                with zipfile.ZipFile(
                    zip_file,
                    "w",
                    zipfile.ZIP_DEFLATED
                ) as zipf:

                    for root, dirs, files in os.walk(
                        output_folder
                    ):

                        for file in files:

                            file_path_inside = os.path.join(
                                root,
                                file
                            )

                            zipf.write(
                                file_path_inside,
                                arcname=file
                            )

                shutil.rmtree(
                    output_folder,
                    ignore_errors=True
                )
            result = (
                "Table extraction completed."
            )

            processing_time = round(
                time.time() - start_time,
                2
            )

            return render_template(
                "index.html",
                result=result,
                zip_file=zip_file,
                processing_time=processing_time,
                average_confidence=average_confidence,
                detected_mode=mode,
                uploaded_filenames=[
                    f.filename
                    for f in uploaded_files
                ]
            )

        else:
            print(
                f"is_pdf = {is_pdf}"
            )

            if is_pdf:

                average_confidence = process_pdf(
                    file_path,
                    output_file,
                    mode
                )

                with open(
                    output_file,
                    "r",
                    encoding="utf-8"
                ) as file:

                    result = file.read()

            else:

                if mode == "ocr":

                    normal_result, normal_confidence = process_image(
                        file_path,
                        output_file,
                        "normal"
                    )

                    if normal_confidence < 90:

                        print(
                            "Trying handwriting OCR..."
                        )

                        handwriting_result, handwriting_confidence = process_image(
                            file_path,
                            output_file,
                            "handwriting"
                        )

                        if handwriting_confidence > normal_confidence:

                            result = handwriting_result
                            average_confidence = handwriting_confidence
                            mode = "handwriting"

                        else:

                            result = normal_result
                            average_confidence = normal_confidence
                            mode = "normal"

                    else:

                        result = normal_result
                        average_confidence = normal_confidence
                        mode = "normal"

                else:

                    result, average_confidence = process_image(
                        file_path,
                        output_file,
                        mode
                    )

            txt_file = output_file

            json_file = os.path.join(
                "output",
                f"{os.path.splitext(uploaded_file.filename)[0]}.json"
            )

            update_stats(True)

            processing_time = round(
                time.time() - start_time,
                2
            )

            return render_template(
                "index.html",
                result=result,
                txt_file=txt_file,
                json_file=json_file,
                processing_time=processing_time,
                average_confidence=average_confidence,
                detected_mode=mode,
                uploaded_filenames=[
                    f.filename
                    for f in uploaded_files
                ]
            )

    except Exception as e:

        print(
            f"Error: {e}"
        )

        log_error(
            str(e)
        )

        update_stats(False)

        return render_template(
            "index.html",
            result="An error occurred while processing the file."
        )

if __name__ == "__main__":

    app.run(
        debug=True
    )