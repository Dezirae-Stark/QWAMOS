package com.samourai.wallet.api.wallet;

import static java.lang.String.format;
import static java.util.Objects.nonNull;

import android.content.Context;
import android.util.Log;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableMap;
import com.samourai.wallet.api.APIFactory;
import com.samourai.wallet.util.network.BackendApiAndroid;
import com.samourai.wallet.util.network.WebUtil;
import com.samourai.wallet.util.tech.AppUtil;

import java.util.Map;

public class WalletClient {

    private static final String TAG = "WalletClient";

    private static final ObjectMapper objectMapper = new ObjectMapper();

    private final Context context;

    private WalletClient(final Context context) {
        this.context = context;
    }

    public static WalletClient createWalletClient(final Context context) {
        return new WalletClient(context);
    }

    public RawWallet getRawWallet(final String address) {
        if (! AppUtil.getInstance(context).isOfflineMode()) {

            try {
                final String apiServiceUrl = BackendApiAndroid.getApiServiceUrl(format("wallet?active=%s", address));
                final String resultAsPlainText = WebUtil.getInstance(null).getURL(
                        apiServiceUrl,
                        ImmutableMap.of("Authorization", "Bearer " + getApiToken()));

                final Map<String, Object> entity = objectMapper.readValue(
                        resultAsPlainText,
                        new TypeReference<Map<String, Object>>() {});
                if (nonNull(entity)) {
                    return RawWallet.createRawWallet(entity);
                }
                return null;
            } catch (final Exception e) {
                Log.e(TAG, "issue on calling api for getRawWallet", e);
            }
        }
        return null;
    }

    private String getApiToken() {
        if (nonNull(context)) {
            return APIFactory.getInstance(context).getAccessToken();
        } else {
            return null;
        }
    }
}
