import json
import os


def export_json(
    filename,
    ocr_mode,
    extracted_lines,
    layout_geometry=None
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
    if layout_geometry is not None:
        data["_internal_layout"] = layout_geometry

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

    return json_path