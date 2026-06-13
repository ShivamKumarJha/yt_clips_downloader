import hashlib
from pathlib import Path
import argparse


def file_hash(path, chunk_size=1024 * 1024):
    """
    Compute SHA256 hash of a file.
    """

    sha256 = hashlib.sha256()

    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            sha256.update(chunk)

    return sha256.hexdigest()


def find_duplicates(folder):
    """
    Find duplicate files by content hash.
    """

    hashes = {}
    duplicates = []

    for path in Path(folder).rglob("*"):

        if not path.is_file():
            continue

        try:
            h = file_hash(path)

            if h in hashes:
                duplicates.append((path, hashes[h]))
            else:
                hashes[h] = path

        except Exception as e:
            print(f"Failed: {path}")
            print(e)

    return duplicates


def delete_duplicates(duplicates, dry_run=False):
    """
    Delete duplicate files.
    Keeps the first file found.
    """

    deleted = 0

    for dup, original in duplicates:

        print(f"\nDuplicate:")
        print(f"DELETE : {dup}")
        print(f"KEEP   : {original}")

        if not dry_run:
            try:
                dup.unlink()
                deleted += 1

            except Exception as e:
                print(f"Could not delete {dup}")
                print(e)

    return deleted


def main():

    parser = argparse.ArgumentParser(
        description="Delete duplicate files"
    )

    parser.add_argument(
        "folder",
        help="Folder to scan"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show duplicates without deleting"
    )

    args = parser.parse_args()

    folder = Path(args.folder)

    if not folder.exists():
        print("Folder does not exist")
        return

    print(f"Scanning: {folder}\n")

    duplicates = find_duplicates(folder)

    if not duplicates:
        print("No duplicates found")
        return

    print(f"\nFound {len(duplicates)} duplicate files")

    deleted = delete_duplicates(
        duplicates,
        dry_run=args.dry_run
    )

    if args.dry_run:
        print("\nDry run complete")
    else:
        print(f"\nDeleted {deleted} duplicate files")


if __name__ == "__main__":
    main()