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
import random

main_color      = "#141414"
secondary_color = "#141414"
third_color     = "#1F1F1F"
accent_color    = "#E50914"
fg = "#E5E5E5"
#file_path = Path("IMG_2697.mp4").absolute()
#webbrowser.open(file_path.as_uri())
def get_folder_icon(folder_path, width=120, height=80):
    """
    Returns a PhotoImage for a folder:
    - if exactly one PNG exists in the folder, use it
    - otherwise, generate a colored rectangle
    """
    folder_path = Path(folder_path)
    if not folder_path.is_dir():
        raise ValueError(f"{folder_path} is not a directory")

    # collect all PNG files
    png_files = list(folder_path.glob("*.png"))

    if len(png_files) == 1:
        img = Image.open(png_files[0])
        img.thumbnail((width, height))
    else:
        # None or multiple → random color placeholder
        color = "#" + "".join(random.choices("0123456789ABCDEF", k=6))
        img = Image.new("RGB", (width, height), color=color)

    return ImageTk.PhotoImage(img)

def get_video_icon(file_path, folder_icons):
    """
    Determine the icon for a video file.
    folder_icons: list of Path objects (png files in folder)
    """
    file_stem = file_path.stem

    if not folder_icons:
        # No png files → random color placeholder
        color = "#" + "".join(random.choices("0123456789ABCDEF", k=6))
        img = Image.new("RGB", (160, 90), color=color)
        return ImageTk.PhotoImage(img)

    if len(folder_icons) == 1:
        img = Image.open(folder_icons[0])
        img.thumbnail((160, 90))
        return ImageTk.PhotoImage(img)

    # Multiple pngs → try to find one with same name
    for icon_file in folder_icons:
        if icon_file.stem.lower() == file_stem.lower():
            img = Image.open(icon_file)
            img.thumbnail((160, 90))
            return ImageTk.PhotoImage(img)

    # fallback → first icon
    img = Image.open(folder_icons[0])
    img.thumbnail((160, 90))
    return ImageTk.PhotoImage(img)

