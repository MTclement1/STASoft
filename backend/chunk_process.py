import glob
import os
import subprocess
import tqdm
import psutil
import backend.file_content_module as fcm
import signal
import re
from config import current_wd as start_wd


def kill_proc_tree(pid, sig=signal.SIGTERM, include_parent=True,
                   timeout=None, on_terminate=None):
    """Kill a process tree (including grandchildren) with signal
    "sig" and return a (gone, still_alive) tuple.
    "on_terminate", if specified, is a callback function which is
    called as soon as a child terminates. It should not have to be called, but it's here in case.
    """
    assert pid != os.getpid(), "won't kill myself"
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    if include_parent:
        children.append(parent)
    for p in children:
        try:
            p.send_signal(sig)
        except psutil.NoSuchProcess:
            pass
    gone, alive = psutil.wait_procs(children, timeout=timeout,
                                    callback=on_terminate)
    return gone, alive


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


def lancer_parser_segment(base_name_with_segment, working_dir):
    """ Parse the prm using prmParser from imod to prepare com files for chunk processing
    :param working_dir: path to directory containing the parameter file for a segment
    :param base_name_with_segment: string
    :return: always True
    """
    # User must be in folder containing segment folder
    os.chdir(working_dir)

    # Parser
    command_parser = "prmParser " + base_name_with_segment + ".prm"
    subprocess.run(command_parser.split(" "), stdout=subprocess.PIPE, text=True)
    os.chdir(start_wd)
    return True


def lancer_parser(base_name):
    """ Parse the prm using prmParser from imod to prepare com files for chunk processing
    :param base_name: string
    :return: always True
    """
    # Parser
    command_parser = "prmParser " + base_name + ".prm"
    subprocess.run(command_parser.split(" "), stdout=subprocess.PIPE, text=True)
    return True


def lancer_process_chunk_fullmt(base_name: str, number_core, wd, stop, lock):
    """ Use the processchunks functions from imod to process chunks using com files generated by prm parser
    :param lock: a lock from threading
    :param wd: working directory as a string
    :param stop: threading event
    :param number_core: int
    :param base_name: str
    :return: a pointer to a stream
    """
    # Generate average
    command_process = "processchunks -n 18 -g -P -c " + base_name + ".cmds localhost:" + str(
        number_core) + " " + base_name
    command = command_process.split(" ")
    lock.acquire()
    os.chdir(wd)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
                            universal_newlines=True, start_new_session=True)  # popen necessary for parallel processing
    lock.release()
    log = open("TotalLog_MainMT.txt", 'a')
    print("Main MT PID is " + str(proc.pid))
    # Setting the progress bar
    total_pattern = re.compile(r'\d+ of (\d+) done so far', re.IGNORECASE)
    segment_bar = tqdm.tqdm(desc=f"Main MT Progress", position=0,
                            leave=False)
    try:
        for line in proc.stdout:
            match = total_pattern.search(line)
            done = False
            if match and not done:  # When total chunk in known, total is adapted once
                total = int(match.group(1))
                segment_bar.total = total
                segment_bar.refresh()
                done = True
            if 'DONE SO FAR' in line:
                segment_bar.update(1)
            else:
                log.write(line)
            if stop.is_set():
                log.close()
                segment_bar.close()
                return

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully using kill_proc_tree function
        print("Ctrl+C received. Terminating process for main MT.")
        log.close()
        print("Proc PID is :" + str(proc.pid))
        gone, alive = kill_proc_tree(proc.pid, signal.SIGKILL)
        for p in alive:
            p.kill()
    finally:
        log.close()
        segment_bar.close()
        return


def lancer_process_chunk_segment(base_name: str, segment_number: int, number_core, wd: str, stop, lock):
    """ Use the processchunks functions from imod to process chunks using com files generated by prm parser
    :param lock: a threading lock
    :param stop: a threading event
    :param wd: a string for working directory
    :param number_core: number of core to use
    :param base_name: str
    :param segment_number: which segment number is it
    """
    base_name_with_segment = base_name + '_S' + str(segment_number)

    command_process = "processchunks -n 18 -g -P -c " + base_name_with_segment + ".cmds localhost:" + str(
        number_core) + " " + base_name_with_segment  # Number of processor to use for the command.
    command = command_process.split(" ")

    # Generate average
    # User must be in folder containing segment folder. Using a lock to prevent shenanigans when multiple threadings
    lock.acquire()
    os.chdir(wd)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
                            universal_newlines=True, start_new_session=True)  # popen necessary for parallel processing

    lock.release()
    log = open("TotalLog_Segment" + str(segment_number) + ".txt", 'a')

    # Setting the progress bar
    total_pattern = re.compile(r'\d+ of (\d+) done so far', re.IGNORECASE)
    segment_bar = tqdm.tqdm(desc=f"Segment {segment_number} Progress", position=segment_number,
                            leave=False)
    try:
        for line in proc.stdout:
            match = total_pattern.search(line)
            done = False
            if match and not done:  # When total chunk in known, total is adapted once
                total = int(match.group(1))
                segment_bar.total = total
                segment_bar.refresh()
                done = True
            if 'DONE SO FAR' in line:
                segment_bar.update(1)
            else:
                log.write(line)
            if stop.is_set():
                segment_bar.close()
                log.close()
                return
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully using kill_proc_tree function
        segment_bar.close()
        print("Ctrl+C received. Terminating process for segment number " + str(segment_number) + ".")
        log.close()
        print("Proc PID is :" + str(proc.pid))
        gone, alive = kill_proc_tree(proc.pid, signal.SIGKILL)
        for p in alive:
            p.kill()
    finally:
        log.close()
        return
