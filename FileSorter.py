import os
import shutil

def sort_files_by_extension(folder, name_map=None):
    """
    Move files in `folder` into subfolders according to extension.
    `name_map` optional dict maps extension keys to folder names:
      key is extension in lower form with leading dot, e.g. ".txt"
      or the special key "(noext)" for files without extension.
    If mapping for an extension is missing or empty, fallback is:
      ext -> ext[1:].lower() (e.g. ".TXT" -> "txt")
      no extension -> "others"
    """
    if name_map is None:
        name_map = {}

    for filename in os.listdir(folder):
        full_path = os.path.join(folder, filename)
        if not os.path.isfile(full_path):
            continue

        _, ext = os.path.splitext(filename)
        ext = ext.lower()
        key = ext if ext else "(noext)"

        # determine target folder name
        target_name = name_map.get(key)
        if not target_name:
            target_name = ext[1:].lower() if ext else "others"

        ext_folder = os.path.join(folder, target_name)
        os.makedirs(ext_folder, exist_ok=True)
        shutil.move(full_path, os.path.join(ext_folder, filename))

if __name__ == "__main__":
    folder_path = os.path.dirname(os.path.abspath(__file__))
    print(f"Target folder:{folder_path}")
    sort_files_by_extension(folder_path)
    input("Sorting complete! Press Enter to exit.")