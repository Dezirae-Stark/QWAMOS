# Reproducible Builds

The purpose of this guide is to aid you in confirming the [official release of Ashigaru mobile APK](http://ashicodepbnpvslzsl2bz7l2pwrjvajgumgac423pp3y2deprbnzz7id.onion/Ashigaru/Ashigaru-Mobile/releases) file can be independently reproduced, therefore confirming the Ashigaru Open Source Project has released an APK file built **only** using source code from the [Ashigaru-Mobile repository](http://ashicodepbnpvslzsl2bz7l2pwrjvajgumgac423pp3y2deprbnzz7id.onion/Ashigaru/Ashigaru-Mobile).

The general goal is for you to independently:
- Build your own unsigned production APK file using the [Ashigaru-Mobile source code](http://ashicodepbnpvslzsl2bz7l2pwrjvajgumgac423pp3y2deprbnzz7id.onion/Ashigaru/Ashigaru-Mobile).
- Obtain the SHA-256 hash of the APK, and confirm it match with the [Unsigned APK Hashes](Unsigned-APK-Hashes.md).

## Building reproducible builds

### Version information

These instructions are valid for officially released Ashigaru mobile APKs from version 1.0.0

### Environment

- Intel x86_64 and Mac M1 architecture. Using other architecture may yield different results.
- Versions: OpenJDK 18.0.1 and Gradle 8.9.
- No pre-configuration required. Environment is automatically set by build.gradle file.

### Building your own unsigned production APK

Below are two methods to build your own unsigned production APK:
- Method 1 - Android Studio
- Method 2 - Command line

#### Method 1: Android Studio:

1. Clone / download the code from the [Ashigaru-Mobile}(http://ashicodepbnpvslzsl2bz7l2pwrjvajgumgac423pp3y2deprbnzz7id.onion/Ashigaru/Ashigaru-Mobile) master branch.
2. Import **Ashigaru-Mobile** project into Android Studio.
3. In the **Main Menu**, select **View** > **Tool windows** > **Gradle** (This should bring up the Gradle Tool window on the right hand side of Android Studio.)
4. Select the icon labels **Execute Gradle Task** in the Gradle Tool window. (This should pop up a **Run Anything** window)
5. In the **Run Anything** window, type `gradlew clean assembleRelease`, then press ENTER.
6. Once build is completed, your unsigned production APK file could be located at `ashigaru-mobile/app/build/outputs/apk/production/release/app-production-release-unsigned.apk`

#### Method 2 - Command line:

1. Clone / download the code from the [Ashigaru-Mobile}(http://ashicodepbnpvslzsl2bz7l2pwrjvajgumgac423pp3y2deprbnzz7id.onion/Ashigaru/Ashigaru-Mobile) master branch.
2. Navigate to `ashigaru-mobile` project folder
3. Run the following command: `./gradlew clean assembleRelease` (For Windows `.\gradlew.bat clean assembleRelease`)
4. Once build is completed, your unsigned production APK file could be located at `ashigaru-mobile/app/build/outputs/apk/production/release/app-production-release-unsigned.apk`


### Obtaining SHA-256 hash of your unsigned production APK file

Below are two methods to obtain the hash of your unsigned production APK file, depending on your operating system:
- Method 1 - Linux (bash)
- Method 2 - Windows (PowerShell)

#### Method 1 - Linux (bash)
1. Navigate to: `ashigaru-mobile/app/build/outputs/apk/production/release/`
2. Run the following command: `shasum -a 256 ./app-production-release-unsigned.apk` 
3. The output shown is the SHA-256 hash of your unsigned production APK file, compare this against the hash listed here: [Unsigned APK Hashes](Unsigned-APK-Hashes.md)

#### Method 2 - Windows (PowerShell)
1. Navigate to: `ashigaru-mobile\app\build\outputs\apk\production\release\`
2. Run the following command: `Get-FileHash -Algorithm SHA256 ./app-production-release-unsigned.apk` 
3. The output shown is the SHA-256 hash of your unsigned production APK file, compare this against the hash listed here: [Unsigned APK Hashes](Unsigned-APK-Hashes.md)