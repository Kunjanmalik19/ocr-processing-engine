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

app = Flask(__name__)

UPLOAD_FOLDER = "input"

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

    uploaded_file = request.files["file"]

    mode = request.form["mode"]

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
            return render_template(
                "index.html",
                result=result,
                zip_file=zip_file
                )

        else:

            csv_file, xlsx_file = process_table(
                file_path,
                document_name=file_name
                )
        
        result= (

        "Table processed successfully! \n" 
        "CSV and XLSX files generated."
        )
        return render_template(
            "index.html",
            result=result,
            csv_file=csv_file,
            xlsx_file=xlsx_file
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
        return render_template(
            "index.html",
            result=result,
            txt_file=txt_file,json_file=json_file
            )
if __name__ == "__main__":

    app.run(
        debug=True
    )