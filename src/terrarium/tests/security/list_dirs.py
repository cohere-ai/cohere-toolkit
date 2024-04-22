#
# expected output in terrarium: listing the guest root & files only, not of the root system!!
#
import os
from os.path import expanduser

home = expanduser("~")
print(home)
print(home, " files", os.listdir(home + "/"))
print("root:", os.listdir("/"))
