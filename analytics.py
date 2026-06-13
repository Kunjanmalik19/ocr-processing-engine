import json
import os

STATS_FILE = "output/stats.json"

def update_stats(success=True):

        os.makedirs(
            "output",
            exist_ok=True
        )

        if os.path.exists(STATS_FILE):

            with open(
                STATS_FILE,
                "r"
            ) as file:

                stats = json.load(file)

        else:

            stats = {
                "files_processed": 0,
                "successful": 0,
                "failed": 0
            }

        stats["files_processed"] += 1

        if success:

            stats["successful"] += 1

        else:

            stats["failed"] += 1

        with open(
            STATS_FILE,
            "w"
        ) as file:

            json.dump(
                stats,
                file,
                indent=4
            )

def get_stats():
    # Ensure output directory exists and return stored stats or defaults
    os.makedirs("output", exist_ok=True)

    if not os.path.exists(STATS_FILE):
        return {
            "files_processed": 0,
            "successful": 0,
            "failed": 0
        }

    with open(STATS_FILE, "r") as file:
        stats = json.load(file)

    return stats

def get_success_rate():

    stats = get_stats()

    total = (
        stats["successful"]
        + stats["failed"]
    )

    if total == 0:

        return 0

    return round(
        (
            stats["successful"]
            / total
        ) * 100,
        2
    )

from datetime import datetime

def log_error(error_message):

    log_file = "output/error.log"

    with open(
        log_file,
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            f"\n{'='*50}\n"
        )

        file.write(
            f"Timestamp: {datetime.now()}\n"
        )

        file.write(
            f"Error: {error_message}\n"
        )

        file.write(
            f"{'='*50}\n"
        )