#include<stdio.h>
#include<unistd.h>
#include<getopt.h>
#include<stdlib.h>
#include<string.h>
#include<limits.h>
#include<libgen.h>
#include<stdbool.h>


// hecking


void helperDFU() {
    printf("\n[*] Press any key when you are ready for DFU mode");
    getchar(); // this thing

    printf("\n[*] Hold HOME and POWER buttons for seconds: \n");
    for (int i = 8; i > 0; i--) {
        printf("Time remaining: %d  \r", i);
        fflush(stdout);
        sleep(1);
    }

    printf("\n[*] Release POWER, keep holding HOME for seconds: \n");
    for (int i = 10; i > 0; i--) {
        printf("Time remaining: %d  \r", i);
        fflush(stdout);
        sleep(1);
    }

    printf("\n[*] Device should now be in DFU mode.\n");
}


void bootFiles() {
    system(
        "SCRIPT_DIR=\"$(cd \"$(dirname \"$0\")\" && pwd)\"; "
        "cd \"$SCRIPT_DIR\" && "
        "tools/img4 -i 7.1.2/iBSS.patched -o 7.1.2/iBSS.img4 -M IM4M -A -T ibss && "
        "tools/img4 -i 7.1.2/iBEC.patched -o 7.1.2/iBEC.img4 -M IM4M -A -T ibec && "
        "tools/img4 -i 7.1.2/kernelcache.im4p -o 7.1.2/kernelcache.img4 -M IM4M -T rkrn -P 7.1.2/kc.bpatch && "
        "tools/img4 -i 7.1.2/dtree.raw -o 7.1.2/devicetree.img4 -A -M IM4M -T rdtr"
    );
}





void prepareNAND()
{

    FILE *iproxy = popen("./tools/iproxy 2222 44", "r");

    printf("[*] Preparing for restore...\n");

    system("./tools/sshpass -p 'alpine' ssh -p 2222 -tt -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost 'lwvm init'");

    system("./tools/sshpass -p 'alpine' ssh -p 2222 -tt -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost '/sbin/reboot'");

    printf("[*] Done preparing for restore! ");

    pclose(iproxy);
}

void sendFS()
{

    FILE *iproxy = popen("./tools/iproxy 2222 44", "r");

    // gptfdisk thing

    char partition_cmd[] = "printf 'n\\n1\\n\\n786438\\n\\nn\\n2\\n\\n\\n\\nw\\ny\\n' | gptfdisk /dev/rdisk0s1";

    char final_ssh_cmd[1024];

    snprintf(final_ssh_cmd, sizeof(final_ssh_cmd), 
    "./tools/sshpass -p 'alpine' ssh -p 2222 -tt -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost \"%s\"", 
    partition_cmd);

    system(final_ssh_cmd);

    // a bunch of 'sync' commands

    system("./tools/sshpass -p 'alpine' ssh -p 2222 -tt -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost 'sync'");
    
    system("./tools/sshpass -p 'alpine' ssh -p 2222 -tt -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost 'sync'");

    system("./tools/sshpass -p 'alpine' ssh -p 2222 -tt -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost 'sync'");

    system("./tools/sshpass -p 'alpine' ssh -p 2222 -tt -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost 'sync'");

    system("./tools/sshpass -p 'alpine' ssh -p 2222 -tt -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost 'sync'");

    system("./tools/sshpass -p 'alpine' ssh -p 2222 -tt -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost 'sync'");

    // format partitions

    // /sbin/newfs_hfs -s -v System -J -b 4096 -n a=4096,c=4096,e=4096 /dev/disk0s1s1
    // /sbin/newfs_hfs -s -v Data -J -b 4096 -n a=4096,c=4096,e=4096 /dev/disk0s1s2

    system("./tools/sshpass -p 'alpine' ssh -p 2222 -tt -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost '/sbin/newfs_hfs -s -v System -J -b 4096 -n a=4096,c=4096,e=4096 /dev/disk0s1s1'");

    system("./tools/sshpass -p 'alpine' ssh -p 2222 -tt -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost '/sbin/newfs_hfs -s -v Data -J -b 4096 -n a=4096,c=4096,e=4096 /dev/disk0s1s2'");

    // now *mount* partitions

    // /sbin/mount_hfs /dev/disk0s1s1 /mnt1
    // /sbin/mount_hfs /dev/disk0s1s2 /mnt2

    system("./tools/sshpass -p 'alpine' ssh -p 2222 -tt -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost '/sbin/mount_hfs /dev/disk0s1s1 /mnt1'");

    system("./tools/sshpass -p 'alpine' ssh -p 2222 -tt -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost '/sbin/mount_hfs /dev/disk0s1s2 /mnt2'");

    printf("[*] Script will now send filesystem, waiting 3 seconds.\n");
    sleep(3);

    system("./tools/sshpass -p 'alpine' scp -P 2222 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ./ios7.tar root@localhost:/mnt2");

    // extract, move

    system("./tools/sshpass -p 'alpine' ssh -p 2222 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost 'tar -xvf /mnt2/ios7.tar -C /mnt1'");
    system("./tools/sshpass -p 'alpine' ssh -p 2222 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost 'mv -v /mnt1/private/var/* /mnt2'");

    system("./tools/sshpass -p 'alpine' ssh -p 2222 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost 'mkdir -p /mnt2/keybags /mnt1/usr/local/standalone/firmware/Baseband'");

    // send stuff

    system("./tools/sshpass -p 'alpine' scp -r -P 2222 ./keybags root@localhost:/mnt2/");
    system("./tools/sshpass -p 'alpine' scp -r -P 2222 ./Baseband root@localhost:/mnt1/usr/local/standalone/firmware/");
    system("./tools/sshpass -p 'alpine' scp -P 2222 ./apticket.der root@localhost:/mnt1/System/Library/Caches/");
    system("./tools/sshpass -p 'alpine' scp -P 2222 ./sep-firmware.img4 root@localhost:/mnt1/usr/standalone/firmware/");
    system("./tools/sshpass -p 'alpine' scp -P 2222 ./fstab root@localhost:/mnt1/etc/");

    // boot file patching?

    system("./tools/sshpass -p 'alpine' ssh -p 2222 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost '/usr/sbin/chown -R root:wheel /mnt2/keybags && /bin/chmod -R 755 /mnt2/keybags'");

    // the end of all suffering, praise reboot

    printf("[*] Sending reboot command to iPhone...\n");
    system("./tools/sshpass -p 'alpine' ssh -p 2222 -tt -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@localhost '/sbin/reboot'");

    printf("[*] Done sending filesystem! If it failed, please restart downgrade process.");

    pclose(iproxy);

}


