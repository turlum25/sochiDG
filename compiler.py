import os
from pathlib import Path
import time
import platform

SCRIPT_DIR = Path(__file__).resolve().parent
OS = platform.system()

checkOS = os.system("uname")
if OS == "Darwin":
    compile = os.system(f"cd {SCRIPT_DIR} && gcc src/mac.c -o sochiDG")
    if compile != 0:
        print("Xcode Command Line Tools not found, installing...")
        os.system("xcode-select --install")
        exit(0)

    elif compile == 0:
        print("Successfully compiled sochiDG")
        time.sleep(1)
        os.system("clear")
        exit(0)

elif OS == "Linux":
    compile = os.system(f"cd {SCRIPT_DIR} && gcc src/linux.c -o sochiDG")
    if compile != 0:
        print("GCC not found, installing.")
        os.system("sudo apt update && sudo apt install build-essential -y")
        os.system("clear")
        exit(0)

    elif compile == 0:
        print("Successfully compiled sochiDG")
        time.sleep(1)
        os.system("clear")
        exit(0)

elif OS == "Windows":
    print("[!] Unsupported OS detected: Windows")
    print("This OS is not supported for sochiDG, please use Linux or macOS.")
    exit(1)
    # i hate windows fuck you 



