import backend.file_content_module as fcm
import backend.chunk_process as cpm
import backend.default_param as dft
import os
import subprocess
import glob
import time
import math
import threading
from config import current_wd as start_wd


# TODO
# Graphical interface
# Possibly using shutil.which and replace all command with their direct path

def round_to_even(nombre):
    return round(nombre / 2.0) * 2


def modifier_prm(lines, lines_to_change):
    modified_prm = lines
    for (param, index) in lines_to_change:
        modified_prm = fcm.change_line(modified_prm, index, param)
    return modified_prm


def open_average(path_to_avg):
    command_to_run = ["3dmod", "-V", "-E", "U ", path_to_avg]
    subprocess.run(command_to_run)


def generate_main_mt_prm(ref_lines, base_name, number_cpu, number_of_particle, pixel_size, path_tomo):
    lines_to_change = []
    cpu = math.ceil(number_of_particle / number_cpu)
    choice = int(input("Do you want to add another search angle (for rotations >= 12 °) ?\n"
                       "0 for no \n"
                       "1 for in plane rotation only\n"
                       "2 for out of plane rotation only\n"
                       "3 for both\n"))
    if choice == 0:
        phi = 'dPhi = {-9:6:9, -4.5:3:4.5, -2.3:1.5:2.3, -1:1:1}\n'
        sradius = ('searchRadius = {[' + str(round(5 * 8 / pixel_size)) + '],[' + str(round(4 * 8 / pixel_size)) + '],['
                   + str(round(2 * 8 / pixel_size)) + '],[' + str(round(1 * 8 / pixel_size)) + ']}\n')
    elif choice == 1:
        phi = 'dPhi = {0:1:0, -9:6:9, -4.5:3:4.5, -2.3:1.5:2.3, -1:1:1}\n'
        psi = 'dPsi = {0:1:0, -9:6:9, -4.5:3:4.5, -2.3:1.5:2.3, -1:1:1}\n'
        theta = 'dTheta = {-15:5:15, -9:6:9, -4.5:3:4.5, -2.3:1.5:2.3, -1:1:1}\n'
        sradius = ('searchRadius = {[' + str(round(6 * 8 / pixel_size)) + '],['
                   + str(round(5 * 8 / pixel_size)) + '],[' + str(round(4 * 8 / pixel_size)) + '],['
                   + str(round(2 * 8 / pixel_size)) + '],[' + str(round(1 * 8 / pixel_size)) + ']}\n')
        lines_to_change.append((psi, fcm.search_string_in_file(ref_lines, "dPsi = ")))
        lines_to_change.append((theta, fcm.search_string_in_file(ref_lines, "dTheta = ")))
    elif choice == 2:
        phi = 'dPhi = {0:1:0, -9:6:9, -4.5:3:4.5, -2.3:1.5:2.3, -1:1:1}\n'
        theta = 'dTheta = {0:1:0, -9:6:9, -4.5:3:4.5, -2.3:1.5:2.3, -1:1:1}\n'
        psi = 'dPsi = {-15:5:15, -9:6:9, -4.5:3:4.5, -2.3:1.5:2.3, -1:1:1}\n'
        sradius = ('searchRadius = {[' + str(round(6 * 8 / pixel_size)) + '],['
                   + str(round(5 * 8 / pixel_size)) + '],[' + str(round(4 * 8 / pixel_size)) + '],['
                   + str(round(2 * 8 / pixel_size)) + '],[' + str(round(1 * 8 / pixel_size)) + ']}\n')
        lines_to_change.append((psi, fcm.search_string_in_file(ref_lines, "dPsi = ")))
        lines_to_change.append((theta, fcm.search_string_in_file(ref_lines, "dTheta = ")))
    elif choice == 3:
        phi = 'dPhi = {0:1:0, -9:6:9, -4.5:3:4.5, -2.3:1.5:2.3, -1:1:1}\n'
        theta = 'dTheta = {-15:5:15, -9:6:9, -4.5:3:4.5, -2.3:1.5:2.3, -1:1:1}\n'
        psi = 'dPsi = {-15:5:15, -9:6:9, -4.5:3:4.5, -2.3:1.5:2.3, -1:1:1}\n'
        sradius = ('searchRadius = {[' + str(round(6 * 8 / pixel_size)) + '],['
                   + str(round(5 * 8 / pixel_size)) + '],[' + str(round(4 * 8 / pixel_size)) + '],['
                   + str(round(2 * 8 / pixel_size)) + '],[' + str(round(1 * 8 / pixel_size)) + ']}\n')
        lines_to_change.append((psi, fcm.search_string_in_file(ref_lines, "dPsi = ")))
        lines_to_change.append((theta, fcm.search_string_in_file(ref_lines, "dTheta = ")))
    else:
        print("This is not a possible answer to the question. Program will exit")
        exit(1)

    volume_size = round_to_even(64 * 8.0 / pixel_size)
    number_of_search = len(phi.split(","))
    if not glob.glob(os.path.dirname(path_tomo) + '/*DualAxisMask.mrc'):
        try:
            tilt_angles = fcm.get_tilt_range(glob.glob(os.path.dirname(path_tomo) + '/*.tlt')[0])
        except IndexError:
            print("Could not find any file following the structure : *.tlt in tomogram folder please fix and retry\n")
            exit(2)
    else:
        try:
            tilt_angles = os.path.abspath(glob.glob(os.path.dirname(path_tomo) + '/*DualAxisMask.mrc')[0])
        except IndexError:
            print("Could not find any file following the structure : *DualAxisMask.mrc in tomogram folder please "
                  "fix and retry\n")
            exit(2)
    path_mod = os.path.relpath(glob.glob(os.getcwd() + "/*Twisted.mod")[0])
    path_motiv = os.path.relpath(glob.glob(os.getcwd() + "/*initMOTL.csv")[0])

    lines_to_change.append(("fnVolume = {'" + path_tomo + "'}\n",
                            fcm.search_string_in_file(ref_lines, "fnVolume = ")))
    lines_to_change.append(("fnModParticle = {'" + path_mod + "'}\n",
                            fcm.search_string_in_file(ref_lines, "fnModParticle = ")))
    lines_to_change.append(("initMOTL = {'" + path_motiv + "'}\n",
                            fcm.search_string_in_file(ref_lines, "initMOTL = ")))
    if isinstance(tilt_angles, tuple):
        lines_to_change.append(("tiltRange = {[" + tilt_angles[0] + ", " + tilt_angles[1] + "]}\n",
                                fcm.search_string_in_file(ref_lines, "tiltRange = {[")))
    else:
        lines_to_change.append(("tiltRange = {'" + tilt_angles + "'}\n",
                                fcm.search_string_in_file(ref_lines, "tiltRange = {")))
    lines_to_change.append((phi,
                            fcm.search_string_in_file(ref_lines, "dPhi = ")))
    lines_to_change.append((sradius,
                            fcm.search_string_in_file(ref_lines, "searchRadius = ")))
    lines_to_change.append(("lowCutoff = {" + "[0, 0.05], " * (number_of_search - 1) + "[0, 0.05]}\n",
                            fcm.search_string_in_file(ref_lines, "lowCutoff =")))
    lines_to_change.append(("hiCutoff = {" + "[0.1, 0.05], " * (number_of_search - 1) + "[0.1, 0.05]}\n",
                            fcm.search_string_in_file(ref_lines, "hiCutoff =")))  # Potentially adapt for bin1
    lines_to_change.append(("refThreshold = {" + (str(number_of_particle) + ", ") * (number_of_search - 1) + str(
        number_of_particle) + "}\n",
                            fcm.search_string_in_file(ref_lines, "refThreshold = ")))
    lines_to_change.append(("duplicateShiftTolerance = " + "[NaN], " * (number_of_search - 1) + "[NaN]\n",
                            fcm.search_string_in_file(ref_lines, "duplicateShiftTolerance = ")))
    lines_to_change.append(("duplicateAngularTolerance = " + "[NaN], " * (number_of_search - 1) + "[NaN]\n",
                            fcm.search_string_in_file(ref_lines, "duplicateAngularTolerance = ")))
    lines_to_change.append(("reference = " + "[1, " + str(round(number_of_particle / 2)) + "]" + "\n",
                            fcm.search_string_in_file(ref_lines, "reference = [")))
    lines_to_change.append(("fnOutput = '{}'\n".format(base_name),
                            fcm.search_string_in_file(ref_lines, "fnOutput = ")))
    lines_to_change.append(("szVol = " + "[{sz}, {sz}, {sz}]".format(sz=volume_size) + "\n",
                            fcm.search_string_in_file(ref_lines, "szVol = ")))
    lines_to_change.append(("lstThresholds = " + "[{nbr}:{nbr}:{nbr}]".format(nbr=number_of_particle) + "\n",
                            fcm.search_string_in_file(ref_lines, "lstThresholds = ")))
    lines_to_change.append(("particlePerCPU = " + str(cpu) + "\n",
                            fcm.search_string_in_file(ref_lines, "particlePerCPU = ")))
    lines_to_change.append(("insideMaskRadius = " + str(round(10 * 8.0 / pixel_size)) + "\n",
                            fcm.search_string_in_file(ref_lines, "insideMaskRadius = ")))
    lines_to_change.append(("outsideMaskRadius = " + str(round(28 * 8.0 / pixel_size)) + "\n",
                            fcm.search_string_in_file(ref_lines, "outsideMaskRadius = ")))
    lines_to_change.append(("cylinderHeight = " + str(volume_size) + "\n",
                            fcm.search_string_in_file(ref_lines, "cylinderHeight = ")))
    return lines_to_change