void bootRamdisk()
{

    sleep(1);

    printf("[*] Entering PwnDFU mode\n");
    system("./tools/ipwnder");

    printf("[*] Entering Ramdisk...\n");
    
    system("./tools/irecovery -f ./ramdisk/iBSS.img4");
    system("./tools/irecovery -f ./ramdisk/iBSS.img4");
    sleep(1);

    system("./tools/irecovery -f ./ramdisk/iBEC.img4");
    sleep(1);

    system("./tools/irecovery -f ./ramdisk/ramdisk.img4");
    system("./tools/irecovery -c ramdisk");
    sleep(1);

    system("./tools/irecovery -f ./ramdisk/devicetree.img4");
    system("./tools/irecovery -c devicetree");
    sleep(1);

    system("./tools/irecovery -f ./ramdisk/kernelcache.img4");
    sleep(1);

    system("./tools/irecovery -c bootx");
    sleep(1);

    printf("[*] Booted into Ramdisk!");

}

void boot()
{

    helperDFU();
    printf("[*] Entering PwnDFU mode\n");
    system("./tools/ipwnder");

    printf("[*] Sending boot files...\n");
    system("./tools/irecovery -f ./7.1.2/iBSS.img4");
    system("./tools/irecovery -f ./7.1.2/iBSS.img4");
    system("./tools/irecovery -f ./7.1.2/iBEC.img4");
    system("./tools/irecovery -f ./7.1.2/devicetree.img4");
    system("./tools/irecovery -c devicetree");
    system("./tools/irecovery -f ./7.1.2/kernelcache.img4");
    system("./tools/irecovery -c bootx");
    
    printf("[*] Booted into iOS 7.1.2 (11D257)");

}

void collectIM4M()
{

    char shsh2_file[256];
    char command[512];

    printf("[*] Drag your shsh2 file, this will be mandatory for signing components later on: ");
    
    // wow such heck
    scanf("%255s", shsh2_file);

    // checking for .shsh2 extension
    if (strstr(shsh2_file, ".shsh2") == NULL) {
        printf("[*] Not shsh2 file, cannot continue.\n");
        exit(1);
    }

    // waw printing 
    printf("[*] Converting .shsh2 file to IM4M... \n");
    
    // build im4m? 
    snprintf(command, sizeof(command), "tools/img4tool -e -s %s -m IM4M", shsh2_file);
    
    // wow conver
    system(command);


}

void collectStuff()
{

    FILE *iproxy = popen("./tools/iproxy 2222 44", "r");

    printf("[*] Dumping files from iPhone\n");
    fflush(stdout);
    sleep(3);

    system("sshpass -p 'alpine' scp -P 2222 root@localhost:/System/Library/Caches/apticket.der ./apticket.der");
    system("sshpass -p 'alpine' scp -P 2222 root@localhost:/usr/standalone/firmware/sep-firmware.img4 ./sep-firmware.img4");
    system("sshpass -p 'alpine' scp -r -P 2222 root@localhost:/usr/local/standalone/firmware/Baseband ./Baseband");
    system("sshpass -p 'alpine'  scp -r -P 2222 root@localhost:/var/keybags ./keybags");

    printf("[*] Dump complete.");
    fflush(stdout);

    pclose(iproxy);

}

bool checkiOS7Tar() {
    int check = system("[ -f './7.1.2/ios7.tar' ]");
    
    if(check == 0) {
       printf("[Log] Found ios7.tar, continuing.\n");
        return true;
        }

        else {
            printf("[Log] Could not find ios7.tar.\n");
            return false;
        }
    }
    
