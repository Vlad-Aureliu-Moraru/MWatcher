import re
from pathlib import Path
from os.path import commonprefix
from itertools import groupby
from collections import defaultdict
from difflib import SequenceMatcher

VIDEO_EXTS = (".mp4", ".mkv", ".avi")

def read_directory_files(dirpath, dirs=False):
    path = Path(dirpath)

    if not path.is_dir():
        raise ValueError(f"{dirpath} is not a valid directory")

    if dirs:
        return [p.name for p in path.iterdir() if p.is_dir()]
    else:
        return [
            p.name
            for p in path.iterdir()
            if p.is_file() and p.suffix.lower() in VIDEO_EXTS]

def get_unique_filenames(dirpath):
    """
    Returns only directory names (series).
    """
    return read_directory_files(dirpath, dirs=True)

def get_matching_files(name, dirpath):
    """
    Returns all .mp4 files inside: dirpath/name
    """
    base_path = Path(dirpath)
    series_path = base_path / name

    if not series_path.exists() or not series_path.is_dir():
        raise ValueError(f"{series_path} is not a valid directory")

    return [
        f.name
        for f in series_path.iterdir()
        if f.is_file() and f.suffix.lower() == ".mp4"
    ]

def save_selected_path(path, filename="selected_paths.txt"):
    with open(filename, "w") as f:
        f.write(path + "\n")

def get_last_selected_path(filename="selected_paths.txt"):
    try:
        with open(filename, "r") as f:
            path = f.readline().strip()
            return path if path else None
    except FileNotFoundError:
        return None

# Example usage
last_path = get_last_selected_path()
if last_path:
    print("Last selected path:", last_path)
else:
    print("No previously selected path found")



