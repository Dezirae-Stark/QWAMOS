package com.samourai.wallet.api.txs;

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

public class TxsClient {

    private static final String TAG = "TxsClient";

    private static final ObjectMapper objectMapper = new ObjectMapper();

    private final Context context;

    private TxsClient(final Context context) {
        this.context = context;
    }

    public static TxsClient createTxsClient(final Context context) {
        return new TxsClient(context);
    }

    public PaginatedRawTxs getPage(
            final String addresses,
            final int pageIndex,
            final int pageSize) {

        if (! AppUtil.getInstance(context).isOfflineMode()) {

            try {
                final String apiServiceUrl = BackendApiAndroid.getApiServiceUrl(format(
                        "txs?active=%s&page=%s&count=%s",
                        addresses,
                        pageIndex,
                        pageSize
                ));
                final String resultAsPlainText = WebUtil.getInstance(null).getURL(
                        apiServiceUrl,
                        ImmutableMap.of("Authorization", "Bearer " + getApiToken()));

                final PaginatedRawTxs paginatedRawTxs = objectMapper.readValue(
                        resultAsPlainText,
                        new TypeReference<PaginatedRawTxs>() {});

                return paginatedRawTxs;
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
