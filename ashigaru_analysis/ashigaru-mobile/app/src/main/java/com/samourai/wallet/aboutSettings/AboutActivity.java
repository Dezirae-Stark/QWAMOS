package com.samourai.wallet.aboutSettings;

import android.app.ActivityOptions;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import com.samourai.wallet.BuildConfig;
import com.samourai.wallet.R;
import com.samourai.wallet.SamouraiActivity;
import com.samourai.wallet.settings.SettingsActivity;
import com.samourai.wallet.util.URLUpdater.URLFileUtil;

public class AboutActivity extends SamouraiActivity {

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_about_settings);
        getWindow().setStatusBarColor(getResources().getColor(R.color.toolbar));
        getWindow().setNavigationBarColor(getResources().getColor(R.color.networking));

        setSupportActionBar(findViewById(R.id.toolbar));
        if(getSupportActionBar() != null){
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        }

        TextView actualVersionTxt = findViewById(R.id.actual_version);
        actualVersionTxt.setText("v" + BuildConfig.VERSION_NAME);

        TextView copyVersionTxt =  findViewById(R.id.copy_website_txt);
        copyVersionTxt.setOnClickListener(v -> {
            ClipboardManager clipboard = (ClipboardManager) AboutActivity.this.getSystemService(Context.CLIPBOARD_SERVICE);
            ClipData clip;
            String websiteStr = (String) URLFileUtil.getInstance(getApplicationContext()).getValue("ashigaru_website_url");
            clip = ClipData.newPlainText("Ashigaru Tor Website", websiteStr);
            clipboard.setPrimaryClip(clip);
            Toast.makeText(this, getString(R.string.copied_to_clipboard), Toast.LENGTH_SHORT).show();
        });

        LinearLayout appUrlsSection = findViewById(R.id.app_urls_section);
        appUrlsSection.setOnClickListener(v -> {
            Intent intent = new Intent(AboutActivity.this,  AppUrlsActivity.class);
            startActivity(intent);
        });

        LinearLayout downloadSection = findViewById(R.id.download_section);
        downloadSection.setOnClickListener(v -> {
            Intent intent = new Intent(AboutActivity.this,  CodeUrlsActivity.class);
            startActivity(intent);
        });

    }

    @Override
    public void onBackPressed() {
        final Intent intent = new Intent(AboutActivity.this, SettingsActivity.class);
        final ActivityOptions options = ActivityOptions.makeCustomAnimation(
                this, R.anim.slide_in_left, R.anim.slide_out_right);
        startActivity(intent, options.toBundle());
        finish();
        super.onBackPressed();
    }
}
