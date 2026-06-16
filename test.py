from paddleocr import PaddleOCR
import time

ocr = PaddleOCR(
    use_angle_cls=False,
    lang="en"
)

start = time.time()

result = ocr.ocr(
    r"input\invoice.png",
    cls=False
)

print("TIME:", time.time() - start)