import time
import fitz
from paddleocr import PaddleOCR
import os

PDF_FILE = r"C:\Users\kunja\OneDrive\Desktop\ocr system\input\rty.pdf"  # change path

print("Loading OCR model...")
ocr = PaddleOCR(
    use_textline_orientation=False,
    lang="en"
)
print("OCR model loaded!")

document = fitz.open(PDF_FILE)

total_start = time.time()

page_times = []

for page_num in range(len(document)):

    print(f"\n===== PAGE {page_num + 1} =====")

    page = document[page_num]

    render_start = time.time()

    pix = page.get_pixmap(
        matrix=fitz.Matrix(
            1,
            1
        )
    )

    image_path = f"benchmark_page_{page_num}.png"

    pix.save(image_path)

    render_time = time.time() - render_start

    print(
        f"Render Time: "
        f"{render_time:.2f}s"
    )

    ocr_start = time.time()

    result = ocr.ocr(
        image_path,
        cls=False
    )

    ocr_time = time.time() - ocr_start

    page_times.append(ocr_time)

    print(
        f"OCR Time: "
        f"{ocr_time:.2f}s"
    )

    line_count = 0

    if result and result[0]:

        for line in result[0]:

            line_count += 1

    print(
        f"Lines Found: "
        f"{line_count}"
    )

    os.remove(
        image_path
    )

print("\n==============================")
print("BENCHMARK COMPLETE")
print("==============================")

print(
    f"Pages: {len(document)}"
)

print(
    f"Total OCR Time: "
    f"{sum(page_times):.2f}s"
)

print(
    f"Average Per Page: "
    f"{sum(page_times)/len(page_times):.2f}s"
)

print(
    f"Wall Clock Time: "
    f"{time.time()-total_start:.2f}s"
)

document.close()