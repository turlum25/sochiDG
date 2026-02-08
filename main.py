#!/usr/local/bin/python3

# hecking

import os
import time
import subprocess
import platform
import argparse

rsafix = "-o HostKeyAlgorithms=+ssh-rsa -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"


parser = argparse.ArgumentParser(description="sochiDG")
parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
args = parser.parse_args()

def recovery():
    print("[*] Sending device to recovery mode...")
    subprocess.run("tools/ideviceenterrecovery $(idevice_id -l)", shell=True)
    time.sleep(3)
    print("[*] Device should now be in recovery mode.")


def ramdisk():
    print("[*] Sending ramdisk...")
    os.system("tools/ipwnder")

    ibss = "tools/irecovery -f ramdisk/iBSS.img4"
    ibec = "tools/irecovery -f ramdisk/iBEC.img4"
    ramdisk = "tools/irecovery -f ramdisk/ramdisk.img4"
    ramdisk2 = "tools/irecovery -c ramdisk"
    dtre = "tools/irecovery -f ramdisk/devicetree.img4"
    dtre2 = "tools/irecovery -c devicetree"
    krnl = "tools/irecovery -f ramdisk/kernelcache.img4"
    boot = "tools/irecovery -c bootx"

    print("[*] Sending iBSS")
    print()
    os.system(ibss)
    os.system(ibss)
    time.sleep(2)
    print("[*] Sending iBEC")
    print()
    os.system(ibec)
    print("[*] Sending ramdisk")
    print()
    os.system(ramdisk)
    os.system(ramdisk2)
    time.sleep(1)
    print("[*] Sending DeviceTree")
    print()
    os.system(dtre)
    os.system(dtre2)
    os.system(krnl)
    print("[*] Booting...")
    time.sleep(2)
    os.system(boot)


