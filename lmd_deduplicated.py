#!/usr/bin/env python3
"""Deduplicate MIDI files from lmd_clean directory by name.

This script scans a source directory (default ``lmd_clean``) and
copies one instance of each MIDI file name to a destination
``lmd_deduplicated`` directory. Files are copied preserving their
relative paths from the source.
"""

import argparse
import os
import shutil


def deduplicate(src_dir: str, dest_dir: str) -> int:
    """Copy unique MIDI files from ``src_dir`` to ``dest_dir``.

    Parameters
    ----------
    src_dir : str
        Directory to search for MIDI files.
    dest_dir : str
        Directory where unique files will be copied.

    Returns
    -------
    int
        Number of unique files copied.
    """
    seen = set()
    count = 0
    for dirpath, _, files in os.walk(src_dir):
        for name in files:
            if not name.lower().endswith('.mid'):
                continue
            if name in seen:
                continue
            seen.add(name)
            src_path = os.path.join(dirpath, name)
            rel_dir = os.path.relpath(dirpath, src_dir)
            dest_path_dir = os.path.join(dest_dir, rel_dir)
            os.makedirs(dest_path_dir, exist_ok=True)
            shutil.copy2(src_path, os.path.join(dest_path_dir, name))
            count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a deduplicated copy of an lmd_clean dataset by file name"
    )
    parser.add_argument(
        "src_dir",
        nargs="?",
        default="lmd_clean",
        help="Source directory containing MIDI files",
    )
    parser.add_argument(
        "dest_dir",
        nargs="?",
        default="lmd_deduplicated",
        help="Destination directory",
    )
    args = parser.parse_args()

    copied = deduplicate(args.src_dir, args.dest_dir)
    print(f"Copied {copied} unique MIDI files to {args.dest_dir}")


if __name__ == "__main__":
    main()
