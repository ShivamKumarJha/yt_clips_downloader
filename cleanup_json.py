import json
from pathlib import Path
import argparse


def process_json_files(folder, dry_run=False):

    folder = Path(folder)

    deleted = 0
    checked = 0

    for json_file in folder.rglob("*.json"):

        checked += 1

        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            video_file = data.get("video_file")

            if not video_file:
                print(f"[SKIP] No video_file field: {json_file}")
                continue

            video_path = Path(video_file)

            if not video_path.exists():

                print(f"\nDELETE JSON:")
                print(json_file)

                print("Missing video:")
                print(video_path)

                if not dry_run:
                    json_file.unlink()

                deleted += 1

        except Exception as e:

            print(f"\nERROR: {json_file}")
            print(e)

    print("\n--------------------")
    print(f"Checked : {checked}")
    print(f"Deleted : {deleted}")

    if dry_run:
        print("Mode    : DRY RUN")


def main():

    parser = argparse.ArgumentParser(
        description="Delete JSON files whose video_file does not exist"
    )

    parser.add_argument(
        "folder",
        help="Folder containing JSON files"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show files without deleting"
    )

    args = parser.parse_args()

    process_json_files(
        args.folder,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()