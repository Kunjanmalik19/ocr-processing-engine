from paddleocr import PPStructure
from bs4 import BeautifulSoup
import pandas as pd
import os
import zipfile
import shutil

# Load once when imported
table_engine = PPStructure(
    show_log=False
)

def process_table(
    image_path,
    document_name="table",
    page_number=None
):

    BASE_DIR = os.path.dirname(
        os.path.abspath(__file__)
    )

    output_folder = os.path.join(
        BASE_DIR,
        "output",
        document_name
    )

    os.makedirs(
        output_folder,
        exist_ok=True
    )

    result = table_engine(
        image_path
    )
    total_confidence = 0
    confidence_count = 0

    table_count = 0

    last_csv = None
    last_xlsx = None

    for block in result:

        if "score" in block:

            total_confidence += block["score"]

            confidence_count += 1

        if block["type"] != "table":
            continue

        table_count += 1

        html = block["res"]["html"]

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        table = soup.find(
            "table"
        )

        rows = []

        for tr in table.find_all(
            "tr"
        ):

            row = []

            for td in tr.find_all(
                ["td", "th"]
            ):

                row.append(
                    td.get_text(
                        strip=True
                    )
                )

            rows.append(row)

        df = pd.DataFrame(rows)

        if page_number is None:

            base_name = (
                f"{document_name}_table{table_count}"
            )

        else:

            base_name = (
                f"page_{page_number}_table_{table_count}"
            )

        csv_path = os.path.join(
            output_folder,
            f"{base_name}.csv"
        )

        excel_path = os.path.join(
            output_folder,
            f"{base_name}.xlsx"
        )

        df.to_csv(
            csv_path,
            index=False,
            header=False
        )

        df.to_excel(
            excel_path,
            index=False,
            header=False
        )

    if table_count == 0:

        print(
         "\nNo structured tables found."
    )

        print(
            "This may be a scanned table."
        )

        return None

# ONLY CREATE ZIP IF TABLES EXIST

    zip_path = os.path.join(
        "output",
        f"{document_name}.zip"
    )

        # print(
        #     f"\nTable {table_count} exported!"
        # )

        # print(
        #     f"CSV: {csv_path}"
        # )

        # print(
        #     f"Excel: {excel_path}"
        # )
    zip_path = os.path.join(
        "output",
        f"{document_name}.zip"
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
    shutil.rmtree(
        output_folder,
        ignore_errors=True
            )
    
    average_confidence = 0

    if confidence_count > 0:

        average_confidence = round(
            (total_confidence / confidence_count) * 100,
            2
        )

    return (
        zip_path,
        average_confidence
    )