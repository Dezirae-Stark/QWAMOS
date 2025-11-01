package com.samourai.wallet.aboutSettings;

import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.os.Bundle;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import com.samourai.wallet.R;
import com.samourai.wallet.SamouraiActivity;
import com.samourai.wallet.util.URLUpdater.URLFileUtil;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.text.MessageFormat;

public class AppUrlsActivity extends SamouraiActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_app_urls_layout);
        setStatusBarColor(getResources().getColor(R.color.toolbar));
        setNavigationBarColor(getResources().getColor(R.color.networking));

        setSupportActionBar(findViewById(R.id.toolbar));
        if(getSupportActionBar() != null){
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        }

        ImageView fixUrlsIcon = findViewById(R.id.toolbar_icon);
        fixUrlsIcon.setOnClickListener(v -> {

            URLFixInfo dialog = new URLFixInfo(this::setUrls);

            dialog.show(getSupportFragmentManager(), dialog.getTag());
        });

        setUrls();


        TextView copyJSONTxt =  findViewById(R.id.copy_url_json);
        copyJSONTxt.setOnClickListener(v -> {
            JSONObject pgpUrlsJson = new JSONObject();
            JSONArray urlsArray = (JSONArray) URLFileUtil.getInstance(getApplicationContext()).getValue("active_and_offline_pgp_signed_message_urls");
            try {
                pgpUrlsJson.put("active_and_offline_pgp_signed_message_urls", urlsArray);
            } catch (JSONException e) {
                throw new RuntimeException(e);
            }

            ClipboardManager clipboard = (ClipboardManager) AppUrlsActivity.this.getSystemService(Context.CLIPBOARD_SERVICE);
            ClipData clip;
            clip = ClipData.newPlainText("PGP signed message URLs", pgpUrlsJson.toString());
            clipboard.setPrimaryClip(clip);
            Toast.makeText(this, getString(R.string.copied_to_clipboard), Toast.LENGTH_SHORT).show();
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
        setUrls();
    }

    private void setUrls() {
        TextView pgpVersion =  findViewById(R.id.pgp_version);
        pgpVersion.setText(formatVersionNumbers((String) URLFileUtil.getInstance(getApplicationContext()).getValue("pgp_signed_message_version")));


        TextView paynymURL =  findViewById(R.id.paynym_url);
        TextView paynymVersion =  findViewById(R.id.paynym_version);
        paynymURL.setText(getShortedUrl((String) URLFileUtil.getInstance(getApplicationContext()).getValue("paynym_url"), false));
        paynymVersion.setText(formatVersionNumbers((String) URLFileUtil.getInstance(getApplicationContext()).getValue("latest_paynym_url_version")));

        TextView sorobanURL =  findViewById(R.id.soroban_url);
        TextView sorobanVersion =  findViewById(R.id.soroban_version);
        sorobanURL.setText(getShortedUrl((String) URLFileUtil.getInstance(getApplicationContext()).getValue("soroban_url"), true));
        sorobanVersion.setText(formatVersionNumbers((String) URLFileUtil.getInstance(getApplicationContext()).getValue("latest_soroban_url_version")));

        TextView websiteURL =  findViewById(R.id.website_url);
        TextView websiteVersion =  findViewById(R.id.website_version);
        websiteURL.setText(getShortedUrl((String) URLFileUtil.getInstance(getApplicationContext()).getValue("ashigaru_website_url"), false));
        websiteVersion.setText(formatVersionNumbers((String) URLFileUtil.getInstance(getApplicationContext()).getValue("latest_ashigaru_website_url_version")));
    }

    private String getShortedUrl (String longURL, boolean isSoroban) {
        if (isSoroban)
            return longURL.substring(7, 15) + "..." + longURL.substring(longURL.length()-14);
        return longURL.substring(7, 15) + "..." + longURL.substring(longURL.length()-11);
    }

    private String formatVersionNumbers(String version) {
        MessageFormat mf = new MessageFormat("{0,number,0000}");
        Object[] objs = {Integer.valueOf(version)};
        return mf.format(objs);
    }
}
