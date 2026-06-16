from paddleocr import PaddleOCR
import time

ocr = PaddleOCR(
    use_angle_cls=False,
    lang='en',
    show_log=False,
    enable_mkldnn=True,
    cpu_threads=4
)

for i in range(5):
    start = time.time()

    ocr.ocr(
        r"input\invoice.png",
        cls=False
    )

    print(
        f"Run {i+1}: {time.time()-start:.2f}s"
    )