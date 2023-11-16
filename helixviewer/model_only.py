import subprocess
import os
import glob
import re
import tkinter as tk


def num_sort(test_string):
    return list(map(int, re.findall(r'\d+', test_string)))[0]


def screen_size():
    root = tk.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.destroy()
    return width, height


list_dossier = os.listdir()
dossiers_segments = []
# Find folders containing helix
for dossier in list_dossier:
    if len(glob.glob(os.getcwd() + "/{}/*helix*.mod".format(dossier))) > 0 and dossier.find("segment") >= 0:
        dossiers_segments.append(dossier)
dossiers_segments.sort(key=num_sort)
width, height = screen_size()
# Adding a 5% margin on the screen

width = width - 0.05 * width
height = height - 0.05 * height

# Finding width

min_width = width / 8
optimal_size = width / len(dossiers_segments)
if optimal_size < min_width:
    optimal_size = min_width

# Making sure we can open at least two lines of models

max_height = height / 2
if optimal_size > max_height:
    optimal_size = max_height

position_x = 0
position_y = 50
procs = []
for dossier in dossiers_segments:
    path = os.path.relpath(glob.glob(os.getcwd() + "/{dossier}/*helix*.mod".format(dossier=dossier))[0])
    command = "3dmodv -qwindowgeometry +{x}+{y} -s {size},{size} {path}".format(x=position_x, y=position_y,
                                                                                   size=round(optimal_size), path=path)
    subprocess.run(command.split(" "))
    position_x += round(optimal_size)
    if position_x + optimal_size > width:
        position_x = 0
        position_y += round(optimal_size) + 23  # Need to account for size of window title

print("All models have been opened.")
exit(0)
