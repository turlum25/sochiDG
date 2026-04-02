# sochiDG

sochiDG is a Shell and C based iPhone 5S (Global) downgrader. However, this will only support iOS 7.1.2.

# Why sochiDG is better

sochiDG is a very stable downgrader for the iPhone 5S Global. It can bring back the classic iOS 7.1.2 UI and speed to your iPhone 5S (again).

# What about Semaphorin?

Semaphorin is an older downgrader which is still very unstable and has stopped recieving updates since mid 2025. It also does not work properly at all, but this works in every macOS version from 10.13 High Sierra.

# Why not iOS 12.5.8 or 10.3.3? 

On the iPhone 5S, iOS 10.3.3 is not liked due to the removal of Slide To Unlock and other bugs. In iOS 9.x and under, it is much smoother and better unlike iOS 10 and 12, which makes the iPhone slower and shortens battery life. 
However, in iOS 7.1.2, applications open in seconds, the animations are very smooth and fast and the battery lasts around 10 hours (or so.)

# Current issues

In iOS 7.1.2, you will not be able to use Touch ID and you will lose access to passwords, including password-protected WiFi. If you try to set a password onto your phone, it will panic once you lock the screen and go back into recovery mode.
The iPhone may also go into recovery mode as well if you leave it unplugged and in sleep for around 30 seconds to 5 minutes. This is called the deep-sleep bug and this is very common in downgrades lacking a functional Secure Enclave Processor (a.k.a SEP).

# What is SEP? 

The SEP (Secure Enclave Processor) is a physical chip in the iPhone/iPad/iPod touch which has the responsibility of controlling both Touch ID and passwords. It was first implemented in the iPhone 5S and is still used in current Apple devices. From the iPhones with A8-A10X chip, the Blackbird exploit enables the SEP to run unsigned firmware. For the A7 chip, however, there is the Hardbird exploit which we do not know how to use yet.

# Compatibility

macOS 10.13+ in Intel is supported, and I will add Linux and ARM64 Mac support later on. The Python-based sochiDG clients can run in both Python 3.9 and 3.14, but I have not tested other versions.

# Compiling source code and running (does not apply with releases)
Since some do not fit into the maximum GitHub file requirement you can either run it as is and let the program download it or:
* Place these files in the ramdisk folder:
* Download ramdisk.im4p from [here.](https://www.mediafire.com/file/aya3nbyzqp7xrm3/ramdisk.im4p/file#)
* Download ramdisk.dmg from [here.](https://www.mediafire.com/file/i3cvx8mz7ehtlqk/ramdisk.dmg/file)
* Place this file in the 7.1.2 folder
* Download ios7.tar from [here.](https://www.mediafire.com/file/i3cvx8mz7ehtlqk/ramdisk.dmg/file)

For the C binary, please run compiler.py by running the command "python3 compiler.py"

# How to run and execute (and downgrade)
* Step 1: CD into the downgrade by typing in "cd sochiDG" or "cd 5s_downgrade"
* Step 2: Run this command: "python3 main.py" or just "./sochiDG/.sh -d". However, you need to install the necessary tools put in the tools folder as this tool is in very rough condition.
* Step 3: Downgrade
* Step 4: Boot (./sochiDG/.sh -b)
* Step 5: Profit

# Activating iPhone after downgrade

After booting into the setup screen, do the following:
* Select your country
* When in WiFi connection screen, click "Connect to iTunes" until the recovery mode logo appears (while not in recovery mode).
* Go to Finder/iTunes and let it activate the iPhone
* Profit

# Pretty necessary stuff

* The full downgrade folder will be around 2 GB after extraction as automating the downloads in the script might cause faliure in the process.

