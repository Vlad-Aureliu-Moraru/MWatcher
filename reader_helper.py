import re
from pathlib import Path
from os.path import commonprefix

def read_directory_files(dirpath):
    path = Path(dirpath)
    if not path.is_dir():
        raise ValueError(f"{dirpath} is not a valid directory")
    return [f.name for f in path.iterdir() if f.is_file() and f.suffix.lower() in (".mp4", ".mkv", ".avi")]

def get_unique_filenames(dirpath):
    files = read_directory_files(dirpath)

    ep_pattern = re.compile(r"(S\d+E\d+|s\d+e\d+|\d{1,2}x\d{1,2})")

    cleaned_files = []
    for file in files:
        name = file.rsplit('.', 1)[0]  
        name = ep_pattern.sub("", name)  
        cleaned_files.append(name)

    unique_names = []

    while cleaned_files:
        current = cleaned_files.pop(0)
        group = [current]

        for other in cleaned_files[:]:
            prefix = commonprefix([current, other])
            if any(c.isalpha() for c in prefix):
                group.append(other)
                cleaned_files.remove(other)

        if group:
            prefix = commonprefix(group)
            prefix = re.sub(r'\d+$', '', prefix)  
            if prefix:
                unique_names.append(prefix)

    unique_names = list(set(unique_names))
    return unique_names

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


