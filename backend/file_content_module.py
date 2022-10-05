import subprocess


def open_file(baseName):
    """This command returns the text file content as a list
    :param baseName: path as a string
    :return: a list of lines
    """
    file = open(baseName, 'r')
    lines = file.readlines()
    file.close()
    return lines


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
    file = open(path, 'w')
    file.writelines(content)
    file.close()
    return True


def get_number_of_particle(pathToMotivList):
    """Return the number of lines in a file minus 1, because csv first line is for headers"""
    return len(open_file(pathToMotivList)) - 1


def determine_pixel_spacing(lines: list) -> float and str:
    """Return the pixel size in a tomogram as well as the path to said tomogram"""
    tomo_path = lines[search_string_in_file(lines, "fnVolume = ")].split("'")[1]
    # if not os.path.exists(tomo_path):
    #     root = tk.Tk()
    #     root.withdraw()
    #     tomo_path = os.path.relpath(filedialog.askopenfilename(initialdir=os.getcwd()))
    command = "header -p " + tomo_path
    output = subprocess.run(command, shell=True, capture_output=True, text=True).stdout
    output = output.strip()
    pixel = output.split()[0]
    return float(pixel), tomo_path
