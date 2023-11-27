# This is a sample Python script.
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import app
import argparse

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="STAsoft is a software that automate microtubule segmented "
                                                 "sub-tomogram averaging using imod PEET")
    parser.add_argument("-c", "--core", type=int, default=4,
                        help="Input number of true core on your machine, default is 4")
    parser.add_argument("-s", "--segments", action="store_true", default=False,
                        help="Assume that the whole MT STA is already generated and only generate segments")
    parser.add_argument("-w", "--whole", action="store_true", default=False, help="Only generate the whole MT")
    parser.add_argument("-v", "--version", action="version", version='%(prog)s 2.9.1', help="Display version")

    args = parser.parse_args()
    app.run(args.core, args.segments, args.whole)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
