#!/bin/bash

# FROM TURLUM25:
# THIS IS STILL A BETA. UNTESTED (ONLY EXCEPT FOR -B) AND MAY NOT WORK PROPERLY
# I DID NOT USE AI FOR THIS, AND VS CODE IS TRYING TO COMPLETE MY CODE
# AND NO I HATE VIBE CODING

# ---- Resolve script directory ----
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

step() {
    for i in $(seq "$1" -1 1); do
        printf '\r\e[1;36m%s (%d) ' "$2" "$i"
        sleep 1
    done
    printf '\r\e[0m%s (0)\n' "$2"
}

dfuhelper() {
    echo "[*] Press any key when ready for DFU mode"
    step 3 "Get ready"
    step_one="Hold home + power button"
    step 8 "$step_one" &
    sleep 9
    step 10 'Release power button, but keep holding home button'
    sleep 1
}


#$SCRIPT_DIR/tools/iproxy 2222 44 > iproxy.log 2>&1 &

#IPROXY_PID=$!

ramdisk() {

    

    dfuhelper

    $SCRIPT_DIR/tools/ipwnder

    $SCRIPT_DIR/tools/irecovery -f $SCRIPT_DIR/ramdisk/iBSS.img4
    $SCRIPT_DIR/tools/irecovery -f $SCRIPT_DIR/ramdisk/iBSS.img4

    $SCRIPT_DIR/tools/irecovery -f $SCRIPT_DIR/ramdisk/iBEC.img4

    $SCRIPT_DIR/tools/irecovery -f $SCRIPT_DIR/ramdisk/ramdisk.img4
    $SCRIPT_DIR/tools/irecovery -c ramdisk

    $SCRIPT_DIR/tools/irecovery -f $SCRIPT_DIR/ramdisk/devicetree.img4
    $SCRIPT_DIR/tools/irecovery -c devicetree

    $SCRIPT_DIR/tools/irecovery -f $SCRIPT_DIR/ramdisk/kernelcache.img4

    $SCRIPT_DIR/tools/irecovery -c bootx

}

testSSH() {
    $SCRIPT_DIR/tools/sshpass -p 'alpine' ssh -o StrictHostKeyChecking=no -l root -p 2222 127.0.0.1 'echo [*] SSH Connection successful'
}

prepareNAND() {

    ramdisk

    step 60 "[*] Waiting for device to boot and run server"    

    $SCRIPT_DIR/tools/iproxy 2222 44 > iproxy.log 2>&1 &

    IPROXY_PID=$!

    timeout 5s testSSH
    timeout 5s testSSH

    $SCRIPT_DIR/tools/sshpass -p 'alpine' ssh -p 2222 -tt -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o UserKnownHostsFile=/dev/null root@localhost lwvm init
    $SCRIPT_DIR/tools/sshpass -p 'alpine' ssh -p 2222 -tt -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o UserKnownHostsFile=/dev/null root@localhost sbin/reboot

    echo "[*] NAND preparation complete."

    kill $IPROXY_PID



}

