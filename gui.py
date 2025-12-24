import webbrowser
import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk
import subprocess
import reader_helper as rh
from functools import partial
from tkinter import filedialog
import shutil
import sys

#file_path = Path("IMG_2697.mp4").absolute()
#webbrowser.open(file_path.as_uri())


def get_ffmpeg_path():
    # Try bundled ffmpeg (PyInstaller)
    if getattr(sys, 'frozen', False):
        bundled = Path(sys._MEIPASS) / "ffmpeg"
        if bundled.exists():
            return str(bundled)

    # Try system ffmpeg
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg

    return None

FFMPEG_PATH = get_ffmpeg_path()

filepath = rh.get_last_selected_path()
if filepath is not None and len(filepath) > 0:
    print("Using last selected path:", filepath)
TRACKER_FILE = "watched_videos.txt"

main_color = "#2C2C2C"       
secondary_color = "#522546"  
third_color = "#88304E"      
accent_color = "#F7374F" 


def mark_as_watched(name):
    tracker = Path(TRACKER_FILE)
    watched = set()
    if tracker.exists():
        watched = set(tracker.read_text().splitlines())

    if name not in watched:
        with tracker.open("a") as f:
            f.write(name + "\n")
        print(f"Marked as watched: {name}")

def is_watched(name):
    """
    Returns True if the video has already been watched.
    """
    tracker = Path(TRACKER_FILE)
    if not tracker.exists():
        return False
    watched = set(tracker.read_text().splitlines())
    return name in watched

def open_file_browser():
    root =tk.Tk()
    root.withdraw()  # Hide the main window
    folder_selected = filedialog.askdirectory(title="Select a folder")
    root.destroy()

    if folder_selected:
        rh.save_selected_path(folder_selected)
        print("New folder selected:", folder_selected)
        create_movie_display(movie_display,filepath)
        return folder_selected
    else:
        print("No folder selected")
        return None

