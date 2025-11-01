## Verifying signatures of the officially released Ashigaru mobile APK

### Ashigaru release builds

Release builds (.APKs) are signed using Ashigaru's Android signing certificate (Java Keystore) and are available for download from [Releases](http://ashicodepbnpvslzsl2bz7l2pwrjvajgumgac423pp3y2deprbnzz7id.onion/Ashigaru/Ashigaru-Mobile/releases).

In order to verify the oficially released Ashigaru mobile APK, you will need to first [build your own unsigned APK](ReproducibleBuilds.md) then compare it agaist the officially released APK file.

### How to verify the offically released Ashigaru mobile APK

1. Download the latest oficially released Ashigaru mobile APK file from [Releases](http://ashicodepbnpvslzsl2bz7l2pwrjvajgumgac423pp3y2deprbnzz7id.onion/Ashigaru/Ashigaru-Mobile/releases).

2. Verify the integrity of the downloaded file by verifying its sha256 hash against the accompanying PGP signed message. You may follow [these instructions](https://ashigaru.rs/docs/software-verification/).

3. [Build your own unsigned production APK](ReproducibleBuilds.md).

4. Place the oficially released Ashigaru APK file (signed), and your unsigned production APK file (unsigned) into the same folder.

5. Navigate to the folder where both signed and unsigned APKs are located.

6. Unzip the signed APK into it's own folder by running the following command:
`unzip ./ashigaru_mobile_vX.X.X.apk -d signed_APK_folder`

Note: you will need to modify `vX.X.X` in this command to correspond with .apk file version you are decoding.

7. Unzip your unsigned APK into it's own folder by running the following command:
`unzip ./app-production-release-unsigned.apk -d unsigned_APK_folder`

8. Compare and display the differences in files between the two decoded folders by running the following command:
`diff -qr signed_APK_folder unsigned_APK_folder`

9. The resulting output will look something like this:

  Only in signed_APK_folder/META-INF: MANIFEST.MF  
  Only in signed_APK_folder/META-INF: ASHIGARU.RSA  
  Only in signed_APK_folder/META-INF: ASHIGARU.SF

10. Remove the listed files from the signed APK:
`zip -d ashigaru_mobile_vX.X.X.apk "META-INF/MANIFEST.MF" "META-INF/ASHIGARU.SF" "META-INF/ASHIGARU.RSA"`

Note: you will need to modify `vX.X.X` in this command to correspond with .apk file version you are removing the listed files from.

11. Obtain the SHA-256 hash of the signed APK by running the following command:
`shasum -a 256 ./ashigaru_mobile_vX.X.X.apk`

Note: you will need to modify `vX.X.X` in this command to correspond with .apk file version you are hashing.

12. Obtain the SHA-256 hash of your unsigned production APK by running the following command:
`shasum -a 256 ./app-production-release-unsigned.apk`

### Check reproducibility

If the two hashes are an exact match, you have confirmed the officially released Ashigaru mobile APK file is a reproducible build.
