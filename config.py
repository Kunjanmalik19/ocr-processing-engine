import logging
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"
TEMP_UPLOAD_FOLDER = "temp_uploads"
DEBUG_FOLDER = "debug"
BATCH_RESULTS_FOLDER = os.path.join(OUTPUT_FOLDER, "batch_results")
TEMP_PAGES_FOLDER = "temp_pages"

MAX_FILE_SIZE_MB = 100
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "tiff", "pdf"}
SUPPORTED_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp", ".tiff")
PDF_EXTENSION = ".pdf"

OCR_MODE = "normal"
SHOW_CONFIDENCE = False
USE_PREPROCESSING = False

SINGLE_IMAGE_HANDWRITING_THRESHOLD = 75
BATCH_IMAGE_HANDWRITING_THRESHOLD = 90

PDF_RENDER_SCALE = 2

CLASSIFIER_CANNY_THRESHOLD_1 = 50
CLASSIFIER_CANNY_THRESHOLD_2 = 150
CLASSIFIER_HOUGH_THRESHOLD = 120
CLASSIFIER_MIN_LINE_LENGTH = 120
CLASSIFIER_MAX_LINE_GAP = 10
CLASSIFIER_MIN_HORIZONTAL_LINES = 20
CLASSIFIER_MIN_VERTICAL_LINES = 10

PADDLE_OCR_OPTIONS = {
    "use_angle_cls": False,
    "lang": "en",
    "show_log": False,
    "enable_mkldnn": True,
    "cpu_threads": 4,
    "det_limit_side_len": 640,
}

PADDLE_TABLE_OPTIONS = {
    "show_log": False,
}

STATS_FILE = os.path.join(OUTPUT_FOLDER, "stats.json")
ERROR_LOG_FILE = os.path.join(OUTPUT_FOLDER, "error.log")

LOG_LEVEL = os.environ.get("OCR_LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def configure_logging() -> None:
    """Configure application logging once with a consistent format."""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format=LOG_FORMAT,
    )


configure_logging()
