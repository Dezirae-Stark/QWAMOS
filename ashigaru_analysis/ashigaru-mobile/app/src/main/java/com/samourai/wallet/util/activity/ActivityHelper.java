package com.samourai.wallet.util.activity;

import static android.content.Context.CLIPBOARD_SERVICE;
import static java.util.Objects.isNull;
import static java.util.Objects.nonNull;

import android.app.Activity;
import android.content.ClipData;
import android.content.ClipData.Item;
import android.content.ClipboardManager;
import android.content.Intent;
import android.util.Log;
import android.widget.Toast;

import androidx.annotation.NonNull;

import com.samourai.wallet.R;
import com.samourai.wallet.SamouraiActivity;
import com.samourai.wallet.explorer.ExplorerActivity;
import com.samourai.wallet.home.BalanceActivity;

public class ActivityHelper {

    private static final String TAG = "ActivityHelper";

    private ActivityHelper() {}

    public static void launchSupportPageInBrowser(final Activity activity,
                                                  final boolean connectedOnTor) {

        final String url = getSupportHttpUrl(connectedOnTor);
        final Intent explorerIntent = new Intent(activity, ExplorerActivity.class);
        explorerIntent.putExtra(ExplorerActivity.SUPPORT, url);
        activity.startActivity(explorerIntent);
    }

    @NonNull
    private static String getSupportHttpUrl(boolean connectedOnTor) {
        if (connectedOnTor) {
            return null; // "http://72typmu5edrjmcdkzuzmv2i4zqru7rjlrcxwtod4nu6qtfsqegngzead.onion/support";
        }
        return null; //"https://samouraiwallet.com/support";
    }

    public static ClipData getClipboardData(final Activity activity) {
        try {
            return ((ClipboardManager) activity.getSystemService(CLIPBOARD_SERVICE)).getPrimaryClip();
        } catch (final Exception e) {
            Log.e(TAG, e.getMessage(), e);
            return null;
        }
    }

    public static Item getFirstItemFromClipboard(final Activity activity) {
        final ClipData clipboardData = getClipboardData(activity);
        if (isNull(clipboardData)) {
            Toast.makeText(activity, R.string.clipboard_unable_access, Toast.LENGTH_SHORT).show();
            return null;
        }
        if (clipboardData.getItemCount() <= 0) {
            Toast.makeText(activity, R.string.clipboard_empty, Toast.LENGTH_SHORT).show();
            return null;
        }

        final Item item = clipboardData.getItemAt(0);
        if (nonNull(item)) {
            return item;
        } else {
            Toast.makeText(activity, R.string.clipboard_item_inconsistent, Toast.LENGTH_SHORT).show();
            return null;
        }
    }

    public static void gotoBalanceHomeActivity(final SamouraiActivity currentActivity,
                                               final int account) {

        final Intent _intent = new Intent(currentActivity, BalanceActivity.class);
        _intent.putExtra("_account", account);
        _intent.putExtra("refresh", true);
        _intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TASK |
                Intent.FLAG_ACTIVITY_NEW_TASK |
                Intent.FLAG_ACTIVITY_SINGLE_TOP);
        currentActivity.startActivity(_intent);
        currentActivity.finish();
    }
}