def create_movie_display(movie_display, dirpath):
    if not FFMPEG_PATH:
        raise RuntimeError("ffmpeg not found")
    for widget in movie_display.winfo_children():
        widget.destroy()

    THUMB_W = 160
    PADDING = 12

    cols = max(movie_display.winfo_width() // (THUMB_W + PADDING), 1)

    row = col = 0
    unique_files = rh.get_unique_filenames(dirpath)
    print("Unique files:", unique_files)

    for name in unique_files:
        matching_files = rh.get_matching_files(name, dirpath)
        if not matching_files:
            continue

        first_file = Path(dirpath) / matching_files[0]
        thumbnail_path = Path("/tmp") / f"{first_file.stem}_thumb.jpg"

        if not thumbnail_path.exists():  
            try:
                subprocess.run([
                    FFMPEG_PATH,
                    "-y",  # overwrite
                    "-i", str(first_file),
                    "-ss", "00:00:01",  # seek 1 second into the video
                    "-vframes", "1",
                    "-vf", "scale=120:-1",  # width 120, keep aspect ratio
                    str(thumbnail_path)
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                print(f"Failed to create thumbnail for {first_file}: {e}")
                img = Image.new("RGB", (120, 80), color="gray")
                photo = ImageTk.PhotoImage(img)
        else:
            img = Image.open(thumbnail_path)
            photo = ImageTk.PhotoImage(img)

        if 'photo' not in locals():
            img = Image.open(thumbnail_path)
            photo = ImageTk.PhotoImage(img)

        btn_color = secondary_color
        btn = tk.Button(movie_display, image=photo,bg=btn_color,highlightthickness=0,borderwidth=0, text=name, compound="top", command=partial(display_selected_series,name,movie_display,filepath))
        btn.image = photo  
        btn.grid(
            row=row,
            column=col,
            padx=PADDING,
            pady=PADDING,
            sticky="n"
        )

        col += 1
        if col >= cols:
            col = 0
            row += 1

def display_selected_series(name, movie_display, dirpath):
    if not FFMPEG_PATH:
        raise RuntimeError("ffmpeg not found")
    for widget in movie_display.winfo_children():
        widget.destroy()

    THUMB_W = 160
    PADDING = 12

    cols = max(movie_display.winfo_width() // (THUMB_W + PADDING), 1)

    row = col = 0
    matching_files = rh.get_matching_files(name, dirpath)
    print("Matching files:", matching_files)

    for file in matching_files:
        file_path = Path(dirpath) / file
        thumbnail_path = Path("/tmp") / f"{file_path.stem}_thumb.jpg"

        if not thumbnail_path.exists():
            try:
                subprocess.run([
                    FFMPEG_PATH,
                    "-y",
                    "-i", str(file_path),
                    "-ss", "00:00:01",
                    "-vframes", "1",
                    "-vf", "scale=120:-1",
                    str(thumbnail_path)
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                print(f"Failed to create thumbnail for {file_path}: {e}")
                img = Image.new("RGB", (120, 80), color="gray")
                photo = ImageTk.PhotoImage(img)
        else:
            img = Image.open(thumbnail_path)
            photo = ImageTk.PhotoImage(img)

        if 'photo' not in locals():
            img = Image.open(thumbnail_path)
            photo = ImageTk.PhotoImage(img)

        btn_color = accent_color if is_watched(file_path.name) else secondary_color
        btn = tk.Button(movie_display,borderwidth=0,highlightthickness=0,activebackground=main_color, image=photo,bg=btn_color, text=file_path.name, compound="top",command=partial(play_selected,file_path.name,dirpath))
        btn.image = photo  # prevent garbage collection
        btn.grid(
            row=row,
            column=col,
            padx=PADDING,
            pady=PADDING,
            sticky="n"
        )

        col += 1
        if col >= cols:
            col = 0
            row += 1

def play_selected(name, dirpath):
    """
    Opens the selected video file in the default browser/media player.
    """
    file_path = Path(dirpath) / name  
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return

    # Convert to a file URI and open in browser
    webbrowser.open(file_path.resolve().as_uri())
    mark_as_watched(name)

window = tk.Tk()
window.geometry("1400x840")
window.title("MWatcher")
window.configure(bg=main_color)

# ===== CONTROL PANEL =====
control_panel = tk.Frame(window, bg=main_color, height=60)
control_panel.pack(fill="x", side="top")
control_panel.pack_propagate(False)  # prevent resizing to children

# Button style
def create_styled_button(parent, text, command=None):
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=secondary_color,
        fg="white",
        activebackground=third_color,
        activeforeground="white",
        relief="flat",
        borderwidth=0,
        padx=20,
        pady=8,
        font=("Segoe UI", 10, "bold"),
        cursor="hand2"
    )
    # Hover effect
    btn.bind("<Enter>", lambda e: btn.config(bg=third_color))
    btn.bind("<Leave>", lambda e: btn.config(bg=secondary_color))
    return btn

# "Choose File" button
choose_file_btn = create_styled_button(control_panel, "Alege Fisier", command=open_file_browser)
choose_file_btn.pack(side="left", padx=15, pady=10)

# Current directory label
current_dir_label = tk.Label(
    control_panel,
    text="SELECTED",
    bg=main_color,
    fg="white",
    font=("Segoe UI", 10)
)
current_dir_label.pack(side="left", padx=10)

#-- movie_display
    
canvas = tk.Canvas(
    window,
    bg=secondary_color,
    highlightthickness=0
)

scrollbar = tk.Scrollbar(
    window,
    orient=tk.VERTICAL,
    command=canvas.yview
)

canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

movie_display = tk.Frame(
    canvas,
    bg=secondary_color,
    borderwidth=0
)

canvas_window = canvas.create_window(
    (0, 0),
    window=movie_display,
    anchor="nw"
)


def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

movie_display.bind("<Configure>", on_frame_configure)

def on_canvas_configure(event):
    canvas.itemconfig(canvas_window, width=event.width)

canvas.bind("<Configure>", on_canvas_configure)


if filepath is not None and len(filepath) > 0:
    current_dir_label.config(text= f"{filepath}")
    create_movie_display(movie_display,filepath)


return_btn = create_styled_button(control_panel,text="<-",command=partial(create_movie_display,movie_display,filepath))
return_btn.pack(side="right")

window.mainloop()
