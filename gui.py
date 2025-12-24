import webbrowser
import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk
import subprocess
import reader_helper as rh
from functools import partial

#file_path = Path("IMG_2697.mp4").absolute()
#webbrowser.open(file_path.as_uri())

filepath = rh.get_last_selected_path()
if filepath is not None and len(filepath) > 0:
    print("Using last selected path:", filepath)
TRACKER_FILE = "watched_videos.txt"

main_color = "#D7C097"
secondary_color = "#E7DEAF"
third_color = "#73AF6F"
accent_color="#007E6E"


def mark_as_watched(name):
    """
    Add a video filename to the tracker file if not already marked.
    """
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
                    "ffmpeg",
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
        btn.pack(side="left", padx=5, pady=5)

def display_selected_series(name, movie_display, dirpath):
    for widget in movie_display.winfo_children():
        widget.destroy()

    matching_files = rh.get_matching_files(name, dirpath)
    print("Matching files:", matching_files)

    for file in matching_files:
        file_path = Path(dirpath) / file
        thumbnail_path = Path("/tmp") / f"{file_path.stem}_thumb.jpg"

        # Generate thumbnail with ffmpeg if it doesn't exist
        if not thumbnail_path.exists():
            try:
                subprocess.run([
                    "ffmpeg",
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
        btn.pack(side="left", padx=5, pady=5)

def play_selected(name, dirpath):
    """
    Opens the selected video file in the default browser/media player.
    """
    file_path = Path(dirpath) / name  # join directory and filename
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


#train_var = StringVar()  
#k_var = IntVar(value=20)  
#nn_norm_var = IntVar(value=1)
#knn_k_var = IntVar(value=3)
#algo_var = StringVar(value="NN") 

# control panel ------
control_panel = tk.Frame(window, borderwidth=2,bg=main_color) 
control_panel.pack(fill="x")
control_panel.configure(height=50)
#control_panel.place(x=20, y=20, width=1360, height=100)

chose_file_btn =tk.Button(control_panel,text="Alege Fisier",borderwidth=0,width=30,command=open_file_browser,bg=secondary_color)
chose_file_btn.pack(side="left")
#chose_file_btn.place(x=10,y=10)


current_dir_label = tk.Label (control_panel,text="SELECTED",bg=main_color)
current_dir_label.pack(side="left")
#current_dir_label.place(x=10,y=50)



#-- movie_display
    
canvas = tk.Canvas(window, bg=secondary_color)
scrollbar = tk.Scrollbar(window, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

# Frame inside the canvas
movie_display = tk.Frame(canvas, bg=secondary_color, relief=tk.RAISED, borderwidth=0)
canvas.create_window((0, 0), window=movie_display, anchor="nw")

# Update scroll region whenever the frame changes
def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

#canvas.place(x=20, y=140, width=1360, height=550)
#scrollbar.place(x=1380, y=140, height=550)


if filepath is not None and len(filepath) > 0:
    current_dir_label.config(text= f"{filepath}")
    create_movie_display(movie_display,filepath)


return_btn =tk.Button(control_panel,text="<-",width=4,bg=secondary_color,command=partial(create_movie_display,movie_display,filepath))
return_btn.pack(side="right")

window.mainloop()
