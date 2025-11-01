package com.samourai.wallet.aboutSettings;

import android.content.ClipData;
import android.content.ClipboardManager;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.TextView;

import com.samourai.wallet.R;
import com.samourai.wallet.SamouraiActivity;
import com.samourai.wallet.util.URLUpdater.URLFileUtil;

import org.json.JSONArray;
import org.json.JSONException;

import java.text.MessageFormat;
import java.util.Arrays;
import java.util.List;

public class CodeUrlsActivity extends SamouraiActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_code_urls_layout);
        getWindow().setStatusBarColor(getResources().getColor(R.color.toolbar));
        getWindow().setNavigationBarColor(getResources().getColor(R.color.networking));

        setSupportActionBar(findViewById(R.id.toolbar));
        if(getSupportActionBar() != null){
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        }
        List<String> stringList = Arrays.asList("URL 1", "URL 2", "URL 3");

        JSONArray zipCodeURLs = (JSONArray) URLFileUtil.getInstance(getApplicationContext()).getValue("active_and_offline_latest_source_code_zip_urls");

        LinearLayout parentLayout = findViewById(R.id.parentLayoutCodeUrls);
        LinearLayout scrollLayout = findViewById(R.id.scrollViewParent);

        for (int i = 0; i < zipCodeURLs.length(); i++) {
            try {
                View divider = new View(this);
                divider.setLayoutParams(new LinearLayout.LayoutParams(
                        LinearLayout.LayoutParams.MATCH_PARENT,
                        2
                ));
                divider.setBackgroundColor(getResources().getColor(R.color.separator));
                scrollLayout.addView(divider);

                String url = zipCodeURLs.getString(i);

                View itemView = LayoutInflater.from(this).inflate(R.layout.source_code_download_element, scrollLayout, false);

                TextView textViewTitle = itemView.findViewById(R.id.textViewTitle);
                textViewTitle.setText("Source code download URL "+formatVersionNumbers(i+1));

                TextView copyUrlText = itemView.findViewById(R.id.copy_url);
                copyUrlText.setText("COPY");
                copyUrlText.setTextColor(getResources().getColor(R.color.blue_settings));
                copyUrlText.setOnClickListener(view -> copyToClipboard(url));

                scrollLayout.addView(itemView);
            } catch (JSONException e) {
                throw new RuntimeException(e);
            }
        }
    }

    private String formatVersionNumbers(int number) {
        MessageFormat mf = new MessageFormat("{0,number,0000}");
        Object[] objs = {number};
        return mf.format(objs);
    }

    private void copyToClipboard(String text) {
        ClipboardManager clipboard = (ClipboardManager) getSystemService(CLIPBOARD_SERVICE);
        ClipData clip = ClipData.newPlainText("Copied Text", text);
        clipboard.setPrimaryClip(clip);
    }
}
