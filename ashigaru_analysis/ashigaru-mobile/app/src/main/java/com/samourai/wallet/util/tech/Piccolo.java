package com.samourai.wallet.util.tech;

import android.content.Context;

import com.samourai.wallet.BuildConfig;
import com.samourai.wallet.SamouraiApplication;
import com.samourai.wallet.util.network.WebUtil;
import com.squareup.picasso.OkHttp3Downloader;
import com.squareup.picasso.Picasso;

import okhttp3.OkHttpClient;

public class Piccolo {

    private static Picasso piccolo;

    private Piccolo() {}

    public static Picasso get() {

        if (piccolo == null) {
            final Context context = SamouraiApplication.getAppContext();
            final OkHttpClient client = WebUtil.getInstance(context).getTorHttpClientBuilder().build();
            final OkHttp3Downloader downloader = new OkHttp3Downloader(client);
            piccolo = new Picasso.Builder(context).downloader(downloader)
                    .indicatorsEnabled(BuildConfig.DEBUG || BuildConfig.FLAVOR.equals("staging"))
                    .build();
        }
        return piccolo;

    }

}
