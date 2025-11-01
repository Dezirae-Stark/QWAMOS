package com.samourai.wallet.api.xpub;

import static java.lang.String.format;
import static java.util.Objects.isNull;
import static java.util.Objects.nonNull;

import android.content.Context;
import android.util.Log;

import com.google.common.collect.ImmutableMap;
import com.samourai.wallet.api.APIFactory;
import com.samourai.wallet.httpClient.HttpResponseException;
import com.samourai.wallet.util.func.EnumAddressType;
import com.samourai.wallet.util.network.BackendApiAndroid;
import com.samourai.wallet.util.network.WebUtil;
import com.samourai.wallet.util.tech.AppUtil;

import org.apache.commons.lang3.StringUtils;
import org.json.JSONObject;

public class XPubClient {

    private static final String TAG = "XPubClient";

    private final Context context;

    private XPubClient(final Context context) {
        this.context = context;
    }

    public static XPubClient createXPubClient(final Context context) {
        return new XPubClient(context);
    }

    public boolean isTracked(final EnumAddressType addressType, final String xpub) throws Exception {
        if (! AppUtil.getInstance(context).isOfflineMode()) {
            try {
                final String apiServiceUrl = BackendApiAndroid.getApiServiceUrl(format("xpub/%s", xpub));
                final String resultAsPlainText = WebUtil.getInstance(null).getURL(
                        apiServiceUrl,
                        ImmutableMap.of("Authorization", "Bearer " + getApiToken()));
                final JSONObject jsonObject = new JSONObject(resultAsPlainText);
                if (jsonObject.has("data")) {
                    final JSONObject data = jsonObject.getJSONObject("data");
                    if (data.has("derivation")) {
                        final String type = data.getString("derivation");
                        if (! StringUtils.containsIgnoreCase(type, "BIP" + addressType.getType())) {
                            return false;
                        }
                    }
                }
            } catch (final HttpResponseException e) {
                if (e.getStatusCode() == 400) {
                    Log.w(TAG, "xpub is not tracked");
                    return false;
                }
                throw  e;
            } catch (final Exception e2) {
                Log.e(TAG, "unexpected exception", e2);
                throw e2;
            }
        }
        return true;
    }

    public boolean track(final EnumAddressType addressType, final String xpub, final String tag) {
        if (! AppUtil.getInstance(context).isOfflineMode()) {
            try {
                final JSONObject content = APIFactory.getInstance(context).registerXPUB(xpub, addressType.getType(), tag);
                if (isNull(content)) return false;
            } catch (final Exception e) {
                Log.e(TAG, "issue on calling api for XPubClient#track", e);
                return false;
            }
        }
        return true;
    }

    private String getApiToken() {
        if (nonNull(context)) {
            return APIFactory.getInstance(context).getAccessToken();
        } else {
            return null;
        }
    }
}
