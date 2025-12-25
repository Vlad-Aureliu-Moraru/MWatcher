#!/usr/bin/env python3
import os
from pathlib import Path

# Get current folder
current_dir = Path(__file__).parent.resolve()

# Executable and icon paths
exe_path = current_dir / "gui"   # or "gui.exe" if it's Windows; adjust if needed
icon_path = current_dir / "mwatcher.png"

# Desktop file location
desktop_dir = Path.home() / ".local/share/applications"
desktop_dir.mkdir(parents=True, exist_ok=True)
desktop_file = desktop_dir / "mwatcher.desktop"

# Create the .desktop file content
desktop_content = f"""[Desktop Entry]
Type=Application
Name=MWatcher
Exec={exe_path}
Icon={icon_path}
Terminal=false
Categories=Utility;Video;
Comment=Movie Player
"""

# Write to file
desktop_file.write_text(desktop_content)
print(f"Created desktop entry at {desktop_file}")
