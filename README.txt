------------------
---INSTALLATION---
------------------
Requirements:
    - Python3
    - Imod PEET installed and on path. version > 4.12.56
    - Multiprocessing setup on IMOD, or use -c 1
    - psutil and tqdm python packages (see requirements.txt)

Download the full folder from GitHub (https://github.com/MTclement1/STASoft) and save it anywhere you want.
You can make an alias such as "alias STAsoft='python3 /home/STASoft'".
------------------
------USAGE-------
------------------
Follow the same procedure as presented in DOI: 10.21769/BioProtoc.4723 until part D included.
In the folder where the model is saved call the software with STAsoft then
    1. Enter the base name of the model. i.e. in MTa_PtsAddedTwisted.mod then enter MTa
    2. Enter the minimum amount of particle for each segment.
    3. For the angle step, theta is in plane rotation while psi is out of plane rotation, considering the horizontal
    plane cutting the microtubule in half along its length.
    4. A file explorer window opens, please select the same tomogram that was used for microtubule modelisation.

From now on it is not possible to cancel the process through the console. See STAsoft -h for help on options.
