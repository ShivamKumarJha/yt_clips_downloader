# YouTube Clips Downloader

A complete toolkit for scraping, downloading, and managing YouTube clips. Extract your favorite clips from YouTube, download them with metadata, and clean up orphaned or duplicate files.

## Overview

This repository provides a set of Python and JavaScript tools to:

- **Scrape clips** from YouTube's clip feed using Selenium
- **Export clip URLs** from any YouTube page via a browser console script
- **Download clips** as MP4 files with full metadata (title, timestamps, video ID)
- **Organize clips** automatically into year/month folders
- **Clean up** JSON files whose referenced video files are missing
- **Remove duplicate files** based on content hash

## Scripts

### `Yt-clips.py`

Selenium-based scraper that logs into YouTube and extracts all clips from `https://www.youtube.com/feed/clips`.

```bash
python Yt-clips.py
```

Outputs: `youtube_clips.csv`

> **Note**: Requires a Chrome profile with YouTube login. Configure the path in the script.

### `export-youtube-clips.js`

JavaScript snippet to run in your browser's dev console. Auto-scrolls the page and extracts all clip URLs as JSON.

**Usage:**
1. Navigate to any YouTube page containing clips (e.g., channel clips page)
2. Open DevTools (`F12`) → Console
3. Paste the script and press Enter
4. JSON file downloads automatically

### `Yt-clip-dl.py`

Core downloader for a single YouTube clip. Extracts clip metadata and downloads the corresponding video segment.

```bash
python Yt-clip-dl.py <clip_url> [--output-dir <dir>]
```

**Features:**
- Extracts clip ID, video ID, timestamps, and title
- Downloads only the clip segment (not the full video)
- Saves MP4 + JSON metadata
- Organizes files as: `output_dir/YYYY/MM/Title [start-end] [clip_id].mp4`
- Skips existing downloads

### `yt_dl_all_clips.py`

Batch downloader that processes a JSON file of clip URLs (from `export-youtube-clips.js`).

```bash
python yt_dl_all_clips.py clips.json --output-dir downloads
```

- Multi-threaded (16 concurrent downloads)
- Progress reporting for each clip

### `cleanup_json.py`

Scans a folder for JSON files (clip metadata) and deletes those whose `video_file` path no longer exists.

```bash
python cleanup_json.py /path/to/folder [--dry-run]
```

- Recursively finds all `.json` files
- Checks if the referenced video exists
- Deletes orphaned JSON files
- `--dry-run` shows what would be deleted

### `dedupe.py`

Finds and deletes duplicate files by SHA256 content hash.

```bash
python dedupe.py /path/to/folder [--dry-run]
```

- Recursively scans all files
- Keeps the first occurrence, deletes duplicates
- Handles any file type

## Requirements

Install dependencies:

```bash
pip install selenium webdriver-manager requests
```

**Additional tools required:**
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) – YouTube downloader
- [ffmpeg](https://ffmpeg.org/) – For downloading clip sections

Both must be available in your `PATH`.

## Workflow Example

1. **Collect clip URLs** – Run `export-youtube-clips.js` on a YouTube clips page
2. **Batch download** – `python yt_dl_all_clips.py clips.json`
3. **Clean up orphans** – `python cleanup_json.py clips/ --dry-run` (then without `--dry-run`)
4. **Remove duplicates** – `python dedupe.py clips/`

## File Structure

```
output_dir/
├── 2024/
│   ├── 01/
│   │   ├── Funny moment [120-145] [Ugkx123...].mp4
│   │   └── Funny moment [120-145] [Ugkx123...].json
│   └── 02/
│       └── ...
└── 2025/
    └── ...
```

Each JSON metadata file contains:
```json
{
  "clip_id": "Ugkx...",
  "video_id": "dQw4w9WgXcQ",
  "clip_url": "https://youtube.com/clip/...",
  "video_url": "https://youtube.com/watch?v=...",
  "title": "Clip title",
  "start": 120.5,
  "end": 145.2,
  "downloaded_at": "2025-01-15T10:30:00",
  "video_file": "path/to/video.mp4"
}
```

## License

MIT