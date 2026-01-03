from pathlib import Path

VIDEO_EXTS = (".mp4", ".mkv", ".avi")

# --------------------------
# Directory utilities
# --------------------------
def read_directory_files(dirpath, dirs=False):
    """
    Returns list of files or directories in a given path.
    - dirs=True: returns directories only
    - dirs=False: returns video files only
    """
    path = Path(dirpath)
    if not path.is_dir():
        raise ValueError(f"{dirpath} is not a valid directory")

    if dirs:
        return [p.name for p in path.iterdir() if p.is_dir()]
    else:
        return [p.name for p in path.iterdir() if p.is_file() and p.suffix.lower() in VIDEO_EXTS]

# --------------------------
# Series / Seasons / Files
# --------------------------
def get_series(repository_path):
    """
    Returns all series (top-level directories in repository)
    """
    return read_directory_files(repository_path, dirs=True)

def get_seasons(series_path):
    """
    Returns all seasons (subdirectories inside series)
    """
    return sorted(read_directory_files(series_path, dirs=True), key=lambda x: x.lower())

def get_files(season_path):
    """
    Returns all video files inside a season directory
    """
    return read_directory_files(season_path, dirs=False)

# --------------------------
# Series icons
# --------------------------
def get_series_icon(series_path):
    """
    Returns the path to icon.png if exists, else None
    """
    icon_file = Path(series_path) / "icon.png"
    return icon_file if icon_file.exists() else None

def get_series_bg(series_path):
    """
    Returns the path to bg.png if exists, else None
    """
    bg_file = Path(series_path) / "bg.png"
    return bg_file if bg_file.exists() else None

# --------------------------
# Last selected folder persistence
# --------------------------
def save_selected_path(path, filename="selected_paths.txt"):
    with open(filename, "w") as f:
        f.write(str(path) + "\n")

def get_last_selected_path(filename="selected_paths.txt"):
    try:
        with open(filename, "r") as f:
            path = f.readline().strip()
            return path if path else None
    except FileNotFoundError:
        return None

# --------------------------
# Example usage
# --------------------------
if __name__ == "__main__":
    last_path = get_last_selected_path()
    if last_path:
        print("Last selected path:", last_path)
    else:
        print("No previously selected path found")
