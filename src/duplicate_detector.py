import hashlib
from pathlib import Path

from extractor import DATA_DIR


def calculate_hash(file_path: Path) -> str:
    """Generate a SHA-256 fingerprint of a file."""

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def find_duplicates(directory: Path) -> list:
    """Identify files with identical content."""

    seen = {}
    duplicates = []

    for file_path in sorted(directory.glob("*.pdf")):

        file_hash = calculate_hash(file_path)

        if file_hash in seen:

            duplicates.append({
                "original": seen[file_hash],
                "duplicate": file_path.name
            })

        else:
            seen[file_hash] = file_path.name

    return duplicates


if __name__ == "__main__":

    duplicates = find_duplicates(DATA_DIR)

    print("=" * 50)
    print("DUPLICATE DOCUMENT DETECTION")
    print("=" * 50)

    for item in duplicates:
        print(f"Original:  {item['original']}")
        print(f"Duplicate: {item['duplicate']}")
        print("-" * 50)

    print(f"Total duplicates found: {len(duplicates)}")
