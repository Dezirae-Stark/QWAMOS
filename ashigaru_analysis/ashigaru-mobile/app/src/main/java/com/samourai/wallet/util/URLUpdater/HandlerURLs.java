package com.samourai.wallet.util.URLUpdater;

import static org.apache.commons.lang3.StringUtils.defaultString;
import static org.apache.commons.lang3.StringUtils.isNotBlank;
import static org.apache.commons.lang3.StringUtils.strip;
import static org.apache.commons.lang3.StringUtils.stripStart;
import static org.apache.commons.lang3.StringUtils.substringBetween;

import android.content.Context;
import android.util.Log;

import com.samourai.wallet.BuildConfig;
import com.samourai.wallet.SamouraiWallet;
import com.samourai.wallet.util.Util;
import com.samourai.wallet.util.network.WebUtil;
import com.samourai.wallet.util.tech.VerifyPGPSignedClearMessageUtil;
import com.sparrowwallet.hummingbird.UR;

import org.apache.commons.lang3.StringUtils;
import org.json.JSONArray;
import org.json.JSONObject;

import java.net.URL;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class HandlerURLs {
    private static final String TAG = "HandlerURLs.java";
    private static Context context;
    private static HandlerURLs instance = null;
    private String highestVersionPgpURLResponse = null;

    public static final String ASHIGARU_PUB_KEY2 = "-----BEGIN PGP PUBLIC KEY BLOCK-----\n" +
            "Comment: https://keybase.io/download\n" +
            "Version: Keybase Go 6.3.1 (linux)\n" +
            "\n" +
            "xsFNBGZdzx4BEADmL1E5gLoHtAd+N9Cw22VbnD47em9Hn946aDeB90pbrx02m8TW\n" +
            "Acji5VOOmN1CNg2EomG0aGk6eox1TZkisYsu5rTCmpQX36CQ6/LvUFh8MTYF38kW\n" +
            "wukNxE93wrXz/emk2yW/jeos6XlQ6/iJmom4bRCHDLxstFn14ICitr2zKysAOHkC\n" +
            "iutQacwsGSLImi/7YEzQrIAi4WeTGrScyEFaJ0BxOQ4lzZeQw3Me+ESufZDOfB6+\n" +
            "u8wsZzqVP5drp/AStbhGPhkYXbHJGikgVDVxxm/C9Yy/jhcQGUPSEFqXREeFncTM\n" +
            "w7q3M5YG7Rl7m2VPEElNkZRYBI7fa5G5E6Iy01Y4/KxyutRwOf/DZHUaK/VQQQne\n" +
            "HJzH58PvISPvswZzJWKN3mHiNGrbWGyBcvJOXlfbekLbRML8I28usKnSDWbHdkWc\n" +
            "9Ls8P+H62TcY7npdGRvZAGIcM11BqGp66fndc911HDbX3/0IPp1DJEnpLn46gQqs\n" +
            "3GJ6rMTBbt++krIFam1/kIr3Atp5EBqoSgAvxY5Xk+OUsYaa/K3VBQONpI2f7qJZ\n" +
            "HN9GpqszwF2eeu1vKB/CRxISRQLjklVBssiZ2Zez7PZ470Ses1V7jK2tWGqzf5sG\n" +
            "C0Tpp53WqFHtn4u/YuRtPQJtO0FHsc82mZbynoCO5YhNSh1mivPQoxPj0QARAQAB\n" +
            "zQxBc2hpZ2FydSBEZXbCwXEEEwEKACUFAmZdzx4JEKE4BrH6KmdrAhsDBQsJCAcD\n" +
            "BRUKCQgLBRYCAwEAAAD0txAAzpXmxtqVRLxEEdUBx1kxp1kE8kDJAhBraX5VXGOv\n" +
            "HuThhcr3j5Esj4IOGcsiV5S9nRNPu+hjjTX8AoOVLQcfU0jymrNRBXLQcd7L03Jj\n" +
            "0vG3sb7HOVbnQdGAwCrabb941BB3smitsYqI/Xz12CjavsONSp6wImt+jVHsAYC6\n" +
            "y1xew4cBkPL9VmzKabTGNTV+wPe7xHSdptdAvK98EWFZ+Yq3ut/rt4mnqr35OQWW\n" +
            "qDcAiAqKndqJXVZklDOvdQ654VPsBlJG4V+K4evZ7ECUc4gRVWWe5Ijl9z0UGopv\n" +
            "FTkeTn9GnyHRZgLYooHkqd3oith/1fweldatvRGIXpdA1W02Tn7I0imjvzgBNDVq\n" +
            "MS3rCp8kFFDtcshpASbtXChiloMFaw1+VDymT7sF81S5obbsJYRRkt2Qo+xM3B2n\n" +
            "t0gZDMuLAJ2Er9VXxpcyrjl8U+Us8atbx7x4UyPaZJe4zj8nZYZly/uVZQ8JL/Nc\n" +
            "zMg8ES9c8LV9ZcSlsIgX8VT6omxlSzWZNtfswBrXMUruxJgc7WKn1I6JMFbeRUG5\n" +
            "fLtjLyn4/KufW+Liiq4RKcRQb/rxUaT+e7tzY90y4MqTzLD7kbVhCRx5RVBY5bZD\n" +
            "2pFtch6CPVnZx/EHjR3Yd2zZgbDCVSIEEA6y2QS3aMhHXu1orgjVayOWVTINZE0y\n" +
            "K3POwU0EZl3PHgEQAOOzDEJRk8paHDXqNGYiFiQZCxX3CIOK3+DR+zsS8oq4AtXT\n" +
            "R7WUBDRACwUkDpNhybmkpEWH6B3zdsZPaGJ80ApTImWXc6KMJagcAJPVrwSGttOb\n" +
            "zQHCsbsVfS3xXQ4G3uxncLd7Ck+fesR0GVsfJ4HsTOZaKmbuUYFifa4PevwEeYKR\n" +
            "AcPdfcx7dTRd18XBaBPLNRzbUfck1rCIiO9QXR6oVbUYBlOKPVDYMjgrav4hd2s2\n" +
            "BxWNLXxkE3MsyTSQ/+B8ty9Sz0C0aDrRRs5lA0/07hF9C3Wnv8op5XsUkO5eT7RD\n" +
            "1PeWk+WiQURcQhAJsmrxjG7rXWQWaU8QR095Ldd1VRZXzPoLx8+iTNWqNRj/VuWw\n" +
            "vhThYuWIP+RJTAV4kx/Mi8Os1dkV0KIKYQYsu+i0d7UBqL4LzCoY332Z/vJiaoVT\n" +
            "+Aa4T7+/hgoG0VYF5ddSyDZv+CwUOzLO7fh/Tg4Jv1CpHKgwq4NELf6G7SVjrnKH\n" +
            "LNd/JULHDMTpl6/RFn0rrwb/phmfQz0cbHU3ZXUJU5m9aqvjhdjV31+UP+Re0EBB\n" +
            "JKDTHqzggTfPtpu8+nIRrfxm8pyHHxmt4pa4wUYujLnySLyPpMYLuAi3U7FUSHyo\n" +
            "F3eZB1SeQ+9rQuZSRlvjXJTdNBDDUnJR9CiKC6K78jHKXHd5v7LPWh86g7SpABEB\n" +
            "AAHCwXYEGAEKACAWIQREX4B5lvcFhrcVx7ihOAax+ipnawUCZl3PHgIbDAAKCRCh\n" +
            "OAax+ipna9/OD/0bHstAeNKkUezn8QbI8ZuRXgkrcPo0EQ3dUNO6ZbyhqFUiM8Vt\n" +
            "1syF2vX72+BNewwFsOAWHrDTRSZ09dO+M1c58I+Lr1AVP14jfYQ0mmPGY8ND9sk5\n" +
            "WDheZjCbO6OJ55yQzC/ZTEra1Pxi3yWqcneyG3yX4z4ih3BazYIH3MR3EaSLVLjd\n" +
            "eo3TqviWsBE7upKI1ipKf58l/0JoYWWWyVSVbEk/kjHlod19NjHzBvxzAX7I17Co\n" +
            "+TMduAb2wrwVOqdDzOTS/X/KOAs7Q643rTgz9YqC2V/k9FLDKQIgqUvsADTnZtwF\n" +
            "1fzL3U/xcJdh46Yy3lmyi2e9Rt6oVSGTaRiSWSlPYGAgiLYiHGTpLhpAmupNGdaj\n" +
            "tJ0PZPoFehQ7zW75tOml1/8AIwUgzJsQHSKe3UCG7uSpXWT0sE4trfF71O0y0zoH\n" +
            "hJZZq0X9O6iC3qLOGi8l4ZmhTJhBd3YlPqtugHuQWSiBABR2EoCxrhgbu0W5+Dp/\n" +
            "db/0DMdwPhIwWwi1j6E3YKqQiz3q+mjUflUFiskJUeaYQe+YaeXJ43bZ4WPXZcfy\n" +
            "5WEKWZypGiuhirhfSrdmt4EPWQ3fR2j7/RafEpMsF9cWDvAoAvQQK3VM/EoCcj12\n" +
            "qbgNKNuFv/4hw+BF2AUIM3SojZ6yqaNw2NByy3zKd5Wx1U4Pd6OY4Jcrxg==\n" +
            "=iJA5\n" +
            "-----END PGP PUBLIC KEY BLOCK-----";

    public static HandlerURLs getInstance(Context ctx) {

        context = ctx;

        if(instance == null) {
            instance = new HandlerURLs();
        }

        return instance;
    }

    public void setPgpMessage(String pgpMessage) {
        this.highestVersionPgpURLResponse = pgpMessage;
    }

    public int getHighestPgpVersionFromUrls() {
        JSONArray urls = (JSONArray) URLFileUtil.getInstance(context).getValue("active_and_offline_pgp_signed_message_urls");
        int highestVersion = 0;

        for (int i = 0; i < urls.length(); i++) {
            try {
                String url = urls.getString(i);
                String signedPgpMessage = WebUtil.getInstance(null).getURL(url);

                if (!VerifyPGPSignedClearMessageUtil.verifySignedMessage(
                        defaultString(signedPgpMessage),
                        ASHIGARU_PUB_KEY2))
                    continue;

                String version = substringBetween(signedPgpMessage, "pgp_signed_message_version=", "\n");

                if (highestVersion < Integer.parseInt(StringUtils.trim(version))) {
                    highestVersion = Integer.parseInt(StringUtils.trim(version));
                    highestVersionPgpURLResponse = signedPgpMessage;
                }

            } catch (Exception e) {
                Log.e(TAG, e.getMessage(), e);
            }
        }
        return highestVersion;
    }

    public void updatePgpAndCodeURLs() {
        JSONArray pgpURLs = new JSONArray();
        List<String> pgpURLExtensions = getElementsOfList("active_and_offline_pgp_signed_message_urls=");
        for (String pgpExt : pgpURLExtensions) {
            String newUrl = substringBetween(highestVersionPgpURLResponse, "pgp_signed_message_url_" + pgpExt + "=" , "\n");
            pgpURLs.put(newUrl);
        }
        URLFileUtil.getInstance(context).modifyValue("active_and_offline_pgp_signed_message_urls", pgpURLs);


        JSONArray codeURLs = new JSONArray();
        List<String> codeURLsExtensions = getElementsOfList("active_and_offline_latest_source_code_zip_urls=");
        for (String codeExt : codeURLsExtensions) {
            String newUrl = substringBetween(highestVersionPgpURLResponse, "latest_source_code_zip_download_url_" + codeExt + "=" , "\n");
            codeURLs.put(newUrl);
        }
        URLFileUtil.getInstance(context).modifyValue("active_and_offline_latest_source_code_zip_urls", codeURLs);
    }

    // Check if the app version is the same as the lastest
    // If it's lower, go through all the provided links to get the release notes
    // If releaseNotes are fetched and hash matches, then return true and set the release notes
    public boolean isAppUpdateAvailable() {
        final String latestVersion = strip(stripStart(substringBetween(highestVersionPgpURLResponse, "latest_ashigaru_mobile_version=", "\n"), "v"));
        if (latestVersion.equals(stripStart(BuildConfig.VERSION_NAME, "v"))) {
            return false;
        }

        String releaseNotes = null;

        List<String> notesExtensions = getElementsOfList("active_and_offline_ashigaru_mobile_release_notes_urls=");

        for (String notesExt : notesExtensions) {
            String rlsNotesUrl = substringBetween(highestVersionPgpURLResponse, "ashigaru_mobile_release_notes_download_url_" + notesExt + "=" , "\n");
            try {
                String tentativeNotes = WebUtil.getInstance(null).getURL(rlsNotesUrl);

                final String releaseNotesSha256 = Util.sha256Hex(defaultString(tentativeNotes)).trim();
                final String releaseNoteSha256ToVerify = substringBetween(highestVersionPgpURLResponse, "ashigaru_mobile_release_notes.txt_sha256hash=", "\n").trim();
                if (StringUtils.equals(releaseNotesSha256, releaseNoteSha256ToVerify)) {
                    releaseNotes = tentativeNotes;
                    JSONObject releaseNotesJSON;
                    try {
                        releaseNotesJSON =  new JSONObject(releaseNotes);
                    } catch (final Exception e) {
                        Log.e(TAG, e.getMessage(), e);
                        releaseNotesJSON = null;
                    }
                    if (releaseNotesJSON == null) {
                        Log.w(TAG, "releaseNotesJSON is null");
                        continue;
                    }
                    SamouraiWallet.getInstance().releaseNotes = releaseNotesJSON;
                    break;
                }
            } catch (Exception e) {
                Log.e(TAG, e.getMessage(), e);
            }
        }

        return releaseNotes != null;
    }

    public void updatePaynymURL() {
        int latestVersion = Integer.parseInt(substringBetween(highestVersionPgpURLResponse, "latest_paynym_url_version=","\n").trim());
        int currentVersion = Integer.parseInt((String) URLFileUtil.getInstance(context).getValue("latest_paynym_url_version"));

        if (currentVersion >= latestVersion) {
            return;
        }

        String newPaynymURL = substringBetween(highestVersionPgpURLResponse, "paynym_url=","\n");
        if (isNotBlank(newPaynymURL)) {
            URLFileUtil.getInstance(context).modifyValue("paynym_url", newPaynymURL);
            URLFileUtil.getInstance(context).modifyValue("latest_paynym_url_version", Integer.toString(latestVersion));
        }
    }

    public void updateSorobanURL() {
        int latestVersion = Integer.parseInt(substringBetween(highestVersionPgpURLResponse, "latest_soroban_url_version=","\n").trim());
        int currentVersion = Integer.parseInt((String) URLFileUtil.getInstance(context).getValue("latest_soroban_url_version"));

        if (currentVersion >= latestVersion) {
            return;
        }

        String newSorobanURL = substringBetween(highestVersionPgpURLResponse, "soroban_url=","\n");
        if (isNotBlank(newSorobanURL)) {
            URLFileUtil.getInstance(context).modifyValue("soroban_url", newSorobanURL);
            URLFileUtil.getInstance(context).modifyValue("latest_soroban_url_version", Integer.toString(latestVersion));
        }
    }

    public void updateAshigaruSiteURL() {
        int latestVersion = Integer.parseInt(substringBetween(highestVersionPgpURLResponse, "latest_ashigaru_website_url_version=","\n").trim());
        int currentVersion = Integer.parseInt((String) URLFileUtil.getInstance(context).getValue("latest_ashigaru_website_url_version"));

        if (currentVersion >= latestVersion) {
            return;
        }

        String newAshigaruSiteURL = substringBetween(highestVersionPgpURLResponse, "ashigaru_website_url=","\n");
        if (isNotBlank(newAshigaruSiteURL)) {
            URLFileUtil.getInstance(context).modifyValue("ashigaru_website_url", newAshigaruSiteURL);
            URLFileUtil.getInstance(context).modifyValue("latest_ashigaru_website_url_version", Integer.toString(latestVersion));
        }
    }

    public void updatePgpSignedMessageVersion(String latestPgpVersion) {
        URLFileUtil.getInstance(context).modifyValue("pgp_signed_message_version", latestPgpVersion);
    }

    private List<String> getElementsOfList(String urlList) {
        String allURLs = substringBetween(highestVersionPgpURLResponse, urlList, "\n");
        return Arrays.asList(allURLs.split(","));
    }
}
