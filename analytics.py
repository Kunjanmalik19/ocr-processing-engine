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