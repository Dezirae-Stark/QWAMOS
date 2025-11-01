package com.samourai.wallet.util.network;

import static org.apache.commons.lang3.StringUtils.strip;

import android.content.Context;

import com.samourai.http.client.AndroidHttpClient;
import com.samourai.http.client.AndroidHttpClientService;
import com.samourai.wallet.SamouraiWallet;
import com.samourai.wallet.api.APIFactory;
import com.samourai.wallet.api.backend.BackendApi;
import com.samourai.wallet.api.backend.BackendServer;
import com.samourai.wallet.httpClient.HttpUsage;
import com.samourai.wallet.network.dojo.DojoUtil;
import com.samourai.wallet.tor.SamouraiTorManager;

public class BackendApiAndroid {
    public static final boolean FULL_DOJO_MODE_ONLY = true;
    public static final String URI_SEP = "/";
    private static BackendApi backendApi;

    public static BackendApi getInstance(final Context ctx) {
        if (backendApi == null) {
            AndroidHttpClient httpClient = AndroidHttpClientService.getInstance(ctx).getHttpClient(HttpUsage.BACKEND);
            boolean testnet = SamouraiWallet.getInstance().isTestNet();
            if (FULL_DOJO_MODE_ONLY || (DojoUtil.getInstance(ctx).getDojoParams() != null)) {
                // use dojo backend
                final String dojoApiKey = APIFactory.getInstance(ctx).getAppToken();
                backendApi = BackendApi.newBackendApiDojo(httpClient, getApiBaseUrl(), dojoApiKey);
            } else {
                // use samourai backend
                boolean onion = SamouraiTorManager.INSTANCE.isRequired();
                String backendUrl = BackendServer.get(testnet).getBackendUrl(onion);
                backendApi = BackendApi.newBackendApiSamourai(httpClient, backendUrl);
            }
        }
        return backendApi;
    }

    public static void reset() {
        backendApi = null;
    }

    public static String getApiBaseUrl() {
        return SamouraiWallet.getInstance().isTestNet()
                ? WebUtil.SAMOURAI_API2_TESTNET_TOR
                : WebUtil.SAMOURAI_API2_TOR;
    }

    public static String getApiServiceUrl(final String service) {
        return strip(getApiBaseUrl(), URI_SEP) + URI_SEP + strip(service, URI_SEP);
    }
}
