import glob
import os
import subprocess
import backend.file_content_module as fcm


def create_segments(numberOfSegment, baseName):
    """ Use the splitIntoNSegments function of imod to create folder ready of subtomogram averaging
    :param numberOfSegment: int
    :param baseName: string
    """
    path_to_mtv_list = os.path.relpath(glob.glob("*RefP*.csv")[0])

    command = "splitIntoNSegments {nbr} {name}_PtsAdded_Twisted.mod {mtv}".format(nbr=numberOfSegment, name=baseName,
                                                                                  mtv=path_to_mtv_list)
    result = subprocess.run(command.split(" "), stdout=subprocess.PIPE, text=True)
    fcm.log_file_append(result)


def lancer_parser_segment(base_name_with_segment, segment_number):
    """ Parse the prm using prmParser from imod to prepare com files for chunk processing
    :param base_name_with_segment: string
    :param segment_number: int
    :return: always True
    """
    working_dir = os.getcwd() + '/{}'.format("segment" + str(segment_number))
    # User must be in folder containing segment folder
    os.chdir(working_dir)

    # Parser
    command_parser = "prmParser " + base_name_with_segment + ".prm"
    result = subprocess.run(command_parser.split(" "), stdout=subprocess.PIPE,
                            text=True)  # should be waiting before doing next (independant of shell = True)
    fcm.log_file_append(result)
    os.chdir("..")
    return True


def lancer_parser(base_name):
    """ Parse the prm using prmParser from imod to prepare com files for chunk processing
    :param base_name: string
    :return: always True
    """
    # Parser
    command_parser = "prmParser " + base_name + ".prm"
    result = subprocess.run(command_parser.split(" "), stdout=subprocess.PIPE, text=True)
    # should be waiting before doing next (independant of shell = True)
    fcm.log_file_append(result)
    return True


def lancer_process_chunk_fullmt(base_name: str, number_core):
    """ Use the processchunks functions from imod to process chunks using com files generated by prm parser
    :param number_core: int
    :param base_name: str
    :return: a pointer to a stream
    """
    # Generate average
    command_process = "processchunks -n 0 -g -P " + "localhost:" + str(
        number_core) + " " + base_name
    proc = subprocess.Popen(command_process.split(" "), preexec_fn=os.setpgrp,
                            stdout=subprocess.PIPE)  # popen necessary for parallel processing

    return proc


def lancer_process_chunk_segment(base_name: str, segment_number: int, number_core):
    """ Use the processchunks functions from imod to process chunks using com files generated by prm parser
    :param number_core: int
    :param base_name: str
    :param segment_number: int
    :return: a pointer to a stream
    """
    base_name_with_segment = base_name + '_S' + str(segment_number)
    working_dir = os.getcwd() + '/{}'.format("segment" + str(segment_number))
    # User must be in folder containing segment folder
    os.chdir(working_dir)  # Number of processor to use for the command.
    command_process = "processchunks -n 0 -g -P " + "localhost:" + str(
        number_core) + " " + base_name_with_segment
    # Generate average
    proc = subprocess.Popen(command_process.split(" "), preexec_fn=os.setpgrp,
                            stdout=subprocess.PIPE)  # popen necessary for parallel processing
    os.chdir("..")
    return proc
