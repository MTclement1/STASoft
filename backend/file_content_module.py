import subprocess
import tkinter as tk
import os
from tkinter import filedialog
import datetime
import glob


def open_file(path):
    """This command returns the text file content as a list
    :param path: string from the path
    :return: a list of lines or None
    """
    try:
        with open(path, 'r') as file:
            lines = file.readlines()
            file.close()
            return lines
    except FileNotFoundError:
        return None


def search_string_in_file(fileContent, aStringToFind):
    """Get line numbers, which contains any string from the list"""
    line_number = 0
    for line in fileContent:
        # For each line, check if line contains any string from the list of strings
        if aStringToFind in line:
            # If any string is found in line, then append that line along with line number in list
            return line_number
        line_number += 1
    # Return list of tuples containing matched string, line numbers and lines where string is found
    raise Exception("Sorry, a line containing {} was not found".format(aStringToFind))


def change_line(lines, index, replacement):
    """Replace a line in a file stored as a line
    :param lines: file content as list of lines
    :param index: int
    :param replacement: string
    """
    lines[index] = replacement
    return lines


def write_file(path, content):
    """Write a file given a path (including its name) and a content as list of string each representing a line
    :param path: string
    :param content: list of string
    """
    with open(path, 'w') as file:
        file.writelines(content)
        file.close()
    return True


def get_number_of_particle(pathToMotivList):
    """Return the number of lines in a file minus 1, because csv first line is for headers"""
    return len(open_file(pathToMotivList)) - 1


def determine_pixel_spacing(tomo_path):
    """Return the pixel size in a tomogram as well as the path to said tomogram"""
    if not os.path.exists(tomo_path):
        root = tk.Tk()
        root.withdraw()
        tomo_path = os.path.relpath(filedialog.askopenfilename(initialdir='../',
                                                               filetypes=[('Volumes', '.mrc'), ('All types', '*.*')],
                                                               title="Please select the tomogram volume file"))
        root.update()
        root.destroy()
    command = "header -p " + tomo_path
    output = subprocess.run(command.split(" "), capture_output=True, text=True).stdout
    output = output.strip()
    pixel = output.split()[0]
    return float(pixel), tomo_path


def get_tilt_range(path):
    with open(path, 'r') as file:
        lines = file.readlines()
        file.close()
        min_angle = lines[0].rstrip()[1:]
        max_angle = lines[len(lines) - 1].rstrip()[2:]
    return min_angle, max_angle


def log_file_append(CompletedProcess, log_file_path='./logfile_except_chunks.log'):
    """
    Create a local log file and append log messages to it.

    Parameters:
    - CompletedProcess (CompletedProcess): An object returned at the end of subprocess.run command.
    - log_file_path (str): Path to the log file. Default is 'logfile_except_chunks.log'.
    """
    # Extract the stdout from the CompletedProcess object
    message = CompletedProcess.stdout.strip()  # Ensure leading/trailing whitespaces are removed

    # Get the current timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Log message format: [TIMESTAMP] Message
    log_message = f"[{timestamp}] {message}\n"

    # Open the log file in append mode or create if it doesn't exist
    with open(log_file_path, 'a') as log_file:
        # Append the log message to the file
        log_file.write(log_message)
        log_file.close()


def cleanup(wd, base_name, list_del=False):
    """
    Delete most file that are rarely used after averaging
    """
    os.chdir(wd)
    # Removing first files with ~ because it can cause issues with files to keep
    files_to_remove = glob.glob('*~')
    for file_path in files_to_remove:
        try:
            os.remove(file_path)
        except OSError as e:
            print(f"Error removing {file_path}: {e}")
            pass
    files_to_keep = ["prmParser.log", f"{base_name}.prm", f"{base_name}_WarningsAndErrors.log", f"{base_name}.mod",
                     os.path.basename(glob.glob("*TotalLog_*")[0]),
                     os.path.basename(glob.glob("*_AvgVol_*P*.mrc*")[-1]),
                     os.path.basename(glob.glob("*_PtsAddedRefP*_initMOTL.csv")[0]),
                     os.path.basename(glob.glob("*_PtsAdded_Twisted.mod")[0]),
                     f"{base_name}-finish.log"]
    all_files = os.listdir(wd)
    deleted_files = []
    for file in all_files:
        file_path = os.path.join(wd, file)
        if file in files_to_keep:
            continue
        else:
            try:
                os.remove(file_path)
                deleted_files.append(file)
            except OSError:
                pass
    if list_del:
        with open(os.path.join(wd, "deletedFiles.txt"), 'a') as log:
            print("Saving the name of deleted files")
            for file in deleted_files:
                log.writelines(file)
                log.write('\n')
