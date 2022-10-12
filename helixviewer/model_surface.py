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
    if len(glob.glob(os.getcwd() + "/{}/*helix*.mod".format(dossier))) > 0 and dossier.find("segment") >= 0:
        dossiers_segments.append(dossier)
dossiers_segments.sort(key=num_sort)

procs = []
for dossier in dossiers_segments:
    path_iso = os.path.relpath(glob.glob(os.getcwd() + "/{dossier}/*AvgVol*.mrc".format(dossier=dossier))[-1])
    path_model = os.path.relpath(glob.glob(os.getcwd() + "/{dossier}/*helix*.mod".format(dossier=dossier))[0])
    command = "3dmod -S -ia 90,0,0 -V -E UC1 {path_iso} {path_mod}".format(path_iso=path_iso, path_mod=path_model)
    subprocess.run(command.split(" "))

print("All models have been opened.")
exit(0)
