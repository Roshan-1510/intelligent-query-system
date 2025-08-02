import os
import shutil

# List of unnecessary folders
folders_to_remove = [
    "__pycache__",
    ".idea",
    "venv",
    "sandbox",
    "dev"
]

# List of unnecessary files
files_to_remove = [
    "file_tree.txt",
]

for folder in folders_to_remove:
    if os.path.isdir(folder):
        shutil.rmtree(folder)
        print(f"Removed folder: {folder}")

for file in files_to_remove:
    if os.path.isfile(file):
        os.remove(file)
        print(f"Removed file: {file}")
