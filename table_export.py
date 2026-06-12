from paddleocr import PPStructure
from bs4 import BeautifulSoup
import pandas as pd
import os

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
     table_count = 0
     for block in result:

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

        # =========================
        # UNIQUE FILE NAMES
        # =========================

        if page_number is None:

            base_name = (
                f"table_{table_count}"
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

        print(
            f"\nTable {table_count} exported!"
        )

        print(
            f"CSV: {csv_path}"
        )

        print(
            f"Excel: {excel_path}"
        )
        if table_count == 0:
            print(
            "\nNo structured tables found."
            )

            print(
            "This may be a scanned table."
            )