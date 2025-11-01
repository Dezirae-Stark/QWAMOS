package com.samourai.wallet;


import static com.samourai.wallet.util.tech.ThreadHelper.pauseMillis;

import static java.lang.String.format;

import android.app.Application;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.Context;
import android.net.ConnectivityManager;
import android.net.NetworkCapabilities;
import android.net.NetworkRequest;
import android.os.Build;
import android.util.Log;

import androidx.appcompat.app.AppCompatDelegate;
import androidx.multidex.MultiDex;

import com.samourai.wallet.payload.ExternalBackupManager;
import com.samourai.wallet.stealth.StealthModeController;
import com.samourai.wallet.tor.SamouraiTorManager;
import com.samourai.wallet.util.tech.AppUtil;
import com.samourai.wallet.util.network.ConnectionChangeReceiver;
import com.samourai.wallet.util.tech.LogUtil;
import com.samourai.wallet.util.PrefsUtil;
import com.samourai.wallet.util.tech.SimpleCallback;
import com.samourai.wallet.util.tech.SimpleTaskRunner;
import com.squareup.picasso.Picasso;

import io.reactivex.plugins.RxJavaPlugins;

public class SamouraiApplication extends Application {

    private static SamouraiApplication instance;

    private static final String TAG = "SamouraiApplication";

    public static String FOREGROUND_SERVICE_CHANNEL_ID = "FOREGROUND_SERVICE_CHANNEL_ID";
    public static String WHIRLPOOL_CHANNEL = "WHIRLPOOL_CHANNEL";
    public static String WHIRLPOOL_NOTIFICATIONS = "WHIRLPOOL_NOTIFICATIONS";

    @Override
    public void onCreate() {
        super.onCreate();
        instance = this;
        ExceptionReportHandler.Companion.attach(this);
        setUpTorService();
        setUpChannels();
        registerNetworkCallBack();
        RxJavaPlugins.setErrorHandler(throwable -> {
        });
        ExternalBackupManager.attach(this);

        AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_YES);

        if (BuildConfig.DEBUG || BuildConfig.FLAVOR.equals("staging")) {
            Picasso.get().setIndicatorsEnabled(true);
            LogUtil.setLoggersDebug();
        }
        StealthModeController.INSTANCE.fixStealthModeIfNotActive(getApplicationContext());
    }

    public static Context getAppContext() {
        return instance.getApplicationContext();
    }

    private void registerNetworkCallBack() {
        ConnectionChangeReceiver changeReceiver = new ConnectionChangeReceiver(getApplicationContext());
        NetworkRequest networkRequest = new NetworkRequest.Builder()
                .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
                .addTransportType(NetworkCapabilities.TRANSPORT_WIFI)
                .addTransportType(NetworkCapabilities.TRANSPORT_CELLULAR)
                .build();
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.M) {
            ConnectivityManager connectivityManager = (ConnectivityManager) getSystemService(ConnectivityManager.class);
            connectivityManager.requestNetwork(networkRequest, changeReceiver.getNetworkCallback());
        }
        AppUtil.getInstance(getApplicationContext()).checkOfflineState();
    }

    private void setUpChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            /*
            NotificationChannel whirlpoolChannel = new NotificationChannel(
                    WHIRLPOOL_CHANNEL,
                    "Whirlpool service ",
                    NotificationManager.IMPORTANCE_LOW
            );
            whirlpoolChannel.enableLights(false);
            whirlpoolChannel.enableVibration(false);
            whirlpoolChannel.setSound(null, null);
             */

            NotificationChannel serviceChannel = new NotificationChannel(
                    getString(R.string.tor_service_notification_channel_id),
                    getString(R.string.tor_service_notification_channel_name),
                    NotificationManager.IMPORTANCE_DEFAULT
            );
            serviceChannel.setSound(null, null);
            NotificationManager manager = getSystemService(NotificationManager.class);

            NotificationChannel refreshService = new NotificationChannel(
                    FOREGROUND_SERVICE_CHANNEL_ID,
                    "Ashigaru Service",
                    NotificationManager.IMPORTANCE_DEFAULT
            );
            refreshService.setSound(null, null);
            refreshService.setImportance(NotificationManager.IMPORTANCE_LOW);
            refreshService.setLockscreenVisibility(Notification.VISIBILITY_SECRET);


            /*
            NotificationChannel whirlpoolNotifications = new NotificationChannel(
                    WHIRLPOOL_NOTIFICATIONS,
                    "Mix status notifications",
                    NotificationManager.IMPORTANCE_HIGH
            );
             */


            //whirlpoolChannel.enableLights(true);

            if (manager != null) {
                manager.createNotificationChannel(serviceChannel);
                manager.createNotificationChannel(refreshService);
                //manager.createNotificationChannel(whirlpoolChannel);
                //manager.createNotificationChannel(whirlpoolNotifications);
            }
        }
    }

    protected void attachBaseContext(Context base) {
        super.attachBaseContext(base);
        MultiDex.install(this);
    }

    @Override
    public void onTerminate() {
        ExternalBackupManager.dispose();
        SamouraiTorManager.INSTANCE.stop();
        super.onTerminate();
    }

    private void setUpTorService() {
        SamouraiTorManager.INSTANCE.setUp(this);
        startTorIfRequired();
    }

    private void startTorIfRequired() {
        if(!StealthModeController.INSTANCE.isStealthEnabled(getApplicationContext())) {
            Log.i(TAG, "mode Stealth is disabled");
            if (PrefsUtil.getInstance(this).getValue(PrefsUtil.ENABLE_TOR, false)) {
                Log.i(TAG, "TOR option is enabled");
                if (!PrefsUtil.getInstance(this).getValue(PrefsUtil.OFFLINE, false)) {
                    Log.i(TAG, "OFFLINE option is disabled => will try to start TOR");
                    tryStart(5);
                } else {
                    Log.i(TAG, "OFFLINE option is enabled => will not start TOR");
                }
            } else {
                Log.i(TAG, "TOR option is disabled => will not start TOR");
            }
        } else {
            Log.i(TAG, "mode Stealth option is enabled => will not start TOR");
        }
    }

    private void tryStart(final int tryCount) {
        if (tryCount == 0) {
            Log.e(TAG, format("Cannot succeeded to start Tor after %s attempt", tryCount));
            return;
        }
        Log.i(TAG, format("will try to start tor (remaining %s try)", tryCount));
        SimpleTaskRunner.create().executeAsync(
                true,
                () -> {
                    if (tryCount == 1) {
                        SamouraiTorManager.INSTANCE.newIdentity();
                    } else {
                        SamouraiTorManager.INSTANCE.start();
                    }
                    for (int i = 0; i < 3; ++i) {
                        pauseMillis(2_000L);
                        if (SamouraiTorManager.INSTANCE.isConnected()) {
                            return null;
                        }
                    }
                    pauseMillis(4_000L);
                    return null;
                },
                new SimpleCallback<Object>() {
                    @Override
                    public void onComplete(Object result) {
                        if (! SamouraiTorManager.INSTANCE.isConnected()) {
                            tryStart(tryCount-1);
                        } else {
                            Log.i(TAG, "Tor is started");
                        }
                    }

                    @Override
                    public void onException(Throwable t) {
                        if (! SamouraiTorManager.INSTANCE.isConnected()) {
                            tryStart(tryCount-1);
                        } else {
                            Log.i(TAG, "Tor is started");
                        }
                    }
                }

        );
    }

}