def create_movie_card(parent, image, title, command,bgcolor =main_color):
    CARD_W = 180
    CARD_H = 260
    RADIUS = 18

    card = tk.Canvas(
        parent,
        width=CARD_W,
        height=CARD_H,
        bg=main_color,
        highlightthickness=0
    )

    # Shadow
    draw_round_rect(
        card,
        8, 10, CARD_W-2, CARD_H-2,
        r=RADIUS,
        fill="#000000",
        outline=""
    )

    # Card body
    body = draw_round_rect(
        card,
        0, 0, CARD_W-10, CARD_H-10,
        r=RADIUS,
        fill=bgcolor,
        outline=""
    )

    # Thumbnail
    img_id = card.create_image(
        (CARD_W-10)//2,
        90,
        image=image
    )

    # Title
    text_id = card.create_text(
        (CARD_W-10)//2,
        215,
        text=title,
        fill="white",
        font=("Segoe UI", 10, "bold"),
        width=CARD_W-30
    )

    # Click
    card.bind("<Button-1>", lambda e: command())

    # Hover animation
    def on_enter(e):
        card.scale("all", CARD_W//2, CARD_H//2, 1.06, 1.06)
        card.configure(cursor="hand2")

    def on_leave(e):
        card.scale("all", CARD_W//2, CARD_H//2, 1/1.06, 1/1.06)

    card.bind("<Enter>", on_enter)
    card.bind("<Leave>", on_leave)

    return card

def draw_round_rect(canvas, x1, y1, x2, y2, r, **kwargs):
    points = [
        x1+r, y1,
        x2-r, y1,
        x2, y1,
        x2, y1+r,
        x2, y2-r,
        x2, y2,
        x2-r, y2,
        x1+r, y2,
        x1, y2,
        x1, y2-r,
        x1, y1+r,
        x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

def layout_cards(container, cards):
    for w in container.winfo_children():
        w.grid_forget()

    CARD_W = 190
    PADDING = 20

    cols = max(container.winfo_width() // (CARD_W + PADDING), 1)

    row = col = 0
    for card in cards:
        card.grid(
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

SELECTED_DIR = ""




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
    for widget in movie_display.winfo_children():
        widget.destroy()

    unique_dirs = rh.get_unique_filenames(dirpath)
    print("Unique dirs:", unique_dirs)

    cards = []

    for name in unique_dirs:
        folder_path = Path(dirpath) / name
        if not folder_path.exists() or not folder_path.is_dir():
            continue

        photo = get_folder_icon(folder_path, width=160, height=90)

        # Netflix-style card
        card = create_movie_card(
            movie_display,
            image=photo,
            title=name,
            command=lambda n=name: display_selected_series(
                n, movie_display, dirpath
            ),
            bgcolor=third_color
        )
        card.image = photo  # prevent GC
        cards.append(card)

    # Layout cards in grid
    layout_cards(movie_display, cards)

    # Reflow on resize
    movie_display.bind(
        "<Configure>",
        lambda e: layout_cards(movie_display, cards)
    )

def display_selected_series(name, movie_display, dirpath):
    # Clear previous content
    for widget in movie_display.winfo_children():
        widget.destroy()

    folder_path = Path(dirpath) / name
    if not folder_path.exists() or not folder_path.is_dir():
        return

    matching_files = rh.get_matching_files(name, dirpath)
    print("Matching files:", matching_files)

    # Collect all png files in folder
    folder_icons = list(folder_path.glob("*.png"))

    cards = []

    for file in matching_files:
        file_path = Path(dirpath) / file
        photo = get_video_icon(file_path, folder_icons)

        watched = is_watched(file_path.name)
        bgcolor = accent_color if watched else third_color

        # Episode card
        card = create_movie_card(
            movie_display,
            image=photo,
            title=file_path.name,
            command=lambda f=file_path.name: play_selected(f, dirpath, name),
            bgcolor=bgcolor
        )

        card.image = photo
        cards.append(card)

    # Initial layout
    layout_cards(movie_display, cards)

    # Reflow on resize
    movie_display.bind(
        "<Configure>",
        lambda e: layout_cards(movie_display, cards)
    )

def play_selected(name, dirpath,dirname):
    """
    Opens the selected video file in the default browser/media player.
    """
    print(SELECTED_DIR)
    file_path = Path(dirpath) /dirname/ name  
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
control_panel.pack_propagate(False)  

# Button style
def create_styled_button(parent, text, command=None, width=160, height=40):
    canvas = tk.Canvas(
        parent,
        width=width,
        height=height,
        bg=parent["bg"],
        highlightthickness=0
    )

    radius = height // 2  # pill shape

    bg_normal = third_color
    bg_hover = main_color

    rect =draw_round_rect(
        canvas,
        2, 2, width-2, height-2,
        radius,
        fill=bg_normal,
        outline=""
    )

    label = canvas.create_text(
        width // 2,
        height // 2,
        text=text,
        fill="white",
        font=("Segoe UI", 10, "bold")
    )

    # Hover effects
    def on_enter(_):
        canvas.itemconfig(rect, fill=bg_hover)

    def on_leave(_):
        canvas.itemconfig(rect, fill=bg_normal)

    # Click
    def on_click(_):
        if command:
            command()

    canvas.bind("<Enter>", on_enter)
    canvas.bind("<Leave>", on_leave)
    canvas.bind("<Button-1>", on_click)

    canvas.configure(cursor="hand2")

    return canvas

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

def on_key_press(event):
    if event.keysym == "Up":
        canvas.yview_scroll(-1, "units")   # scroll up
    elif event.keysym == "Down":
        canvas.yview_scroll(1, "units")    # scroll down

# Bind to the main window
window.bind("<Up>", on_key_press)
window.bind("<Down>", on_key_press)

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


movie_display.bind(
    "<Configure>",
    lambda e: layout_cards(movie_display, movie_display.winfo_children())
)

window.bind("<MouseWheel>", lambda e: canvas.yview_scroll(-int(e.delta/120), "units"))
window.mainloop()