sendFS() {

    ramdisk

    step 60 "[*] Waiting for device to boot and run server"    

    $SCRIPT_DIR/tools/iproxy 2222 44 > iproxy.log 2>&1 &

    IPROXY_PID=$!

    PARTITION="printf 'n\\n1\\n\\n786438\\n\\nn\\n2\\n\\n\\n\\nw\\ny\\n' | gptfdisk /dev/rdisk0s1"

    sshpass -p alpine ssh -p 2222 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost $PARTITION

    sync="$SCRIPT_DIR/tools/sshpass -p 'alpine' ssh -p 2222 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost sync"

    $sync
    $sync
    $sync
    $sync
    $sync
    $sync
    $sync
    $sync
    $sync
    $sync

    sleep 3

    $SCRIPT_DIR/tools/sshpass -p 'alpine' ssh -p 2222 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost /sbin/newfs_hfs -s -v System -J -b 4096 -n a=4096,c=4096,e=4096 /dev/disk0s1s1
    $SCRIPT_DIR/tools/sshpass -p 'alpine' ssh -p 2222 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost /sbin/newfs_hfs -s -v Data -J -b 4096 -n a=4096,c=4096,e=4096 /dev/disk0s1s2

    
    $SCRIPT_DIR/tools/sshpass -p 'alpine' ssh -p 2222 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost /sbin/mount_hfs /dev/disk0s1s1 /mnt1
    $SCRIPT_DIR/tools/sshpass -p 'alpine' ssh -p 2222 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost /sbin/mount_hfs /dev/disk0s1s2 /mnt2

    $SCRIPT_DIR/tools/sshpass -p 'alpine' scp -P 2222 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null 7.1.2/ios7.tar root@localhost:/mnt2
    $SCRIPT_DIR/tools/sshpass -p 'alpine' ssh -p 2222 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost tar -xvf /mnt2/ios7.tar -C /mnt1

    $SCRIPT_DIR/tools/sshpass -p 'alpine' ssh -p 2222 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost mv -v /mnt1/private/var/* /mnt2

    $SCRIPT_DIR/tools/sshpass -p 'alpine' ssh -p 2222 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost mkdir -p /mnt2/keybags 
    $SCRIPT_DIR/tools/sshpass -p 'alpine' ssh -p 2222 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost mkdir -p /mnt2/keybags /mnt1/usr/local/standalone/firmware/Baseband

    $SCRIPT_DIR/tools/sshpass -p 'alpine' scp -r -P 2222 $SCRIPT_DIR/keybags root@localhost:/mnt2/
    $SCRIPT_DIR/tools/sshpass -p 'alpine' scp -r -P 2222 $SCRIPT_DIR/Baseband root@localhost:/mnt1/usr/local/standalone/firmware/
    $SCRIPT_DIR/tools/sshpass -p 'alpine' scp -P 2222 $SCRIPT_DIR/apticket.der root@localhost:/mnt1/System/Library/Caches/
    $SCRIPT_DIR/tools/sshpass -p 'alpine' scp -P 2222 $SCRIPT_DIR/sep-firmware.img4 root@localhost:/mnt1/usr/standalone/firmware/
    $SCRIPT_DIR/tools/sshpass -p 'alpine' scp -P 2222 $SCRIPT_DIR/fstab root@localhost:/mnt1/etc/
    $SCRIPT_DIR/tools/sshpass -p 'alpine' ssh -p 2222 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost /usr/sbin/chown -R root:wheel /mnt2/keybags && /bin/chmod -R 755 /mnt2/keybags

    $SCRIPT_DIR/tools/sshpass -p 'alpine' ssh -p 2222 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost /sbin/reboot

    echo "[*] Flashed filesystem and rebooted device"

    kill $IPROXY_PID

}

bootFiles() {
    cd $SCRIPT_DIR && tools/img4 -i 7.1.2/iBSS.patched -o 7.1.2/iBSS.img4 -M IM4M -A -T ibss
    cd $SCRIPT_DIR && tools/img4 -i 7.1.2/iBEC.patched -o 7.1.2/iBEC.img4 -M IM4M -A -T ibec

    cd $SCRIPT_DIR && tools/img4 -i 7.1.2/kernelcache.im4p -o 7.1.2/kernelcache.img4 -M IM4M -T rkrn -P 7.1.2/kc.bpatch

    cd $SCRIPT_DIR && tools/img4 -i 7.1.2/dtree.raw -o 7.1.2/devicetree.img4 -A -M IM4M -T rdtr  
}


makeIM4M() {
    read -p "[*] Drag your shsh2 file, this will be mandatory for signing components later on: " shsh2_file
    
    if [[ "$shsh2_file" != *".shsh2"* ]]; then
        echo "[-] Not shsh2 file, cannot continue."
        exit 1
    fi
    
    echo "[*] Converting .shsh2 file to IM4M... "
    $SCRIPT_DIR/tools/img4tool -e -s "$shsh2_file" -m IM4M
}

collectStuff() {
    echo "[*] Collecting files from device..."
    $SCRIPT_DIR/tools/iproxy 2222 22 > iproxy.log 2>&1 &
    IPROXY_PID=$!

    timeout 5s testSSH
    timeout 5s testSSH
    
    $SCRIPT_DIR/tools/sshpass -p 'alpine' scp -P 2222 root@localhost:/System/Library/Caches/apticket.der ./apticket.der
    $SCRIPT_DIR/tools/sshpass -p 'alpine' scp -P 2222 root@localhost:/usr/standalone/firmware/sep-firmware.img4 ./sep-firmware.img4
    $SCRIPT_DIR/tools/sshpass -p 'alpine' scp -r -P 2222 root@localhost:/usr/local/standalone/firmware/Baseband ./Baseband
    $SCRIPT_DIR/tools/sshpass -p 'alpine'  scp -r -P 2222 root@localhost:/var/keybags ./keybags

    echo "[*] Collection complete."

    kill $IPROXY_PID
}

boot() {
    dfuhelper
    bootFiles
    echo "[*] Entering PwnDFU mode"
    $SCRIPT_DIR/tools/ipwnder

    echo "[*] Sending boot files..."
    $SCRIPT_DIR/tools/irecovery -f $SCRIPT_DIR/7.1.2/iBSS.img4
    $SCRIPT_DIR/tools/irecovery -f $SCRIPT_DIR/7.1.2/iBSS.img4
    $SCRIPT_DIR/tools/irecovery -f $SCRIPT_DIR/7.1.2/iBEC.img4
    $SCRIPT_DIR/tools/irecovery -f $SCRIPT_DIR/7.1.2/devicetree.img4
    $SCRIPT_DIR/tools/irecovery -c devicetree
    $SCRIPT_DIR/tools/irecovery -f $SCRIPT_DIR/7.1.2/kernelcache.img4
    $SCRIPT_DIR/tools/irecovery -c bootx

    echo "[*] Booted into iOS 7.1.2 (11D257)"
}

checkiOS7Tar() {
    [ -f './7.1.2/ios7.tar' ]
    check=$?
    
    if [ $check -eq 0 ]; then
       echo "[Log] Found ios7.tar, continuing."
        return 0
    else
        echo "[Log] Could not find ios7.tar."
        return 1
    fi
}

checkRamdiskDMG() {
    [ -f './ramdisk/ramdisk.dmg' ]
    check=$?
        
    if [ $check -eq 0 ]; then
        echo "[Log] Found ramdisk.dmg, continuing."
        return 0
    else
        echo "[Log] Could not find ramdisk.dmg."
        return 1
    fi
}

checkRamdiskIM4P() {
    [ -f './ramdisk/ramdisk.im4p' ]
    check=$?
        
    if [ $check -eq 0 ]; then
        echo "[Log] Found ramdisk.im4p, continuing."
        return 0
    else
        echo "[Log] Could not find ramdisk.im4p."
        return 1
    fi
}

checkIfNecessaryFilesExist() {
    # checks if the necessary files for a downgrade are existent which are:
    # ios7.tar in 7.1.2 folder, ramdisk.dmg and ramdisk.im4p in ramdisk folder.
    # p.s this is not vibe coded, wen eta printf in c without stdio.h :P
    

    checkiOS7Tar
    check1=$?
    checkRamdiskDMG
    check2=$?
    checkRamdiskIM4P
    check3=$?

    if [ $check1 -eq 0 ]; then
        echo "[*] Found ios7.tar, continuing."
    fi
    if [ $check1 -ne 0 ]; then
        echo "[-] Could not find ios7.tar, downloading."
        curl -L https://github.com/turlum25/sochidg-files/releases/download/FILES/ios7.tar.zip -o ./7.1.2/ios7.tar.zip
        unzip -q ./7.1.2/ios7.tar.zip -d ./7.1.2/
        rm ./7.1.2/ios7.tar.zip
    fi

    if [ $check2 -eq 0 ]; then
        echo "[*] Found ramdisk.dmg, continuing."
    fi
    if [ $check2 -ne 0 ]; then
        echo "[-] Could not find ramdisk.dmg, downloading."
        curl -L https://github.com/turlum25/sochidg-files/releases/download/FILES/ramdisk.dmg -o ./ramdisk/ramdisk.dmg
    fi

    if [ $check3 -eq 0 ]; then
        echo "[*] Found ramdisk.im4p, continuing."
    fi
    if [ $check3 -ne 0 ]; then
        echo "[-] Could not find ramdisk.im4p, downloading."
        curl -L https://github.com/turlum25/sochidg-files/releases/download/FILES/ramdisk.im4p -o ./ramdisk/ramdisk.im4p
    fi

    # added: v0.4~b5
    # probably april fools today but eh who cares
    # v20260401

}


# make args existent
downgrade_flag=0
ramdisk_flag=0
boot_flag=0

while getopts "drb" opt; do
    case $opt in
        d)
            downgrade_flag=1
            ;;
        r)
            ramdisk_flag=1
            ;;
        b)
            boot_flag=1
            ;;
        *)
            exit 1
            ;;
    esac
done


if [[ $# -eq 0 ]] || [[ $downgrade_flag -eq 0 && $ramdisk_flag -eq 0 && $boot_flag -eq 0 ]]; then
    echo "sochiDG - Script by Turlum25"
    echo "Version 0.4-beta5"
    echo "----------------------------"
    echo "Usage: $0 [-d] [-r] [-b]"
    echo "  -d      Downgrade iPhone to iOS 7.1.2 (11D257)"
    echo "  -r      Enter ramdisk mode"
    echo "  -b      Boot iOS 7.1.2 (11D257)"
    exit 0
fi


if [[ $downgrade_flag -eq 1 ]]; then
    echo "sochiDG - Script by Turlum25"
    echo "Version 0.4-beta5"
    echo "----------------------------"
    checkIfNecessaryFilesExist
    makeIM4M
    echo 
    echo "[*] Compiling boot files..."
    bootFiles
    echo "[*] Done compiling boot files, continuing."
    collectStuff
    $SCRIPT_DIR/tools/img4tool -c ramdisk/ramdisk.img4 -p ramdisk/ramdisk.im4p -m IM4M
    echo "[*] Starting downgrade to iOS 7.1.2 (11D257)..."
    prepareNAND
    sendFS    
    echo "[*] Done restoring to iOS 7.1.2 (hopefully!)"
    exit 0
fi


if [[ $ramdisk_flag -eq 1 ]]; then
    echo "sochiDG - Script by Turlum25"
    echo "Version 0.4-beta5"
    echo "----------------------------"
    echo "[*] Entering ramdisk mode..."
    ramdisk
    exit 0
fi


if [[ $boot_flag -eq 1 ]]; then
    echo "sochiDG - Script by Turlum25"
    echo "Version 0.4-beta5"
    echo "----------------------------"
    boot
fi

exit 0


