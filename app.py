import backend.file_content_module as fcm
import backend.chunk_process as cpm
import backend.default_param as dft
import os
import subprocess
import glob
import time
import math


# TODO
# It is possible to have all prm loading with *.prm to remove any trouble with different base
# name but it might not be the best
# Graphical interface
# fix when file are not found (for example in splitIntoseg with the model pts added)
# Possibly using shutil.which and replace all command with their direct path
# Allow for optional arguments as a way to modify the file
# Prepare unit testing file https://pymbook.readthedocs.io/en/latest/testing.html
# Alternatively, shell=False can be used when command is used as a list with arguments (see docu). Might help on W10
# Use subprocess.call in lancer prm parser and chunk to prevent starting chunk before parser has finished.
# popen.wait maybe can be useful too. exit_codes = [p.wait() for p in p1, p2] for multiple processes. Note that
# according to the python documentation subprocess.run waits for the process to end


def round_to_even(nombre):
    return round(nombre / 2.0) * 2


def modifier_prm(lines, lines_to_change):
    modified_prm = lines
    for (param, index) in lines_to_change:
        modified_prm = fcm.change_line(modified_prm, index, param)
    return modified_prm


def open_average(path_to_avg):
    commandToRun = "3dmod -V -E U " + path_to_avg
    subprocess.run(commandToRun, shell=True)


