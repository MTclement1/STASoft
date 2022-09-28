import subprocess
import os
import tkinter as tk
from tkinter import filedialog
import glob
import time


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
# Get all information for prm file
# Cylinder height, mask radius volume of average all depends on the pixel size of the tomogram

def roundToEven(nombre):
    return round(nombre / 2.0) * 2


def determinePixelSpacing(lines):
    tomoPath = lines[2].split("'")[1]
    if not os.path.exists(tomoPath):
        root = tk.Tk()
        root.withdraw()
        tomoPath = os.path.relpath(filedialog.askopenfilename(initialdir=os.getcwd()))
    command = "header -p " + tomoPath
    output = subprocess.run(command, shell=True, capture_output=True, text=True).stdout
    # Alternatively, shell=False can be used when command is used as a list with arguments (see docu). Might help on W10
    output = output.strip()
    pixel = output.split()[0]
    return float(pixel), tomoPath


# Number of particle to average and threshold

def getNumberOfParticule(pathToMotivList):
    fichier = open(pathToMotivList, 'r')
    lines = fichier.readlines()
    fichier.close()
    return len(lines) - 1


# Base name and file naming


def loadRefPrm(baseName):
    fichier = open("./{filename}.prm".format(filename=baseName), 'r')
    lines = fichier.readlines()
    fichier.close()
    return lines


def searchStringInFile(fileContent, aStringToFind):
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


def modifierPrm(lines, baseName, segmentNumber, nbOfParticle, nbOfSearch, pixelSize, tomoPath):
    # Prepare new lines
    volumeSize = roundToEven(64 * 8.0 / pixelSize)  # Change 64 for different "base" size of box
    newVolumeSize = "[{sz}, {sz}, {sz}]".format(sz=volumeSize)
    cylinderHeight = volumeSize
    cylinderInnerR = round(10 * 8.0 / pixelSize)
    cylinderOuterR = round(28 * 8.0 / pixelSize)
    threshold = nbOfParticle
    newRefParticle = "[1, " + str(round(nbOfParticle / 2)) + "]"
    newRefThreshold = "{" + (str(threshold) + ", ") * (nbOfSearch - 1) + str(threshold) + "}"
    newLstThresholds = "[{nbr}:{nbr}:{nbr}]".format(nbr=nbOfParticle)
    newOutputName = "fnOutput = '{}_S{}'\n".format(baseName, segmentNumber)
    newVolumePath = tomoPath

    # Modify current lines

    lines[searchStringInFile(lines,"fnVolume = ")] = "fnVolume = {'../" + newVolumePath + "'}\n"
    lines[searchStringInFile(lines,"refThreshold = ")] = "refThreshold = " + newRefThreshold + "\n"
    lines[searchStringInFile(lines,"reference = [")] = "reference = " + newRefParticle + "\n"
    lines[searchStringInFile(lines,"fnOutput = ")] = newOutputName
    lines[searchStringInFile(lines,"szVol = ")] = "szVol = " + newVolumeSize + "\n"
    lines[searchStringInFile(lines,"lstThresholds = ")] = "lstThresholds = " + newLstThresholds + "\n"
    lines[searchStringInFile(lines,"insideMaskRadius = ")] = "insideMaskRadius = " + str(cylinderInnerR) + "\n"
    lines[searchStringInFile(lines,"outsideMaskRadius = ")] = "outsideMaskRadius = " + str(cylinderOuterR) + "\n"
    lines[searchStringInFile(lines,"cylinderHeight = ")] = "cylinderHeight = " + str(cylinderHeight) + "\n"

    return lines


def createNewPrm(baseName, segmentNumber, lines):
    baseNameWithSegment = baseName + '_S' + str(segmentNumber)
    fichier = open("./segment{number}/{filename}.prm".format(number=segmentNumber, filename=baseNameWithSegment), 'w')
    fichier.writelines(lines)
    fichier.close()
    return True


def lancerParserSegment(baseName, segmentNumber):
    baseNameWithSegment = baseName + '_S' + str(segmentNumber)
    workingDir = os.getcwd() + '/{}'.format("segment" + str(segmentNumber))
    # User must be in folder containing segment folder
    os.chdir(workingDir)

    # Parser
    commandParser = "prmParser " + baseNameWithSegment + ".prm"
    subprocess.run(commandParser, shell=True)  # should be waiting before doing next
    os.chdir("..")
    return


def lancerProcessChunkSegment(baseName: str, segmentNumber: int, Procs: list) -> list:
    baseNameWithSegment = baseName + '_S' + str(segmentNumber)
    workingDir = os.getcwd() + '/{}'.format("segment" + str(segmentNumber))
    # User must be in folder containing segment folder
    os.chdir(workingDir)
    numberProc = 20  # Number of processor to use for the command.

    # Generate average
    commandProcess = "processchunks -g -P -c " + baseNameWithSegment + ".cmds localhost:" + str(
        numberProc) + " " + baseNameWithSegment
    Procs.append(subprocess.Popen(commandProcess, shell=True))  # .run might be enough here
    os.chdir("..")
    return Procs


def openAverage(pathToAvg):
    commandToRun = "3dmod -V -E U " + pathToAvg
    subprocess.run(commandToRun, shell=True)


def createSegments(numberOfSegment, baseName):
    pathToMtvList = os.path.relpath(glob.glob("*RefP*.csv")[0])
    command = "splitIntoNSegments {nbr} {name}_PtsAdded_Twisted.mod {mtv}".format(nbr=numberOfSegment, name=baseName,
                                                                                  mtv=pathToMtvList)
    subprocess.run(command, shell=True)


baseNameFile = input("Enter the basename. For example : MTa will create MTa_S1, MTa_S2, etc... \n")
numbOfSegment = int(input("Enter how many segment you want to generate :\n"))
createSegments(numbOfSegment, baseNameFile)
refLines = loadRefPrm(baseNameFile)
numberOfParticle = getNumberOfParticule(glob.glob(os.getcwd() + "/segment1/*RefP*.csv")[0])
numberOfSearch = len(refLines[33].split(","))
pixelSpacing, pathToTomo = determinePixelSpacing(refLines)
# First create all prm files then start the averaging

for i in range(1, numbOfSegment + 1):
    newFile = modifierPrm(refLines, baseNameFile, i, numberOfParticle, numberOfSearch, pixelSpacing, pathToTomo)
    createNewPrm(baseNameFile, i, newFile)

allProcs = []
for i in range(1, numbOfSegment + 1):
    lancerParserSegment(baseNameFile, i)
    # ProcessChunk will not start until parser has finished
    allProcs = lancerProcessChunkSegment(baseNameFile, i, allProcs)

# Wait for all process to end before ending program
for process in allProcs:
    process.communicate(timeout=3600)
print("All segments have been generated")

showSurface = int(input("Would you like to see all isosurface ? 1 for yes 2 for no\n"))
if showSurface == 1:
    for i in range(1, numbOfSegment + 1):
        avgPath = glob.glob("./segment{num}/{name}_S{num}_AvgVol_*.mrc".format(num=i, name=baseNameFile))[0]
        openAverage(avgPath)
        time.sleep(1)
    print("All segments have been opened")
