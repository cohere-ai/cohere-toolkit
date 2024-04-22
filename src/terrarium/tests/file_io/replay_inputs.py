import os

directory = os.path.expanduser("~")

# Get a list of all files in the directory
files = os.listdir(directory)

# Print the list of files
for file in files:
    print(file)
    with open(file, mode="rb") as f, open(
        file.replace("_input", "_output"), mode="wb"
    ) as f2:
        f2.write(f.read())
