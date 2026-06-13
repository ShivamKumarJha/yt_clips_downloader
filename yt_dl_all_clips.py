import json
import subprocess
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import os


def download_clip(link, output_dir, idx, total):
    print(f"[{idx}/{total}] {link}")

    result = subprocess.run(
        ["python", "Yt-clip-dl.py", link, "--output-dir", output_dir],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return (link, False, result.stderr)

    return (link, True, None)


def main():
    if len(sys.argv) < 2:
        print("Usage: python yt_dl_all_clips.py <json> --output-dir <dir>")
        sys.exit(1)

    json_file = Path(sys.argv[1])
    output_dir = "clips"

    if "--output-dir" in sys.argv:
        idx = sys.argv.index("--output-dir")
        output_dir = sys.argv[idx + 1]

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    clips = data.get("clips", [])

    print(f"Found {len(clips)} clips")
    print(f"Output directory: {output_dir}")

    MAX_WORKERS = 16  # threads can go higher safely

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(download_clip, link, output_dir, i, len(clips))
            for i, link in enumerate(clips, start=1)
        ]

        for f in as_completed(futures):
            link, ok, err = f.result()
            if ok:
                print("✔", link)
            else:
                print("✖", link)
                print(err)


if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    main()