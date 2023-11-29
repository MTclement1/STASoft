import os

# This variable should be initialized only the first time is it called.
current_wd = None
current_wd = current_wd if current_wd is not None else os.getcwd()
