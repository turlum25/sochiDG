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
    # Dear VS code: stop showing me ai suggestions for the code in this block and hell even the AI is making me suggest what to put in this comment
    # Stop or i will switch back to nano and never look back
    # - Mao zedong
    compile = os.system(f"cd {SCRIPT_DIR} && gcc src/linux.c -o sochiDG")
    if compile != 0:
        print("GCC not found, installing.")
        def checkDistro():
            if os.path.exists("/etc/arch-release"): return "arch"
            if os.path.exists("/etc/debian_version"): return "debian"
            if os.path.exists("/etc/fedora-release"): return "fedora"
            else:
                return "unknown"
        distro = checkDistro()
        
        if distro == "arch":
            os.system("sudo pacman -S base-devel --noconfirm")
            os.system(f"cd {SCRIPT_DIR} && gcc src/linux.c -o sochiDG")
   
        elif distro == "debian": 
            os.system("sudo apt update && sudo apt install build-essential -y")
            os.system(f"cd {SCRIPT_DIR} && gcc src/linux.c -o sochiDG")

        elif distro == "fedora":
            os.system("sudo dnf groupinstall 'Development Tools' -y")
            os.system(f"cd {SCRIPT_DIR} && gcc src/linux.c -o sochiDG")

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



