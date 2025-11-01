package com.samourai.wallet.api.ping;

import static java.lang.String.format;
import static java.util.Objects.nonNull;

import android.content.Context;
import android.util.Log;

import com.google.common.collect.ImmutableMap;
import com.samourai.wallet.api.APIFactory;
import com.samourai.wallet.httpClient.HttpResponseException;
import com.samourai.wallet.util.network.BackendApiAndroid;
import com.samourai.wallet.util.network.AshigaruNetworkException;
import com.samourai.wallet.util.network.WebUtil;
import com.samourai.wallet.util.tech.AppUtil;

import java.util.Map;

public class PingDojoClient {

    private static final String TAG = "PingDojoClient";

    private final Context context;

    private PingDojoClient(final Context context) {
        this.context = context;
    }

    public static PingDojoClient createPingDojoClient(final Context context) {
        return new PingDojoClient(context);
    }

    public void ping() throws AshigaruNetworkException {

        Log.i(TAG, "ping Dojo");

        boolean flag = false;

        if (! AppUtil.getInstance(context).isOfflineMode()) {

            try {
                final String apiServiceUrl = BackendApiAndroid.getApiServiceUrl(format("fees"));

                final Map<String, String> headers = ImmutableMap.of(
                        "Authorization",
                        "Bearer " + getApiToken());

                final String content = WebUtil.getInstance(null).tor_getURL(apiServiceUrl, headers);
                Log.i(TAG, "pong Dojo " + content);
                flag = true;
            } catch (final HttpResponseException e) {
                if (e.getStatusCode() == 400) {
                    Log.i(TAG, "pong Dojo " + e.getResponseBody());
                    flag = true;
                }
            } catch (final Exception e2) {
                Log.w(TAG, "failed pong Dojo : " + e2.getMessage());
            }
        }
        if (!flag) {
            throw new AshigaruNetworkException("ping Dojo failed");
        }
    }

    private String getApiToken() {
        if (nonNull(context)) {
            return APIFactory.getInstance(context).getAccessToken();
        } else {
            return null;
        }
    }
}
