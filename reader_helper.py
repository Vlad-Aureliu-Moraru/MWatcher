import re
from pathlib import Path
from os.path import commonprefix
from itertools import groupby
from collections import defaultdict
from difflib import SequenceMatcher

def read_directory_files(dirpath):
    path = Path(dirpath)
    if not path.is_dir():
        raise ValueError(f"{dirpath} is not a valid directory")
    return [f.name for f in path.iterdir() if f.is_file() and f.suffix.lower() in (".mp4", ".mkv", ".avi")]

def get_unique_filenames(dirpath, min_common_length=3):
    
   files = read_directory_files(dirpath)
   base_counts = {}

   for i in range(len(files)):
        name1 = files[i].rsplit('.', 1)[0]
        for j in range(i + 1, len(files)):
            name2 = files[j].rsplit('.', 1)[0]
            matcher = SequenceMatcher(None, name1, name2)
            for block in matcher.get_matching_blocks():
                if block.size >= min_common_length:
                    sub = name1[block.a:block.a + block.size]
                    base_counts[sub] = base_counts.get(sub, 0) + 1

    # only keep substrings that occur more than once
   unique_bases = [k for k, v in base_counts.items() if v > 0]

    # sort by length descending
   unique_bases.sort(key=lambda x: -len(x))

   return unique_bases

def get_matching_files(Name, dirpath):
    path = Path(dirpath)
    if not path.is_dir():
        raise ValueError(f"{dirpath} is not a valid directory")

    return [f.name for f in path.iterdir() if f.is_file() 
            and f.name.lower().endswith(".mp4") 
            and f.name.startswith(Name)]

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


dirpath = "."
uniques = get_unique_filenames(dirpath)
print(uniques)

