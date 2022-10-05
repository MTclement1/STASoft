# This is a sample Python script.
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import app
from optparse import OptionParser

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parser = OptionParser()
    parser.set_defaults(number_core=12)
    parser.add_option("-c", "--core", dest="number_core", type="int", help="input number of true core on your "
                                                                           "machine, default is 12", metavar="INT")
    (options, args) = parser.parse_args()
    app.run(options.number_core)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