bool checkRamdiskDMG() {
        int check = system("[ -f './ramdisk/ramdisk.dmg' ]");
        
        if(check == 0) {
            printf("[Log] Found ramdisk.dmg, continuing.\n");
            return true;
        }

        else {
            printf("[Log] Could not find ramdisk.dmg.\n");
            return false;
        }
}
    
bool checkRamdiskIM4P() {
    int check = system("[ -f './ramdisk/ramdisk.im4p' ]");
        
    if(check == 0) {
        printf("[Log] Found ramdisk.im4p, continuing.\n");
        return true;
    }

    else {
        printf("[Log] Could not find ramdisk.im4p.\n");
        return false;
    }
}
void checkIfNecessaryFilesExist() {
    // checks if the necessary files for a downgrade are existent which are:
    // ios7.tar in 7.1.2 folder, ramdisk.dmg and ramdisk.im4p in ramdisk folder.
    // p.s this is not vibe coded, wen eta printf in c without stdio.h :P
    

    int check1 = checkiOS7Tar();
    int check2 = checkRamdiskDMG();
    int check3 = checkRamdiskIM4P();

    if(check1 == true) {
        printf("[*] Found ios7.tar, continuing.\n");
    }
    if(check1 == false) {
        printf("[-] Could not find ios7.tar, downloading.\n");
        system("curl -L https://github.com/turlum25/sochidg-files/releases/download/FILES/ios7.tar.zip -o ./7.1.2/ios7.tar.zip");
        system("unzip -q ./7.1.2/ios7.tar.zip -d ./7.1.2/");
        system("rm ./7.1.2/ios7.tar.zip");
    }

    if(check2 == true) {
        printf("[*] Found ramdisk.dmg, continuing.\n");
    }
    if(check2 == false) {
        printf("[-] Could not find ramdisk.dmg, downloading.\n");
        system("curl -L https://github.com/turlum25/sochidg-files/releases/download/FILES/ramdisk.dmg -o ./ramdisk/ramdisk.dmg");
    }

    if(check3 == true) {
        printf("[*] Found ramdisk.im4p, continuing.\n");
    }
    if(check3 == false) {
        printf("[-] Could not find ramdisk.im4p, downloading.\n");
        system("curl -L https://github.com/turlum25/sochidg-files/releases/download/FILES/ramdisk.im4p -o ./ramdisk/ramdisk.im4p");
    }

    // added: v0.4~b5
    // probably april fools today but eh who cares
    // v20260401

}

int main(int argc, char *argv[]) {
    int opt;
    int downgrade_flag = 0;
    int ramdisk_flag = 0;
    int boot_flag = 0;

    // flags
    while ((opt = getopt(argc, argv, "drb")) != -1) {
        switch (opt) {
            case 'd':
                downgrade_flag = 1;
                break;
            case 'r':
                ramdisk_flag = 1;
                break;
            case 'b':
                boot_flag = 1;
                break;
            default:
                return 1;
        }
    }


    if (argc == 1 || (downgrade_flag == 0 && ramdisk_flag == 0 && boot_flag == 0)) {
        printf("sochiDG - Script by Turlum25\n");
        printf("Version 0.4-beta5\n");
        printf("----------------------------\n");
        printf("Usage: %s [-d] [-r] [-b]\n", argv[0]);
        printf("  -d      Downgrade iPhone to iOS 7.1.2 (11D257)\n");
        printf("  -r      Enter ramdisk mode\n");
        printf("  -b      Boot iOS 7.1.2 (11D257)");
        return(0); 
    }

    if (downgrade_flag) {
        printf("sochiDG - Script by Turlum25\n");
        fflush(stdout);
        printf("Version 0.4-beta5\n");
        fflush(stdout);
        printf("----------------------------\n");
        fflush(stdout);
        checkIfNecessaryFilesExist();
        collectIM4M();
        bootFiles();
        collectStuff();
        system("tools/img4tool -c ramdisk/ramdisk.img4 -p ramdisk/ramdisk.im4p -m IM4M");
        helperDFU();
        printf("[*] Starting downgrade to iOS 7.1.2 (11D257)...\n");
        fflush(stdout);
        setvbuf(stdout, NULL, _IONBF, 0);
        bootRamdisk();
        prepareNAND();
        helperDFU();
        bootRamdisk();
        sendFS();
        printf("[*] Done restoring to iOS 7.1.2 (hopefully)");

        return(0);
    }

    if (ramdisk_flag) {
        printf("sochiDG - Script by Turlum25\n");
        fflush(stdout);
        printf("Version 0.4-beta5\n");
        fflush(stdout);
        printf("----------------------------\n");
        fflush(stdout);
        printf("[*] Entering ramdisk mode...\n");
        fflush(stdout);
        helperDFU();
        bootRamdisk();

        return(0);
    }

    if (boot_flag) {

        printf("sochiDG - Script by Turlum25\n");
        fflush(stdout);
        printf("Version 0.4-beta5\n");
        fflush(stdout);
        printf("----------------------------\n");
        fflush(stdout);

        helperDFU();
        bootFiles();
        boot();

    }

    return 0;
    
}
