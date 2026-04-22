#!/usr/bin/env python3
"""Convert a PNG in this directory to JPG, update the DB reference, delete the PNG."""

import sys
import os
import sqlite3
from pathlib import Path

DB_PATH = Path.home() / ".sacs" / "cases.db"
IMAGES_DIR = Path(__file__).parent


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {Path(sys.argv[0]).name} <filename.png>")
        sys.exit(1)

    src = Path(sys.argv[1])
    if not src.is_absolute():
        src = IMAGES_DIR / src

    if not src.exists():
        print(f"Error: {src} not found")
        sys.exit(1)

    if src.suffix.lower() != ".png":
        print(f"Error: {src.name} is not a .png file")
        sys.exit(1)

    dst = src.with_suffix(".jpg")
    if dst.exists():
        print(f"Error: {dst.name} already exists — remove it first")
        sys.exit(1)

    # Convert
    from PIL import Image
    img = Image.open(src).convert("RGB")
    img.save(dst, "JPEG", quality=92)
    print(f"Converted: {src.name} → {dst.name}")

    # Update DB
    old_name = src.name
    new_name = dst.name
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "UPDATE people SET photo=? WHERE photo=?", (new_name, old_name)
        )
        rows = cur.rowcount
        conn.commit()

    if rows:
        print(f"DB updated: {rows} row(s) in people.photo ({old_name} → {new_name})")
    else:
        print(f"Warning: no DB rows referenced {old_name} — check manually")

    # Delete original
    src.unlink()
    print(f"Deleted: {old_name}")


if __name__ == "__main__":
    main()
