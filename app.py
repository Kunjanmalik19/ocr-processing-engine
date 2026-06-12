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
from analytics import update_stats
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
    uploaded_file = request.files["file"]
    if uploaded_file.filename == "":
        
        return render_template(
            "index.html",
            result="Please select a file."
        )

    mode = request.form["mode"]
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
    try:
        output_file = os.path.join(
            "output",
            f"{os.path.splitext(uploaded_file.filename)[0]}_result.txt"
        )
        if mode=="table":
            file_name = os.path.splitext(
                uploaded_file.filename
            )[0]
            if is_pdf:
                zip_file=process_pdf_tables(
                    file_path
                )
                result = (
                    "PDF table extraction completed."
                )
                processing_time = round(
                    time.time() - start_time,
                    2
                )
                return render_template(
                    "index.html",
                    result=result,
                    zip_file=zip_file,
                    processing_time=processing_time
                )

            else:
                zip_file = process_table(
                    file_path,
                    document_name=file_name
                )
            result = (
                "Table processed successfully! \n"
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
                processing_time=processing_time
            )
        else:
            if is_pdf:
                process_pdf(
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
                result = process_image(
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
                processing_time=processing_time
            )
    except Exception as e:
        print(f"Error: {e}")
        update_stats(False)

        return render_template(
            "index.html",
            result="An error occurred while processing the file."
        )

if __name__ == "__main__":

    app.run(
        debug=True
    )