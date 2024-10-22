import os
import pathlib
import platform

def get_download_folder():
    home = str(pathlib.Path.home())

    if platform.system() == "Windows":
        return os.path.join(home, "Downloads")
    elif platform.system() == "Darwin":
        return os.path.join(home, "Downloads")
    elif platform.system() == "Linux":
        return os.path.join(home, "Downloads")
    else:
        raise Exception("Unsupported operating system")

