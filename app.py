import backend.file_content_module as fcm
import backend.chunk_process as cpm
import os
import subprocess
import glob
import time


# This is basically what automaticsegment.py was previously minus functions
# TODO
# automatic choice of particle per CPU, to do with optional arguments
# Graphical interface
# fix when file are not found (for example in splitIntoseg with the model pts added)
# Better PRM modification ==> DONE, need to be tested
# Possibly using shutil.which and replace all command with their direct path
# Allow for optional arguments as a way to modify the file
# Prepare unit testing file https://pymbook.readthedocs.io/en/latest/testing.html
# Alternatively, shell=False can be used when command is used as a list with arguments (see docu). Might help on W10
# Use subprocess.call in lancer prm parser and chunk to prevent starting chunk before parser has finished.
# popen.wait maybe can be useful too. exit_codes = [p.wait() for p in p1, p2] for multiple processes. Note that
# according to the python documentation subprocess.run waits for the process to end


def round_to_even(nombre):
    return round(nombre / 2.0) * 2


def modifier_prm(lines, base_name, segment_number, nb_particle, nb_search, pixel_size, tomo_path):
    volume_size = round_to_even(64 * 8.0 / pixel_size)  # Change 64 for different "base" size of box
    lines_to_change = [
        ("szVol = " + "[{sz}, {sz}, {sz}]".format(sz=volume_size) + "\n",
         fcm.search_string_in_file(lines, "szVol = ")),
        ("cylinder_height = " + str(volume_size) + "\n",
         fcm.search_string_in_file(lines, "cylinder_height = ")),
        ("insideMaskRadius = " + str(round(10 * 8.0 / pixel_size)) + "\n",
         fcm.search_string_in_file(lines, "insideMaskRadius = ")),
        ("outsideMaskRadius = " + str(round(28 * 8.0 / pixel_size)) + "\n",
         fcm.search_string_in_file(lines, "outsideMaskRadius = ")),
        ("refThreshold = " + "{" + (str(nb_particle) + ", ") * (nb_search - 1) + str(nb_particle) + "}" + "\n",
         fcm.search_string_in_file(lines, "refThreshold = ")),
        ("reference = " + "[1, " + str(round(nb_particle / 2)) + "]" + "\n",
         fcm.search_string_in_file(lines, "reference = [")),
        ("lstThresholds = " + "[{nbr}:{nbr}:{nbr}]".format(nbr=nb_particle) + "\n",
         fcm.search_string_in_file(lines, "lstThresholds = ")),
        ("fnVolume = {'../" + tomo_path + "'}\n",
         fcm.search_string_in_file(lines, "fnVolume = ")),
        ("fnOutput = '{}_S{}'\n".format(base_name, segment_number),
         fcm.search_string_in_file(lines, "fnOutput = "))]
    modified_prm = lines
    for (param, index) in lines_to_change:
        modified_prm = fcm.change_line(modified_prm, index, param)
    return modified_prm


def open_average(path_to_avg):
    commandToRun = "3dmod -V -E U " + path_to_avg
    subprocess.run(commandToRun, shell=True)


def run():
    print("everything is working as I intend and thats great")
    base_name_file = input("Enter the basename. For example : MTa will create MTa_S1, MTa_S2, etc... \n")
    nb_of_segment = int(input("Enter how many segment you want to generate :\n"))
    cpm.create_segments(nb_of_segment, base_name_file)
    prm_path = "./" + base_name_file + ".prm"
    ref_lines = fcm.open_file(prm_path)
    number_of_particle = fcm.get_number_of_particle(glob.glob(os.getcwd() + "/segment1/*RefP*.csv")[0])
    number_of_search = len(ref_lines[fcm.search_string_in_file(ref_lines, "dPhi = ")].split(","))
    pixel_spacing, path_to_tomo = fcm.determine_pixel_spacing(ref_lines)

    # First create all prm files then start the averaging

    for i in range(1, nb_of_segment + 1):
        new_file = modifier_prm(ref_lines, base_name_file, i, number_of_particle, number_of_search, pixel_spacing,
                                path_to_tomo)
        base_name_with_segment = base_name_file + '_S' + str(i)
        new_file_path = "./segment{number}/{filename}.prm".format(number=i, filename=base_name_with_segment)
        fcm.write_file(new_file_path, new_file)

    # Averaging

    all_procs = []
    for i in range(1, nb_of_segment + 1):
        cpm.lancer_parser_segment(base_name_with_segment, i)
        # ProcessChunk will not start until parser has finished
        all_procs.append(cpm.lancer_process_chunk_segment(base_name_file, i))

    # Wait for all process to end before ending program

    for process in all_procs:
        process.communicate(timeout=3600)
    print("All segments have been generated")

    show_surface = int(input("Would you like to see all isosurface ? 1 for yes 2 for no\n"))
    if show_surface == 1:
        for i in range(1, nb_of_segment + 1):
            avg_path = glob.glob("./segment{num}/{name}_S{num}_AvgVol_*.mrc".format(num=i, name=baseNameFile))[0]
            open_average(avg_path)
            time.sleep(1)
        print("All segments have been opened")
