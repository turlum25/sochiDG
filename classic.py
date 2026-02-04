#!/usr/local/bin/python3

import os
import time
import subprocess
import platform

def recovery():
    print("[*] Sending device to recovery mode...")
    subprocess.run("tools/ideviceenterrecovery $(idevice_id -l)", shell=True)
    time.sleep(3)
    print("[*] Device should now be in recovery mode.")


def ramdisk():
    print("[*] Sending ramdisk...")
    pwn = os.popen("tools/ipwnder").read()

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

    os.system("output=$(tools/sshpass -p 'alpine' ssh -o StrictHostKeyChecking=no -l root -p 2222 127.0.0.1 'echo test'); if [ \"$output\" == \"\" ]; then sleep 5; exit; fi")

    os.system("tools/sshpass -p 'alpine' ssh -o StrictHostKeyChecking=no -l root -p 2222 127.0.0.1 'echo test'")


    # prepre nand
    subprocess.run([
        "sshpass", "-p", "alpine",
        "ssh", "-p", "2222", "-tt",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "UserKnownHostsFile=/dev/null",
        "root@localhost", "lwvm init"
    ], check=True)

    time.sleep(2)

    # reboot
    subprocess.run([
        "sshpass", "-p", "alpine",
        "ssh", "-p", "2222",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "UserKnownHostsFile=/dev/null",
        "root@localhost", "/sbin/reboot"
    ], check=True)

    iproxy.terminate()

    # DFU Helper
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
    subprocess.run(["sshpass", "-p", "alpine", "ssh", "-p", "2222",
                    "-o", "StrictHostKeyChecking=no",
                    "-o", "UserKnownHostsFile=/dev/null",
                    "root@localhost", partition_cmd], check=True)

    time.sleep(5)

    # a bunch of syncs (or 2)
    subprocess.run(["sshpass", "-p", "alpine", "ssh", "-p", "2222",
                    "-o", "StrictHostKeyChecking=no",
                    "-o", "UserKnownHostsFile=/dev/null",
                    "root@localhost", "sync"], check=True)

    subprocess.run(["sshpass", "-p", "alpine", "ssh", "-p", "2222",
                    "-o", "StrictHostKeyChecking=no",
                    "-o", "UserKnownHostsFile=/dev/null",
                    "root@localhost", "sync"], check=True)

    # 4mat da nand ig
    subprocess.run(["sshpass", "-p", "alpine", "ssh", "-p", "2222",
                    "-o", "StrictHostKeyChecking=no",
                    "-o", "UserKnownHostsFile=/dev/null",
                    "root@localhost",
                    "/sbin/newfs_hfs -s -v System -J -b 4096 -n a=4096,c=4096,e=4096 /dev/disk0s1s1"], check=True)

    time.sleep(2)

    # format data
    subprocess.run(["sshpass", "-p", "alpine", "ssh", "-p", "2222",
                    "-o", "StrictHostKeyChecking=no",
                    "-o", "UserKnownHostsFile=/dev/null",
                    "root@localhost",
                    "/sbin/newfs_hfs -s -v Data -J -b 4096 -n a=4096,c=4096,e=4096 /dev/disk0s1s2"], check=True)

    time.sleep(2)

    # time to mont
    subprocess.run(["sshpass", "-p", "alpine", "ssh", "-p", "2222",
                    "-o", "StrictHostKeyChecking=no",
                    "-o", "UserKnownHostsFile=/dev/null",
                    "root@localhost", "/sbin/mount_hfs /dev/disk0s1s1 /mnt1"], check=True)

    time.sleep(1)

    subprocess.run(["sshpass", "-p", "alpine", "ssh", "-p", "2222",
                    "-o", "StrictHostKeyChecking=no",
                    "-o", "UserKnownHostsFile=/dev/null",
                    "root@localhost", "/sbin/mount_hfs /dev/disk0s1s2 /mnt2"], check=True)

    print("[*] Sending filesystem...")
    print()
    print("[*] Waiting 3 seconds")
    time.sleep(3)

    subprocess.run(["sshpass", "-p", "alpine", "scp", "-P", "2222", "7.1.2/ios7.tar", "root@localhost:/mnt2"], check=True)

    print("[*] Done sending filesystem tarball! If it fails, try restarting downgrade process.")
    print()

    # move ios 7 tar && extract
    subprocess.run(["sshpass", "-p", "alpine", "ssh", "-p", "2222", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", "root@localhost", "tar -xvf /mnt2/ios7.tar -C /mnt1"], check=True)
    subprocess.run(["sshpass", "-p", "alpine", "ssh", "-p", "2222", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", "root@localhost", "mv -v /mnt1/private/var/* /mnt2"], check=True)

    # make some stuff, i guess
    subprocess.run(["sshpass", "-p", "alpine", "ssh", "-p", "2222", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", "root@localhost", "mkdir -p /mnt2/keybags /mnt1/usr/local/standalone/firmware/Baseband"], check=True)
    time.sleep(1)

    # send stuff
    subprocess.run(["sshpass", "-p", "alpine", "scp", "-r", "-P", "2222", "./keybags", "root@localhost:/mnt2/"], check=True)
    subprocess.run(["sshpass", "-p", "alpine", "scp", "-r", "-P", "2222", "./Baseband", "root@localhost:/mnt1/usr/local/standalone/firmware/"], check=True)
    subprocess.run(["sshpass", "-p", "alpine", "scp", "-P", "2222", "./apticket.der", "root@localhost:/mnt1/System/Library/Caches/"], check=True)
    subprocess.run(["sshpass", "-p", "alpine", "scp", "-P", "2222", "./sep-firmware.img4", "root@localhost:/mnt1/usr/standalone/firmware/"], check=True)
    subprocess.run(["sshpass", "-p", "alpine", "scp", "-P", "2222", "7.1.2/fstab", "root@localhost:/mnt1/etc/"], check=True)

    time.sleep(1)

    # patching sum boot filez

    subprocess.run(["sshpass", "-p", "alpine", "ssh", "-p", "2222", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", "root@localhost", "/usr/sbin/chown -R root:wheel /mnt2/keybags && /bin/chmod -R 755 /mnt2/keybags"], check=True)

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

    os.system("output=$(tools/sshpass -p 'alpine' ssh -o StrictHostKeyChecking=no -l root -p 2222 127.0.0.1 'echo test'); if [ \"$output\" == \"\" ]; then sleep 5; exit; fi")

    os.system("tools/sshpass -p 'alpine' ssh -l root -p 2222 127.0.0.1 'echo test'")


    time.sleep(10)


    print("[*] Dumping files from device...")
    os.system("sshpass -p 'alpine' scp -P 2222 root@localhost:/System/Library/Caches/apticket.der ./apticket.der")
    os.system("sshpass -p 'alpine' scp -P 2222 root@localhost:/usr/standalone/firmware/sep-firmware.img4 ./sep-firmware.img4")
    os.system("sshpass -p 'alpine' scp -r -P 2222 root@localhost:/usr/local/standalone/firmware/Baseband ./Baseband")
    os.system("sshpass -p 'alpine' scp -r -P 2222 root@localhost:/var/keybags ./keybags")
    print("[*] Dump complete.")

    iproxy.terminate()

def hacktiv8():

    print("[*] Waiting 60 seconds for ramdisk to boot and run server")
    time.sleep(60)

    #iproxy, testing stuff

    print("[*] Starting iProxy in background....")

    iproxy = subprocess.Popen(["tools/iproxy", "2222", "44"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    os.system("output=$(tools/sshpass -p 'alpine' ssh -o StrictHostKeyChecking=no -l root -p 2222 127.0.0.1 'echo test'); if [ \"$output\" == \"\" ]; then sleep 5; exit; fi")

    os.system("tools/sshpass -p 'alpine' ssh -l root -p 2222 127.0.0.1 'echo test'")


    os.system("sshpass -p 'alpine' ssh -p 2222 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost '/sbin/mount_hfs /dev/disk0s1s1 /mnt1 && mv /mnt1/Applications/Setup.app /mnt1/Applications/fuckYou_Setup && reboot'")

    iproxy.terminate()



def make_im4m():
    shsh2_file = input("[*] Drag your shsh2 file, this will be mandatory for signing components later on: ")
    if ".shsh2" not in shsh2_file:
        print("[*] Not shsh2 file, cannot continue.")
        exit()

    if ".shsh2" in shsh2_file:
        print("[*] Converting .shsh2 file to IM4M... ")
        os.system("tools/img4tool -e -s " + shsh2_file + " -m IM4M")

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

# main UI (finally)

time.sleep(1)



print("Starting sochiDG....")

mac_ver = int(platform.mac_ver()[0].split('.')[0])

os.system("clear")
print("*** sochiDG ***")
print("Script by Turlum25")
print("Version 0.2.1-legacy")
print()
time.sleep(1)
print("[*] Starting...")

time.sleep(1)
print("[*] macOS Version: " + str(mac_ver) + ".x")

time.sleep(2)

while True:

    os.system("clear")
    print("*** sochiDG ***")
    print("Script by Turlum25")
    print("Version 0.2.1-legacy")
    print()
    print("1 > Downgrade")
    print("2 > Hactivate iPhone")
    print("3 > Boot iOS 7.1.2")
    print("4 > Exit")
    print("------------------")
    print()
    main= input("Select a number: ")

    if main == "4":
        print("Exiting....")
        time.sleep(2)
        os.system("clear")
        exit()

    elif main == "1":
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

    elif main == "2":
        print("[*] Sending device to recovery mode.")
        recovery()
        os.system("tools/dfuhelper.sh")
        ramdisk()
        input("[*] Press enter if you want to hacktivate your device. If not, please exit by pressing CTRL+C")
        hacktiv8()

    elif main == "3":
        os.system("tools/dfuhelper.sh")
        boot()
