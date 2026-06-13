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
MAX_FILE_SIZE = 20 * 1024 * 1024

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
                    result="File exceeds 20 MB limit."
                    
                )

        # ======================
        # MULTIPLE FILES
        # ======================

        if multiple_files and mode != "table":

            batch_folder = os.path.join(
                "output",
                "batch_results"
            )

            os.makedirs(
                batch_folder,
                exist_ok=True
            )

            for uploaded_file in uploaded_files:

                file_path = os.path.join(
                    UPLOAD_FOLDER,
                    uploaded_file.filename
                )

                uploaded_file.save(
                    file_path
                )

                output_file = os.path.join(
                    batch_folder,
                    f"{os.path.splitext(uploaded_file.filename)[0]}_result.txt"
                )

                is_pdf = uploaded_file.filename.lower().endswith(
                    ".pdf"
                )

                if is_pdf:

                    process_pdf(
                        file_path,
                        output_file,
                        mode
                    )

                else:

                    process_image(
                        file_path,
                        output_file,
                        mode
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

            import zipfile

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

            update_stats(True)

            processing_time = round(
                time.time() - start_time,
                2
            )

            return render_template(
                "index.html",
                result=f"{len(uploaded_files)} files processed successfully.",
                zip_file=zip_file,
                processing_time=processing_time,
                average_confidence=average_confidence
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

        is_pdf = uploaded_file.filename.lower().endswith(
            ".pdf"
        )

        output_file = os.path.join(
            "output",
            f"{os.path.splitext(uploaded_file.filename)[0]}_result.txt"
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

                zip_file, average_confidence = process_table(
                    file_path,
                    document_name=file_name
                )

                result = (
                    "Table processed successfully!\n"
                    "CSV and XLSX files generated."
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
                average_confidence=average_confidence
            )

        else:

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