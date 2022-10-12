import subprocess
import os
import glob
import re
import tkinter as tk


def num_sort(test_string):
    return list(map(int, re.findall(r'\d+', test_string)))[0]


list_dossier = os.listdir()
dossiers_segments = []
# Find folders containing helix
for dossier in list_dossier:
    if len(glob.glob(os.getcwd() + "/{}/*AvgVol*.mrc".format(dossier))) > 0 and dossier.find("segment") >= 0:
        dossiers_segments.append(dossier)
dossiers_segments.sort(key=num_sort)

for dossier in dossiers_segments:
    path_iso = os.path.relpath(glob.glob(os.getcwd() + "/{dossier}/*AvgVol*.mrc".format(dossier=dossier))[-1])
    command = "3dmod -S -ia 90,0,0 -V -E UO1 {path_iso}".format(path_iso=path_iso)
    subprocess.run(command.split(" "))

print("All models have been opened.")
exit(0)
