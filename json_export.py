import json
import os


def export_json(
    filename,
    ocr_mode,
    extracted_lines
):

    os.makedirs(
        "output",
        exist_ok=True
    )

    data = {
        "filename": filename,
        "ocr_mode": ocr_mode,
        "line_count": len(extracted_lines),
        "text": extracted_lines
    }

    json_path = os.path.join(
        "output",
        f"{os.path.splitext(filename)[0]}.json"
    )

    with open(
        json_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"JSON saved: {json_path}"
    )
    