def preparedsk():

    ramdisk()

    print("[*] Waiting 60 seconds for ramdisk to boot and run server")
    time.sleep(60)

    #iproxy, testing stuff

    print("[*] Starting iProxy in background....")

    iproxy = subprocess.Popen(["tools/iproxy", "2222", "44"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    time.sleep(5)

    os.system(f"timeout 5s sh -c \"output=$(tools/sshpass -p 'alpine' ssh -o StrictHostKeyChecking=no -l root {rsafix} -p 2222 127.0.0.1 'echo test'); if [ '$output' == '' ]; then sleep 5; fi\" || exit")
    os.system(f"tools/sshpass -p 'alpine' ssh -o StrictHostKeyChecking=no -l root {rsafix} -p 2222 127.0.0.1 'echo test'")


    # prepre nand
    subprocess.run([
        "sshpass", "-p", "alpine",
        "ssh", rsafix, "-p", "2222", "-tt",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "UserKnownHostsFile=/dev/null",
        "root@localhost", "lwvm init"
    ], check=True)

    time.sleep(2)

    # reboot
    subprocess.run([
        "sshpass", "-p", "alpine",
        "ssh", rsafix, "-p", "2222",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "UserKnownHostsFile=/dev/null",
        "root@localhost", "/sbin/reboot"
    ], check=True)

    iproxy.terminate()

    # dfu thing
    os.system("tools/dfuhelper.sh")


def send_fs():
    ramdisk()

    print("[*] Waiting 60 seconds for ramdisk to boot and run server")
    time.sleep(60)

    #iproxy, testing stuff

    print("[*] Starting iProxy in background....")

    iproxy = subprocess.Popen(["tools/iproxy", "2222", "44"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    time.sleep(5)

    os.system("output=$(tools/sshpass -p 'alpine' ssh -o StrictHostKeyChecking=no -l root -p 2222 127.0.0.1 'echo test'); if [ \"$output\" == \"\" ]; then sleep 5; exit; fi")

    os.system("tools/sshpass -p 'alpine' ssh -l root -p 2222 127.0.0.1 'echo test'")


    # mm partition!
    partition_cmd = "printf 'n\\n1\\n\\n786438\\n\\nn\\n2\\n\\n\\n\\nw\\ny\\n' | gptfdisk /dev/rdisk0s1"
    subprocess.run(["sshpass", "-p", "alpine", "ssh", rsafix, "-p", "2222",
                    "-o", "StrictHostKeyChecking=no",
                    "-o", "UserKnownHostsFile=/dev/null",
                    "root@localhost", partition_cmd], check=True)

    time.sleep(5)

    # a bunch of syncs (or 2)
    subprocess.run(["sshpass", "-p", "alpine", "ssh", rsafix, "-p", "2222",
                    "-o", "StrictHostKeyChecking=no",
                    "-o", "UserKnownHostsFile=/dev/null",
                    "root@localhost", "sync"], check=True)

    subprocess.run(["sshpass", "-p", "alpine", "ssh", rsafix, "-p", "2222",
                    "-o", "StrictHostKeyChecking=no",
                    "-o", "UserKnownHostsFile=/dev/null",
                    "root@localhost", "sync"], check=True)

    # 4mat da nand ig
    subprocess.run(["sshpass", "-p", "alpine", "ssh", rsafix, "-p", "2222",
                    "-o", "StrictHostKeyChecking=no",
                    "-o", "UserKnownHostsFile=/dev/null",
                    "root@localhost",
                    "/sbin/newfs_hfs -s -v System -J -b 4096 -n a=4096,c=4096,e=4096 /dev/disk0s1s1"], check=True)

    time.sleep(2)

    # format data
    subprocess.run(["sshpass", "-p", "alpine", "ssh", rsafix, "-p", "2222",
                    "-o", "StrictHostKeyChecking=no",
                    "-o", "UserKnownHostsFile=/dev/null",
                    "root@localhost",
                    "/sbin/newfs_hfs -s -v Data -J -b 4096 -n a=4096,c=4096,e=4096 /dev/disk0s1s2"], check=True)

    time.sleep(2)

    # time to mont
    subprocess.run(["sshpass", "-p", "alpine", "ssh", rsafix, "-p", "2222",
                    "-o", "StrictHostKeyChecking=no",
                    "-o", "UserKnownHostsFile=/dev/null",
                    "root@localhost", "/sbin/mount_hfs /dev/disk0s1s1 /mnt1"], check=True)

    time.sleep(1)

    subprocess.run(["sshpass", "-p", "alpine", "ssh", rsafix, "-p", "2222",
                    "-o", "StrictHostKeyChecking=no",
                    "-o", "UserKnownHostsFile=/dev/null",
                    "root@localhost", "/sbin/mount_hfs /dev/disk0s1s2 /mnt2"], check=True)

    print("[*] Sending filesystem...")
    print()
    print("[*] Waiting 3 seconds")
    time.sleep(3)

    subprocess.run(["sshpass", "-p", "alpine", "scp", rsafix, "-P", "2222", "7.1.2/ios7.tar", "root@localhost:/mnt2"], check=True)

    print("[*] Done sending filesystem tarball! If it fails, try restarting downgrade process.")
    print()

    # move ios 7 tar && extract
    subprocess.run(["sshpass", "-p", "alpine", "ssh", rsafix, "-p", "2222", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", "root@localhost", "tar -xvf /mnt2/ios7.tar -C /mnt1"], check=True)
    subprocess.run(["sshpass", rsafix, "-p", "alpine", "ssh", "-p", "2222", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", "root@localhost", "mv -v /mnt1/private/var/* /mnt2"], check=True)

    # make some stuff, i guess
    subprocess.run(["sshpass", "-p", "alpine", "ssh", rsafix, "-p", "2222", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", "root@localhost", "mkdir -p /mnt2/keybags /mnt1/usr/local/standalone/firmware/Baseband"], check=True)
    time.sleep(1)

    # send stuff
    subprocess.run(["sshpass", "-p", "alpine", "scp", rsafix, "-r", "-P", "2222", "./keybags", "root@localhost:/mnt2/"], check=True)
    subprocess.run(["sshpass", "-p", "alpine", "scp", rsafix, "-r", "-P", "2222", "./Baseband", "root@localhost:/mnt1/usr/local/standalone/firmware/"], check=True)
    subprocess.run(["sshpass", "-p", "alpine", "scp", rsafix, "-P", "2222", "./apticket.der", "root@localhost:/mnt1/System/Library/Caches/"], check=True)
    subprocess.run(["sshpass", "-p", "alpine", "scp", rsafix, "-P", "2222", "./sep-firmware.img4", "root@localhost:/mnt1/usr/standalone/firmware/"], check=True)
    subprocess.run(["sshpass", "-p", "alpine", "scp", rsafix, "-P", "2222", "7.1.2/fstab", "root@localhost:/mnt1/etc/"], check=True)

    time.sleep(1)

    # patching sum boot filez

    subprocess.run(["sshpass", "-p", "alpine", "ssh", rsafix, "-p", "2222", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", "root@localhost", "/usr/sbin/chown -R root:wheel /mnt2/keybags && /bin/chmod -R 755 /mnt2/keybags"], check=True)

    # there we go
    subprocess.run(["sshpass", "-p", "alpine", "ssh", "-p", "2222", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", "root@localhost", "/sbin/reboot"], check=True)

    time.sleep(1)
    print()
    print("[*] Flashed filesystem and rebooted device")

    iproxy.terminate()



def collect_stuff():

    #iproxy, testing stuff

    print("[*] Starting iProxy in background....")

    iproxy = subprocess.Popen(["tools/iproxy", "2222", "22"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


    os.system(f"tools/sshpass -p 'alpine' ssh -l root {rsafix} -p 2222 127.0.0.1 'echo test'")


    time.sleep(10)


    print("[*] Dumping files from device...")
    os.system(f"sshpass -p 'alpine' scp {rsafix} -P 2222 root@localhost:/System/Library/Caches/apticket.der ./apticket.der")
    os.system(f"sshpass -p 'alpine' scp {rsafix} -P 2222 root@localhost:/usr/standalone/firmware/sep-firmware.img4 ./sep-firmware.img4")
    os.system(f"sshpass -p 'alpine' scp {rsafix} -r -P 2222 root@localhost:/usr/local/standalone/firmware/Baseband ./Baseband")
    os.system(f"sshpass -p 'alpine'  scp {rsafix} -r -P 2222 root@localhost:/var/keybags ./keybags")
    print("[*] Dump complete.")

    iproxy.terminate()



def make_im4m():
    shsh2_file = input("[*] Drag your shsh2 file, this will be mandatory for signing components later on: ")
    if ".shsh2" not in shsh2_file:
        print("[*] Not shsh2 file, cannot continue.")
        exit()

    if ".shsh2" in shsh2_file:
        print("[*] Converting .shsh2 file to IM4M... ")
        os.system(f"tools/img4tool -e -s {shsh2_file} -m IM4M")

def boot():
    print("[*] Sending boot files...")
    pwn = os.system("tools/ipwnder")

    ibss = "tools/irecovery -f 7.1.2/iBSS.img4"
    ibec = "tools/irecovery -f 7.1.2/iBEC.img4"
    dtre = "tools/irecovery -f 7.1.2/devicetree.img4"
    dtre2 = "tools/irecovery -c devicetree"
    krnl = "tools/irecovery -f 7.1.2/kernelcache.img4"
    boot = "tools/irecovery -c bootx"

    print("[*] Sending iBSS")
    print()
    os.system(ibss)
    os.system(ibss)
    time.sleep(2)
    print("[*] Sending iBEC")
    print()
    os.system(ibec)
    time.sleep(1)
    print("[*] Sending DeviceTree")
    print()
    os.system(dtre)
    os.system(dtre2)
    os.system(krnl)
    print("[*] Booting...")
    time.sleep(2)
    os.system(boot)
    time.sleep(10)
    print()
    print("[*] Booted into iOS 7.1.2! ")
    exit()

def downgrade():
        print()
        warning = input("[*] WARNING: This will erase all data from your device. Would you like to continue? (Y/n) ")
        if warning.lower() == "n":
            print("[-] User selected N, cannot continue.")
            os.system("clear")
            exit()

        if warning.lower() == "y":
            print("[*] User selected Y, continuing.")
            collect_stuff()
            make_im4m()
            os.system("tools/img4tool -c ramdisk/ramdisk.img4 -p ramdisk/ramdisk.im4p -m IM4M")

            print("[*] Sending device to recovery mode...")
            recovery()
            os.system("tools/dfuhelper.sh")
            preparedsk()
            send_fs()
            print()
            print("[*] Restored to iOS 7.1.2 (hopefully)")
            print("[*] Clearing up stuff...")
            os.system("rm ramdisk/ramdisk.img4")
            os.system("rm IM4M")
            print("[*] Done cleaning up, quitting.")
            exit()

# main UI (finally)

time.sleep(1)



print("Starting sochiDG....")

mac_ver = int(platform.mac_ver()[0].split('.')[0])

os.system("clear")
print("*** sochiDG ***")
print("Script by Turlum25")
print("Version 0.3 (9065cdd)")
print()
time.sleep(1)
print("[*] Starting...")
if args.debug:
    print("[WARNING] You have enabled the --debug flag which is currently buggy at the moment.")

if mac_ver >= 12:
    time.sleep(1)
    print(f"[*] macOS Version: {mac_ver}.x")

    time.sleep(2)
else:
    print(f"[-] macOS Version: {mac_ver}.x, Running compatibility mode.")
    time.sleep(3)
    os.system(f"python3 classic.py")
    exit()


while True:

    os.system("clear")
    print("*** sochiDG ***")
    print("Script by Turlum25")
    print("Version 0.3 (9065cdd)")
    print()
    print("1 > Downgrade")
    print("2 > Boot iOS 7.1.2")
    print("3 > Exit")
    print("------------------")
    if args.debug:
        print("Debug Tools: ")
        print()
        print("5 > SSH Ramdisk")
    print()
    main= input("Select a number: ")

    if main == "3":
        print("Exiting....")
        time.sleep(2)
        os.system("clear")
        exit()

    elif main == "1":
        downgrade()

    elif main == "2":
        os.system("tools/dfuhelper.sh")
        boot()

    elif args.debug and main == "5":
        recovery()
        os.system("tools/dfuhelper.sh")
        ramdisk()
