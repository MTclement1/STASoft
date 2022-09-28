import subprocess
import os

#toDO
#automatic choice of particle per CPU
#Graphical interface
#Failsafe when file are not found
#Better PRM modification
def loadRefPrm(baseName):
    segmentNumber = 1
    baseNameWithSegment = baseName + '_S' + str(segmentNumber)
    fichier = open("./segment{number}/{filename}.prm".format(number=segmentNumber, filename=baseNameWithSegment), 'r')
    lines = fichier.readlines()
    fichier.close()
    return lines


def modifierPrm(lines, baseName, segmentNumber):
    # Prepare new lines
    newOutputName = "fnOutput = '{}_S{}'\n".format(baseName, segmentNumber)
    # Modify current lines
    lines[81] = newOutputName
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
    print(commandParser)
    subprocess.run(commandParser, shell=True)  # should be waiting before doing next
    os.chdir("..")
    return


def lancerProcessChunkSegment(baseName, segmentNumber, Procs):
    baseNameWithSegment = baseName + '_S' + str(segmentNumber)
    workingDir = os.getcwd() + '/{}'.format("segment" + str(segmentNumber))
    # User must be in folder containing segment folder
    os.chdir(workingDir)
    numberProc = 20  # Number of processor to use for the command.

    # Generate average
    commandProcess = "processchunks -g -P -c " + baseNameWithSegment + ".cmds localhost:" + str(
        numberProc) + " " + baseNameWithSegment
    Procs.append(subprocess.Popen(commandProcess, shell=True))
    os.chdir("..")
    return Procs


baseName = input("Enter the basename. For example : CG1_2_1_MTa \n")
numberOfSegment = int(
    input("Enter how many segment you want to generate (not counting the first one that should be done "
          "already):\n"))

refLines = loadRefPrm(baseName)
# First create all prm files then start the averaging
for i in range(2, numberOfSegment + 2):
    lines = modifierPrm(refLines, baseName, i)
    success = createNewPrm(baseName, i, lines)

Procs = []
for i in range(2, numberOfSegment + 2):
    lancerParserSegment(baseName, i)
    # ProcessChunk will not start until parser has finished
    Procs = lancerProcessChunkSegment(baseName, i, Procs)

# Wait for all process to end before ending program
for process in Procs:
    process.communicate(timeout=600)  # If a process is stuck for more than 10min kill it.

print("All segments have been generated")