def generate_main_mt_prm(ref_lines, base_name, number_cpu):
    number_of_particle = fcm.get_number_of_particle(glob.glob(os.getcwd() + "/*RefP*.csv")[0])
    choice = int(input("Do you want to add another search ? 0 for no, 1 for theta only, 2 for psi only, 3 for both\n"))
    lines_to_change = []
    phi = ""
    sradius = 'searchRadius = {[5], [4], [2], [1]}\n'
    if choice == 0:
        phi = 'dPhi = {-9:6:9, -4.5:3:4.5, -2.3:1.5:2.3, -1:1:1}\n'
        sradius = 'searchRadius = {[5], [4], [2], [1]}\n'
    elif choice == 1:
        phi = 'dPhi = {0:1:0, -9:6:9, -4.5:3:4.5, -2.3:1.5:2.3, -1:1:1}\n'
        psi = 'dPsi = {0:1:0, -9:6:9, -4.5:3:4.5, -2.3:1.5:2.3, -1:1:1}\n'
        theta = 'dTheta = {-15:5:15, -9:6:9, -4.5:3:4.5, -2.3:1.5:2.3, -1:1:1}\n'
        sradius = 'searchRadius = {[6], [5], [4], [2], [1]}\n'
        lines_to_change.append((psi, fcm.search_string_in_file(ref_lines, "dPsi = ")))
        lines_to_change.append((theta, fcm.search_string_in_file(ref_lines, "dTheta = ")))
    elif choice == 2:
        phi = 'dPhi = {0:1:0, -9:6:9, -4.5:3:4.5, -2.3:1.5:2.3, -1:1:1}\n'
        theta = 'dTheta = {0:1:0, -9:6:9, -4.5:3:4.5, -2.3:1.5:2.3, -1:1:1}\n'
        psi = 'dPsi = {-15:5:15, -9:6:9, -4.5:3:4.5, -2.3:1.5:2.3, -1:1:1}\n'
        sradius = 'searchRadius = {[6], [5], [4], [2], [1]}\n'
        lines_to_change.append((psi, fcm.search_string_in_file(ref_lines, "dPsi = ")))
        lines_to_change.append((theta, fcm.search_string_in_file(ref_lines, "dTheta = ")))
    elif choice == 3:
        phi = 'dPhi = {0:1:0, -9:6:9, -4.5:3:4.5, -2.3:1.5:2.3, -1:1:1}\n'
        theta = 'dTheta = {-15:5:15, -9:6:9, -4.5:3:4.5, -2.3:1.5:2.3, -1:1:1}\n'
        psi = 'dPsi = {-15:5:15, -9:6:9, -4.5:3:4.5, -2.3:1.5:2.3, -1:1:1}\n'
        sradius = 'searchRadius = {[6], [5], [4], [2], [1]}\n'
        lines_to_change.append((psi, fcm.search_string_in_file(ref_lines, "dPsi = ")))
        lines_to_change.append((theta, fcm.search_string_in_file(ref_lines, "dTheta = ")))
    else:
        print("This is not a possible answer to the question. Program will exit")
        exit(2)

    pixel_size, path_tomo = fcm.determine_pixel_spacing("../tomogram.mrc")
    volume_size = round_to_even(64 * 8.0 / pixel_size)
    number_of_search = len(phi.split(","))
    tilt_angles = fcm.get_tilt_range(glob.glob(os.path.dirname(path_tomo) + '/*.tlt')[0])

    lines_to_change.append(("fnVolume = {'" + path_tomo + "'}\n",
                            fcm.search_string_in_file(ref_lines, "fnVolume = ")))
    lines_to_change.append(("fnModParticle = {'" + glob.glob(os.getcwd() + "/*Twisted.mod")[0] + "'}\n",
                            fcm.search_string_in_file(ref_lines, "fnModParticle = ")))
    lines_to_change.append(("initMOTL = {'" + glob.glob(os.getcwd() + "/*initMOTL.csv")[0] + "'}\n",
                            fcm.search_string_in_file(ref_lines, "initMOTL = ")))
    lines_to_change.append(("tiltRange = {[" + tilt_angles[0] + ", " + tilt_angles[1] + "]}\n",
                            fcm.search_string_in_file(ref_lines, "tiltRange = {[")))
    lines_to_change.append((phi,
                            fcm.search_string_in_file(ref_lines, "dPhi = ")))
    lines_to_change.append((sradius,
                            fcm.search_string_in_file(ref_lines, "searchRadius = ")))
    lines_to_change.append(("lowCutoff = {" + "[0, 0.05], " * (number_of_search - 1) + "[0, 0.05]}\n",
                            fcm.search_string_in_file(ref_lines, "lowCutoff =")))
    lines_to_change.append(("hiCutoff = {" + "[0.1, 0.05], " * (number_of_search - 1) + "[0.1, 0.05]}\n",
                            fcm.search_string_in_file(ref_lines, "hiCutoff =")))
    lines_to_change.append(("refThreshold = {" + (str(number_of_particle) + ", ") * (number_of_search - 1) + str(
        number_of_particle) + "}\n",
                            fcm.search_string_in_file(ref_lines, "refThreshold = ")))
    lines_to_change.append(("duplicateShiftTolerance = " + "[NaN], " * (number_of_search - 1) + "[1]\n",
                            fcm.search_string_in_file(ref_lines, "duplicateShiftTolerance = ")))
    lines_to_change.append(("duplicateAngularTolerance = " + "[NaN], " * (number_of_search - 1) + "[1]\n",
                            fcm.search_string_in_file(ref_lines, "duplicateAngularTolerance = ")))
    lines_to_change.append(("reference = " + "[1, " + str(round(number_of_particle / 2)) + "]" + "\n",
                            fcm.search_string_in_file(ref_lines, "reference = [")))
    lines_to_change.append(("fnOutput = '{}'\n".format(base_name),
                            fcm.search_string_in_file(ref_lines, "fnOutput = ")))
    lines_to_change.append(("szVol = " + "[{sz}, {sz}, {sz}]".format(sz=volume_size) + "\n",
                            fcm.search_string_in_file(ref_lines, "szVol = ")))
    lines_to_change.append(("lstThresholds = " + "[{nbr}:{nbr}:{nbr}]".format(nbr=number_of_particle) + "\n",
                            fcm.search_string_in_file(ref_lines, "lstThresholds = ")))
    lines_to_change.append(("particlePerCPU = " + str(number_cpu) + "\n",
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
    motiv_path = glob.glob(os.getcwd() + "/segment{}/*RefP*.csv".format(segment_number))[0]
    mod_path = glob.glob(os.getcwd() + "/segment{}/*Twisted.mod".format(segment_number))[0]
    CPU = math.ceil(number_of_particle / number_cpu)
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
                       ("particlePerCPU = " + str(CPU) + "\n",
                        fcm.search_string_in_file(lines, "particlePerCPU = "))]
    return lines_to_change


def run(number_core, seg_only):
    #os.chdir("/Volumes/SSD_2To/TestSTASOft/MTa")
    base_name_file = input("Enter the basename. For example : MTa will create MTa_S1, MTa_S2, etc... \n")
    nb_of_segment = int(input("Enter how many segment you want to generate :\n"))
    prm_path = "./" + base_name_file + ".prm"
    ref_lines = fcm.open_file(prm_path)
    all_procs = []
    if ref_lines is None:
        print("{} could not be found, loading default prm...\n".format(prm_path))
        ref_lines = dft.BASE_PRM
        lines_to_change = generate_main_mt_prm(ref_lines, base_name_file, number_core)
        new_prm = modifier_prm(ref_lines, lines_to_change)
        fcm.write_file(prm_path, new_prm)
        if not seg_only:
            cpm.lancer_parser(base_name_file)
            #all_procs.append(cpm.lancer_process_chunk_fullmt(base_name_file, number_core))

        ref_lines = fcm.open_file(prm_path)  # Now that the new prm exist we can load it for segments
    else:
        print("Generating segments using {}.prm file...".format(base_name_file))

    # First create all prm files then start the averaging
    cpm.create_segments(nb_of_segment, base_name_file)
    motiv_path = glob.glob(os.getcwd() + "/segment1/*RefP*.csv")[0]
    number_of_particle = fcm.get_number_of_particle(motiv_path)
    nbr_search = len(ref_lines[fcm.search_string_in_file(ref_lines, "dPhi = ")].split(","))
    tomo_path = ref_lines[fcm.search_string_in_file(ref_lines, "fnVolume = ")].split("'")[1]
    pixel_spacing, tomo_path = fcm.determine_pixel_spacing(tomo_path)
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
        cpm.lancer_parser_segment(base_name_with_segment, i)
        # ProcessChunk will not start until parser has finished
        #all_procs.append(cpm.lancer_process_chunk_segment(base_name_file, i, number_core))

    # ait for all process to end before ending program

    for process in all_procs:
        process.communicate(timeout=3600)
    print("All segments have been generated")

    show_surface = int(input("Would you like to see all isosurface ? 1 for yes 2 for no\n"))
    if show_surface == 1:
        for i in range(1, nb_of_segment + 1):
            avg_path = glob.glob("./segment{num}/{name}_S{num}_AvgVol_*.mrc".format(num=i, name=base_name_file))[0]
            open_average(avg_path)
            time.sleep(1)
        print("All segments have been opened")
