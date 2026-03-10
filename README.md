# sochiDG

sochiDG is a Python and C based iPhone 5S (Global) downgrader. However, this will only support iOS 7.1.2.

# Compatibility

macOS 10.13+ in Intel is supported, and I will add Linux and ARM64 Mac support later on. The Python-based sochiDG clients can run in both Python 3.9 and 3.14, but I have not tested other versions.

# Compiling source code and running (does not apply with releases)
Since some do not fit into the maximum GitHub file requirement:
* Place these files in the ramdisk folder:
* Download ramdisk.im4p from [here.](https://www.mediafire.com/file/aya3nbyzqp7xrm3/ramdisk.im4p/file#)
* Download ramdisk.dmg from [here.](https://www.mediafire.com/file/i3cvx8mz7ehtlqk/ramdisk.dmg/file)
* Place this file in the 7.1.2 folder
* Download ios7.tar from [here.](https://www.mediafire.com/file/i3cvx8mz7ehtlqk/ramdisk.dmg/file)
For the C binary, please run compiler.py by running the command "python3 compiler.py"

# How to run and execute (and downgrade)
* Step 1: CD into the downgrade by typing in "cd sochiDG" or "cd 5s_downgrade"
* Step 2: Run this command: "python3 main.py" or just "./sochiDG -d". However, you need to install the necessary tools put in the tools folder as this tool is in very rough condition.
* Step 3: Downgrade
* Step 4: Boot (./sochiDG -b)
* Step 5: Profit

# Activating iPhone after downgrade

After booting into the setup screen, do the following:
* Select your country
* When in WiFi connection screen, click "Connect to iTunes" until the recovery mode logo appears (while not in recovery mode).
* Go to Finder/iTunes and let it activate the iPhone
* Profit

# Pretty necessary stuff

* The full downgrade folder will be around 2 GB after extraction as automating the downloads in the script might cause faliure in the process.
* Since this downgrade tool is unstable and buggy, I would reccomend other developers to enhance my code. I also do not mind at all, if anyone puts my downgrade logic and code into their program.
