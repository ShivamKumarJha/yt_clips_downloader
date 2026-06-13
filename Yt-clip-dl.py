import subprocess
import json
import re
import shutil
import argparse
import requests
from pathlib import Path
from datetime import datetime


def sanitize_filename(name: str) -> str:
    """
    Remove invalid filename characters.
    """

    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = re.sub(r"\s+", " ", name).strip()

    return name


def get_clip_title(url: str) -> str:

    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=30
    )

    response.raise_for_status()

    html = response.text

    match = re.search(
        r"<title>(.*?)</title>",
        html,
        re.IGNORECASE | re.DOTALL
    )

    if not match:
        return "youtube_clip"

    title = match.group(1)

    #
    # Remove:
    # ✂️
    # - YouTube
    #

    title = title.replace("✂️", "")

    title = re.sub(
        r"\s*-\s*YouTube\s*$",
        "",
        title
    )

    title = title.strip()

    return sanitize_filename(title)


def get_clip_info(url):

    result = subprocess.run(
        ["yt-dlp", "-J", url],
        capture_output=True,
        text=True,
        check=True
    )

    data = json.loads(result.stdout)

    #
    # CLIP ID
    #

    clip_id = data.get("id")

    #
    # VIDEO ID
    #

    video_id = data.get("video_id")

    #
    # Fallback:
    # extract from thumbnail URL
    #

    thumbnail = data.get("thumbnail", "")

    if (
        not video_id
        or video_id.startswith("Ugkx")
    ) and "/vi/" in thumbnail:

        video_id = thumbnail.split("/vi/")[1].split("/")[0]

    if not video_id:
        raise Exception("Could not extract video ID")

    original_url = f"https://www.youtube.com/watch?v={video_id}"

    #
    # TIMESTAMPS
    #

    start = data.get("section_start")

    end = data.get("section_end")

    if start is None:
        start = data.get("start_time")

    if end is None:
        end = data.get("end_time")

    if start is None or end is None:
        raise Exception("Could not extract timestamps")

    title = get_clip_title(url)

    upload_date = data.get("upload_date")

    return {
        "clip_id": clip_id,
        "video_id": video_id,
        "video_url": original_url,
        "start": start,
        "end": end,
        "title": title,
        "upload_date": upload_date,
    }


def build_output_paths(
    title: str,
    upload_date: str,
    clip_id: str,
    start,
    end,
    base_dir: str = "clips"
):

    #
    # upload_date format:
    # YYYYMMDD
    #

    if upload_date and len(upload_date) >= 6:

        year = upload_date[:4]
        month = upload_date[4:6]

    else:

        now = datetime.now()

        year = now.strftime("%Y")
        month = now.strftime("%m")

    output_dir = Path(base_dir) / year / month

    output_dir.mkdir(parents=True, exist_ok=True)

    #
    # unique filename
    #

    filename = (
        f"{title} "
        f"[{int(start)}-{int(end)}] "
        f"[{clip_id}]"
    )

    filename = sanitize_filename(filename)

    #
    # avoid very long filenames
    #

    filename = filename[:180]

    video_path = output_dir / f"{filename}.mp4"

    metadata_path = output_dir / f"{filename}.json"

    return video_path, metadata_path


def save_metadata(metadata_path: Path, info: dict):

    with open(metadata_path, "w", encoding="utf-8") as f:

        json.dump(
            info,
            f,
            indent=2,
            ensure_ascii=False
        )


def cleanup_temp_files():

    for f in Path(".").glob("temp_clip*"):

        try:
            f.unlink()

        except Exception:
            pass


def download_clip(video_url, start, end, final_path: Path, clip_id: str, video_id: str):

    Path("temp").mkdir(exist_ok=True)

    section = f"*{start}-{end}"

    temp_template = f"temp/{video_id}_{start}_{end}_{clip_id}.%(ext)s"

    cmd = [
        "yt-dlp",
        "-f", "bv*+ba/b",
        "--download-sections", section,
        "--downloader", "ffmpeg",
        "--merge-output-format", "mp4",
        "--remux-video", "mp4",
        "-o", temp_template,
        video_url
    ]

    print("\nDownloading clip...\n")

    subprocess.run(cmd, check=True, timeout=600)

    # FIND actual output safely
    temp_files = list(Path("temp").glob(f"{video_id}_{start}_{end}_{clip_id}*.mp4"))

    if not temp_files:
        raise Exception("Downloaded file not found")

    temp_file = temp_files[0]

    shutil.move(str(temp_file), str(final_path))

    print(f"\nSaved to:\n{final_path}")

    return final_path


def main():

    parser = argparse.ArgumentParser(
        description="Download YouTube clips"
    )

    parser.add_argument(
        "url",
        help="YouTube clip URL"
    )

    parser.add_argument(
        "--output-dir",
        default="clips",
        help="Base output directory"
    )

    args = parser.parse_args()

    clip_url = args.url

    print("Resolving clip URL...\n")

    info = get_clip_info(clip_url)

    video_path, metadata_path = build_output_paths(
        info["title"],
        info["upload_date"],
        info["clip_id"],
        info["start"],
        info["end"],
        args.output_dir
    )

    print(f"Clip Title : {info['title']}")
    print(f"Clip ID    : {info['clip_id']}")
    print(f"Video ID   : {info['video_id']}")
    print(f"Video URL  : {info['video_url']}")
    print(f"Start      : {info['start']}")
    print(f"End        : {info['end']}")
    print(f"Output     : {video_path}")

    #
    # Skip existing
    #

    if video_path.exists():

        print("\nClip already exists. Skipping.")
        print(video_path)

        return

    final_video = download_clip(
        info["video_url"],
        info["start"],
        info["end"],
        video_path,
        info["clip_id"],
        info["video_id"]
    )

    #
    # Save metadata
    #

    metadata = {
        "clip_id": info["clip_id"],
        "video_id": info["video_id"],
        "clip_url": clip_url,
        "video_url": info["video_url"],
        "title": info["title"],
        "start": info["start"],
        "end": info["end"],
        "downloaded_at": datetime.now().isoformat(),
        "video_file": str(final_video),
    }

    save_metadata(
        metadata_path,
        metadata
    )

    print(f"\nMetadata saved to:\n{metadata_path}")

    print("\nDone.")


if __name__ == "__main__":
    main()