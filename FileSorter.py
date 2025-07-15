import os
import shutil

def sort_files_by_extension(folder):
    for filename in os.listdir(folder):
        full_path = os.path.join(folder, filename)
        if os.path.isfile(full_path):
            name, ext = os.path.splitext(filename)
            if ext:
                ext_folder = os.path.join(folder, ext[1:].lower())
            else:
                ext_folder = os.path.join(folder, "others")
            os.makedirs(ext_folder, exist_ok=True)
            shutil.move(full_path, os.path.join(ext_folder, filename))

folder_path = os.path.dirname(os.path.abspath(__file__))

print(f"Target folder:{folder_path}")
sort_files_by_extension(folder_path)
input("Sorting complete! Press Enter to exit.")