def generate_segments_prm(lines, base_name, segment_number, number_cpu, number_of_particle, number_of_search,
                          tomo_path, volume_size, pixel_spacing):
    motiv_path = os.path.basename(glob.glob(os.getcwd() + "/segment{}/*RefP*.csv".format(segment_number))[0])
    mod_path = os.path.basename(glob.glob(os.getcwd() + "/segment{}/*Twisted.mod".format(segment_number))[0])
    cpu = math.ceil(number_of_particle / number_cpu)
    lines_to_change = [("fnOutput = '{}_S{}'\n".format(base_name, segment_number),
                        fcm.search_string_in_file(lines, "fnOutput = ")),
                       ("fnModParticle = {'" + mod_path + "'}\n",
                        fcm.search_string_in_file(lines, "fnModParticle = ")),
                       ("initMOTL = {'" + motiv_path + "'}\n",
                        fcm.search_string_in_file(lines, "initMOTL = ")),
                       ("szVol = " + "[{sz}, {sz}, {sz}]".format(sz=volume_size) + "\n",
                        fcm.search_string_in_file(lines, "szVol = ")),
                       ("cylinderHeight = " + str(volume_size) + "\n",
                        fcm.search_string_in_file(lines, "cylinderHeight = ")),
                       ("insideMaskRadius = " + str(round(10 * 8.0 / pixel_spacing)) + "\n",
                        fcm.search_string_in_file(lines, "insideMaskRadius = ")),
                       ("outsideMaskRadius = " + str(round(28 * 8.0 / pixel_spacing)) + "\n",
                        fcm.search_string_in_file(lines, "outsideMaskRadius = ")),
                       ("refThreshold = " + "{" + (str(number_of_particle) + ", ") * (number_of_search - 1) + str(
                           number_of_particle) + "}" + "\n",
                        fcm.search_string_in_file(lines, "refThreshold = ")),
                       ("reference = " + "[1, " + str(round(number_of_particle / 2)) + "]" + "\n",
                        fcm.search_string_in_file(lines, "reference = [")),
                       ("lstThresholds = " + "[{nbr}:{nbr}:{nbr}]".format(nbr=number_of_particle) + "\n",
                        fcm.search_string_in_file(lines, "lstThresholds = ")),
                       ("fnVolume = {'../" + tomo_path + "'}\n",
                        fcm.search_string_in_file(lines, "fnVolume = ")),
                       ("particlePerCPU = " + str(cpu) + "\n",
                        fcm.search_string_in_file(lines, "particlePerCPU = "))]
    return lines_to_change


