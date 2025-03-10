# Build Instructions

**Thanks to `timeframe123` who did the heavy lifting and without him this would not exist**

Build Instructions for lmodroid based on Android 15 for the Xioami Mi Pad 6 (pipa).

Requirements:
* Linux build machine 
* Build machine with at least 32GB of RAM
* Build machine with at least 300GB of free disk space


Remarks:
* Have a look at [Lineage Wiki](https://wiki.lineageos.org/devices/gts4lv/build/) for general instructions

## Instructions

Remarks:
* Make certain to set the environment variable `${workspace}` or replace in the instructions
* Setup cache usage see: [Lineage Wiki](https://wiki.lineageos.org/devices/gts4lv/build/)

1. Setup folder structure
    ```sh
    mkdir -p ${workspace}/bin
    mkdir -p ${workspace}/lmodroid
    ```
2. Install repo
    ```sh
    curl https://storage.googleapis.com/git-repo-downloads/repo > ${workspace}/bin/repo
    chmod a+x ${workspace}/bin/repo
    ```
3. Add repo to `PATH` variable so that it will be found later on. Append to file `~/.bashrc`:
    ```sh
    if [ -d "$HOME/bin" ] ; then
        PATH="${workspace}/bin:$PATH"
    fi
    ```
4. Reopen the terminal or source `~/.bashrc`
5. Initialize repositories
    ```sh
    repo init -u https://git.libremobileos.com/LMODroid/manifest.git -b fifteen --git-lfs
    ```
6. Sync repositories
    ```sh
    repo sync -c -j$(nproc --all) --force-sync --no-clone-bundle --no-tags
    ```
7. Copy the device
    ```sh
    git clone https://github.com/ai94iq/android_device_xiaomi_pipa -b lmov device/xiaomi/pipa
    ```
8. Source environment for this shell and downloads the dependencies for the device
    ```sh
    . build/envsetup.sh
    ```
9. Configure environment. See [build-numbers](https://source.android.com/docs/setup/reference/build-numbers) and [beta wiki](https://betawiki.net/wiki/Android_15) for the right build number. `ap4a` should be the latest lmodroid release. Please see [build-numbers](https://source.android.com/docs/setup/reference/build-numbers) for the right one.

    See `${workspace}/build/release/aconfig` for available releases.
    ```sh
    lunch lmodroid_pipa-ap4a-userdebug
    ```
10. Compile 
    ```sh
    brunch pipa
    ```


## Apply Android Security patches

1. Execute step `6. Sync repositories` to sync the repos
2. Execute step `7. Copy the device`to update the device repository
2. Execute step `8. Source environment for this shell` to setup `bash` environment
3. Select right build number as described in step `9. Configure environment`
4. Execute step `10. Compile` to build the project again

# Installation Guide

NOTE:
* Make sure to use **HyperOS Global** or **China** based on Android 14 Firmware, don't try to run this ROM with Miui Firmware

## Guid
* Install fastboot and adb on your system
* Download the rom package along with boot, dtbo and vendor_boot (links mentioned in post)
* Put downloaded files in a folder(your platform tools folder preferred)
* Reboot to bootloader(hold power + volume down button)
* In your PC, open terminal where you copied the above files and run the following commands:
    Flash the boot image
    ```sh
    fastboot flash boot boot.img
    ```

    Flash the (device tree blob overlay)[https://source.android.com/docs/core/architecture/dto]
    ```sh
    fastboot flash dtbo dtbo.img
    ```

    Flash the (vendor boot partitions)[https://source.android.com/docs/core/architecture/partitions/vendor-boot-partitions]
    ```sh
    fastboot flash vendor_boot vendor_boot.img
    ```

    Reboot into recovery
    ```sh
        fastboot reboot recovery
    ```

* Format data via recovery (optional if flashing on the same rom)
* Select reboot to recovery (advanced -> reboot to recovery)
* Select apply update in recovery
* In your PC terminal, run 
    ```sh
    adb sideload <rom.zip>
    ```
    (replace `<rom.zip>` with the downloaded ROM package `name.zip`)
* If you are flashing a vanilla build and want to **flash gapps**, select reboot to recovery, select apply update in recovery. Sideload gapps via adb
    ```sh
    adb side
    ```
    Sideload gapps by selecting apply update
    Remarks: 
    * Installation ends at 47% displayed on your pc terminal
    * If you downloaded an `.img` file, simple rename it to `.zip`
    * The build might be unsigned, you need to confirm to flash gapps
    
    *Skip this step if you are already flashing a gapps build*
* Sidelaod Magisk via adb as described in last step
* Reboot to system

## For updating from existing LMO build
* Select reboot to recovery (advanced -> reboot to recovery)
* Select apply update in recovery
* In your pc terminal
    ```sh
    adb sideload rom.zip
    ```
    (replace `<rom.zip>` with the downloaded ROM package `name.zip`)
* To flash gapps, see in section above. 
* To flash Magisk, see in section above.

## Useful Links
* Google Apps for A14: [here](https://github.com/MindTheGapps/14.0.0-arm64/releases)
* Google Apps for A15: [here](https://github.com/MindTheGapps/15.0.0-arm64/releases)
* Magisk: [here](https://github.com/topjohnwu/magisk/releases)
* We recommend MinMicroG installed before the first boot, **either Minimal or MinimalPhonesky variant**
microG Installer: [here](https://github.com/FriendlyNeighborhoodShane/MinMicroG-abuse-CI/releases)

FAQ: 
* Q: Will I loose data when upgrading to new release? 
    A: You never really know, so do a backup first. Usually the data storage should persist while upgrade
* Q: Do I need to reinstall gapps when upgrading? 
    A: If you upgrade from one to an other android version you need to reflash the right version of gapps.
* Q: My device is stuck in fastboot mode (green start written on the top of the screen) and I am unable to boot into recovery nor boot. What can I do? 
    A: Download the global or china HyperOS version for fastboot and flash the device and then try again. 
