# This is a sample Python script.
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import app
from optparse import OptionParser

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parser = OptionParser()
    parser.set_defaults(number_core=8)
    parser.set_defaults(seg_only=False)
    parser.add_option("-c", "--core", dest="number_core", type="int", help="input number of true core on your "
                                                                           "machine, default is 8", metavar="INT")
    parser.add_option("-s", "--segments", action="store_true", dest="seg_only", help="Assume that the whole MT STA is "
                                                                                     "already generated and only "
                                                                                     "generate segments")
    parser.add_option("-w", "--whole", action="store_true", dest="no_seg", help=" Only generate the whole MT")
    (options, args) = parser.parse_args()
    app.run(options.number_core, options.seg_only, options.no_seg)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