def run(number_core, seg_only, no_seg, no_cleanup):
    # os.chdir("/Volumes/SSD_2To/TestSTASOft/MTa") # For debugging only
    all_procs = []
    stop_threads = threading.Event()
    lock = threading.Lock()
    try:
        path_to_mtv_list = os.path.relpath(glob.glob("*RefP*.csv")[0])
    except IndexError:
        print("Could not find any motiv list following the structure name : *RefP*.csv please fix and retry\n")
        exit(2)
    try:
        os.path.exists(os.path.relpath(glob.glob("*Twisted.mod")[0]))
    except IndexError:
        print('Could not find any model file with name structure : *Twisted.mod please fix and retry \n')
        exit(2)

    # Get basic information on microtubule and tomogram
    total_particle = fcm.get_number_of_particle(path_to_mtv_list)
    base_name_file = input("Enter the basename. For example : MTa will create MTa_S1, MTa_S2, etc... \n")
    pixel_spacing, tomo_path = fcm.determine_pixel_spacing("../tomogram.mrc")

    # Determine number of segments
    if not no_seg:
        particle_per_seg = int(input("Enter the minimum particle per segments (total = " + str(total_particle) + "):\n"))
        nb_of_segment = math.floor(total_particle / particle_per_seg)
        print("Generating {} segments of at least {} particles.\n".format(nb_of_segment, particle_per_seg))
        cpm.create_segments(nb_of_segment, base_name_file)

    # Checking for existing prm file
    print("Checking for {}.prm...\n".format(base_name_file))
    prm_path = "./" + base_name_file + ".prm"  # It is also possible to have all prm loading with *.prm
    ref_lines = fcm.open_file(prm_path)

    if ref_lines is None:
        print("{} could not be found, loading default prm...\n".format(prm_path))
        ref_lines = dft.BASE_PRM
        lines_to_change = generate_main_mt_prm(ref_lines, base_name_file, number_core, total_particle, pixel_spacing,
                                               tomo_path)
        new_prm = modifier_prm(ref_lines, lines_to_change)
        fcm.write_file(prm_path, new_prm)
    else:
        print("Previous prm file found. Using {}.prm...\n".format(base_name_file))
    ref_lines = fcm.open_file(prm_path)  # Now that a prm file exist we can load it

    # Preparing mainMT thread if necessary
    stop = False
    if not seg_only:
        try:
            _ = glob.glob("{base}_AvgVol_*.mrc".format(base=base_name_file))[-1]
            remake = input("A MT average already exist for the full length, do you want to remake one (with existing "
                           "prm) ? y/n\n")
            if remake == 'n' or remake == "no":
                stop = True
        except IndexError:
            print("No full MT average found, generating one...\n")
        if not stop:
            cpm.lancer_parser(base_name_file)
            proc = threading.Thread(target=cpm.lancer_process_chunk_fullmt,
                                    args=(base_name_file, number_core, start_wd, stop_threads, lock))
            all_procs.append(proc)

    # Preparing segment threads if authorized
    if not no_seg:

        # First create all prm files then start the averaging
        motiv_path = os.path.relpath(glob.glob(os.getcwd() + "/segment1/*RefP*.csv")[0])
        number_of_particle = fcm.get_number_of_particle(motiv_path)
        nbr_search = len(ref_lines[fcm.search_string_in_file(ref_lines, "dPhi = ")].split(","))
        volume_sz = round_to_even(64 * 8.0 / pixel_spacing)
        for i in range(1, nb_of_segment + 1):
            lines_to_change = generate_segments_prm(ref_lines, base_name_file, i, number_core, number_of_particle,
                                                    nbr_search, tomo_path, volume_sz, pixel_spacing)
            new_file = modifier_prm(ref_lines, lines_to_change)
            base_name_with_segment = base_name_file + '_S' + str(i)
            new_file_path = "./segment{number}/{filename}.prm".format(number=i, filename=base_name_with_segment)
            fcm.write_file(new_file_path, new_file)

        # Averaging
        for i in range(1, nb_of_segment + 1):
            base_name_with_segment = base_name_file + '_S' + str(i)
            working_dir = os.path.join(start_wd, "segment{}".format(i))
            cpm.lancer_parser_segment(base_name_with_segment, working_dir)
            # ProcessChunk will not start until parser has finished
            proc = threading.Thread(target=cpm.lancer_process_chunk_segment,
                                    args=(base_name_file, i, number_core, working_dir, stop_threads, lock))
            all_procs.insert(0, proc)

    # Starting all threads
    for proc in all_procs:
        proc.start()

    # Wait for all process to end before ending program
    try:

        # Wait for all threads to finish
        print("There is " + str(threading.active_count() - 1) +
              " parallel threads running for PEET. You can kill them using CTRL + C if they reached at least iteration "
              "3. Otherwise do it manually in by killing processchunks processes.")
        for proc in all_procs:
            proc.join()
    except KeyboardInterrupt:

        # Handle Ctrl+C during the execution of threads
        print("Ctrl+C received. Stopping all processes after they updated at least a chunk. \n\n\n\n\n")
        stop_threads.set()
        try:
            for proc in all_procs:
                proc.join()
            print("All threads are closed")
        finally:
            exit(1)

    print("\nAll segments have been generated\nCleanup is starting...")
    # Cleaning up files
    if not no_cleanup:

        # If whole MT was generated then do it
        if not seg_only and not stop:
            print("Cleaning main folder")
            fcm.cleanup(start_wd, base_name_file)

        # If segments were generated then do it for the segments too
        if not no_seg:
            for i in range(1, nb_of_segment + 1):
                base_name_with_segment = base_name_file + '_S' + str(i)
                wd = os.path.join(start_wd, "segment{}".format(i))
                print("Cleaning {} for segment {}".format(wd, i))
                fcm.cleanup(wd, base_name_with_segment)
    os.chdir(start_wd)
    show_surface = str(input("Would you like to see all iso-surfaces ? y/n\n"))
    if show_surface == "y" or show_surface == "yes":
        if not seg_only:
            avg_path = glob.glob("{base}_AvgVol_*.mrc".format(base=base_name_file))[-1]
            open_average(avg_path)
            time.sleep(1)
        if not no_seg:
            for i in range(1, nb_of_segment + 1):
                avg_path = glob.glob("./segment{num}/{name}_S{num}_AvgVol_*.mrc".format(num=i, name=base_name_file))[0]
                open_average(avg_path)
                time.sleep(1)
        print("All isosurfaces have been opened\n")
        exit(0)
