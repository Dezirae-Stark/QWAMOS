package com.samourai.wallet.util.URLUpdater;

import android.content.Context;

import com.samourai.wallet.dexConfig.DexConfigProvider;
import com.samourai.wallet.paynym.api.PayNymApiService;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.File;
import java.util.List;


public class URLFileUtil {
    private static Context context;
    private static URLFileUtil instance = null;

    private static final String FILE_NAME = "urlsTable.json";

    // <editor-fold desc="Default URL values when initializing the JSON file:">
    private static final String PAYNYM_URL = "http://paynym25chftmsywv4v2r67agbrr62lcxagsf4tymbzpeeucucy2ivad.onion";
    private static final String PAYNYM_URL_VERSION = "0001";

    private static final String SOROBAN_URL = "http://ashi5c6obifqi2thzkxqrqlkewywzucgglusc3n7qusnei75nrkwwyad.onion:4242";
    private static final String SOROBAN_URL_VERSION = "0001";

    private static final String ASHIGARU_URL = "http://ashigaruprvm4u263aoj6wxnipc4jrhb2avjll4nnk255jkdmj2obqqd.onion";
    private static final String ASHIGARU_URL_VERSION = "0001";

    private static final String PGP_VERSION = "0002";

    private static final List<String> PGP_MESSAGE_URLs = List.of(
            "http://ashicodepbnpvslzsl2bz7l2pwrjvajgumgac423pp3y2deprbnzz7id.onion/Ashigaru/Ashigaru-Mobile/raw/branch/main/accompanying-release-files/ashigaru_mobile_latest.txt",
            "http://lbpxfhbnfyhxmy3jl6a4q7dzpeobx7cvkghz2vvwygevq3k4ilo2v5ad.onion/Ashigaru/Ashigaru-Mobile/raw/branch/main/accompanying-release-files/ashigaru_mobile_latest.txt",
            "http://ashi27h42d4efvidvu2rca43mmztayzfkrdyl7bdcz6qcybpuzbxetqd.onion/ashigaru_mobile_latest.txt"
    );

    private static final List<String> ZIP_CODE_URLs = List.of(
            "http://ashicodepbnpvslzsl2bz7l2pwrjvajgumgac423pp3y2deprbnzz7id.onion/Ashigaru/Ashigaru-Mobile/archive/v1.1.0.zip",
            "http://lbpxfhbnfyhxmy3jl6a4q7dzpeobx7cvkghz2vvwygevq3k4ilo2v5ad.onion/Ashigaru/Ashigaru-Mobile/archive/v1.1.0.zip",
            "http://ashi27h42d4efvidvu2rca43mmztayzfkrdyl7bdcz6qcybpuzbxetqd.onion/v1.1.0.zip"
    );

    // </editor-fold>

    private URLFileUtil() { ; }

    public static URLFileUtil getInstance(Context ctx) {

        context = ctx;

        if(instance == null) {
            instance = new URLFileUtil();
        }

        return instance;
    }

    // File Writer

    public void writeToFile(JSONObject jsonObject) {
        try (FileOutputStream fos = context.openFileOutput(FILE_NAME, Context.MODE_PRIVATE)) {
            fos.write(jsonObject.toString().getBytes());
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void modifyValue(String key, Object value) {
        JSONObject jsonObject = readFromFile();

        if (jsonObject != null) {
            try {
                jsonObject.put(key, value);
                writeToFile(jsonObject);
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
    }

    public boolean deleteFile() {
        File file = new File(context.getFilesDir(), FILE_NAME);
        return file.delete();
    }

    //File Reader

    public JSONObject readFromFile() {
        File file = new File(context.getFilesDir(), FILE_NAME);

        if (!file.exists()) {
            JSONObject defaultURLS = new JSONObject();
            try {
                defaultURLS.put("pgp_signed_message_version", PGP_VERSION);
                JSONArray pgpMessageURLArray = new JSONArray(PGP_MESSAGE_URLs);
                defaultURLS.put("active_and_offline_pgp_signed_message_urls", pgpMessageURLArray);
                JSONArray zipCodeURLArray = new JSONArray(ZIP_CODE_URLs);
                defaultURLS.put("active_and_offline_latest_source_code_zip_urls", zipCodeURLArray);

                defaultURLS.put("paynym_url", PAYNYM_URL);
                defaultURLS.put("latest_paynym_url_version", PAYNYM_URL_VERSION);

                defaultURLS.put("soroban_url", SOROBAN_URL);
                defaultURLS.put("latest_soroban_url_version", SOROBAN_URL_VERSION);

                defaultURLS.put("ashigaru_website_url", ASHIGARU_URL);
                defaultURLS.put("latest_ashigaru_website_url_version", ASHIGARU_URL_VERSION);

                writeToFile(defaultURLS);
            } catch (JSONException e) {
                e.printStackTrace();
            }
            return defaultURLS;
        }

        // Read from the file if it exists
        StringBuilder stringBuilder = new StringBuilder();
        try (FileInputStream fis = context.openFileInput(FILE_NAME)) {
            int character;
            while ((character = fis.read()) != -1) {
                stringBuilder.append((char) character);
            }
            return new JSONObject(stringBuilder.toString());
        } catch (IOException | JSONException e) {
            e.printStackTrace();
            return null;
        }
    }

    public Object getValue(String key) {
        JSONObject jsonObject = readFromFile();

        if (jsonObject != null) {
            try {
                if (jsonObject.has(key)) {
                    return jsonObject.get(key);
                } else {
                    System.out.println("Key not found in the JSON file.");
                }
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }

        return null;
    }

    public void setPaynymAndSorobanUrls() {
        String paynymUrl = (String) getValue("paynym_url");
        if (paynymUrl.lastIndexOf('/') != paynymUrl.length()-1)
            paynymUrl += "/";
        PayNymApiService.Companion.setPAYNYM_API(paynymUrl);

        String sorobanURL = (String) getValue("soroban_url");
        if (!sorobanURL.contains(":4242"))
            sorobanURL += ":4242";
        DexConfigProvider.getInstance().getSamouraiConfig().setSorobanServerTestnetOnion(sorobanURL);
    }

    public void checkJsonAndSeedVersions() {
        int jsonVersion = Integer.parseInt((String) getValue("pgp_signed_message_version"));
        int seedVersion = Integer.parseInt(PGP_VERSION);
        if (seedVersion > jsonVersion) {
            deleteFile();
            readFromFile();
        }
    }
}
