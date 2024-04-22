#
# expected output in terrarium: allow to create dir in guest fs, but not show any other test dirs from previous runs (!)
#
import os
import time

os.makedirs("test_dir_" + str(time.time()))
print(os.listdir())
