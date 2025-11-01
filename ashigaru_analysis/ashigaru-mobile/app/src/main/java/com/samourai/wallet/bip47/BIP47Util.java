package com.samourai.wallet.bip47;

import static com.samourai.wallet.bip47.BIP47Meta.STATUS_SENT_CFM;
import static org.apache.commons.lang3.StringUtils.isBlank;
import static java.util.Objects.nonNull;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.util.Log;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.core.content.ContextCompat;
import androidx.lifecycle.LiveData;
import androidx.lifecycle.MutableLiveData;

import com.samourai.wallet.SamouraiWallet;
import com.samourai.wallet.api.APIFactory;
import com.samourai.wallet.api.backend.beans.HttpException;
import com.samourai.wallet.bip47.paynym.WebUtil;
import com.samourai.wallet.bip47.rpc.AndroidSecretPointFactory;
import com.samourai.wallet.bip47.rpc.BIP47Wallet;
import com.samourai.wallet.bip47.rpc.PaymentAddress;
import com.samourai.wallet.bip47.rpc.PaymentCode;
import com.samourai.wallet.hd.HD_Address;
import com.samourai.wallet.hd.HD_WalletFactory;
import com.samourai.wallet.paynym.api.PayNymApiService;
import com.samourai.wallet.segwit.SegwitAddress;
import com.samourai.wallet.util.PrefsUtil;
import com.samourai.wallet.util.tech.ThreadHelper;

import org.apache.commons.lang3.tuple.Pair;
import org.bitcoinj.core.AddressFormatException;
import org.bitcoinj.core.NetworkParameters;
import org.bitcoinj.crypto.MnemonicException;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import io.reactivex.Completable;
import io.reactivex.android.schedulers.AndroidSchedulers;
import io.reactivex.schedulers.Schedulers;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

public class BIP47Util extends BIP47UtilGeneric {

    public static final String TAG = "BIP47Util";

    private static final boolean ALWAYS_ACCEPT_SEGWIT = true;

    private static BIP47Wallet wallet = null;

    private static Context context = null;
    private static BIP47Util instance = null;
    private MutableLiveData<Bitmap> paynymLogo = new MutableLiveData();

    public static BIP47Util getInstance(final Context ctx) {

        context = ctx;

        if (instance == null || wallet == null) {

            try {
                wallet = HD_WalletFactory.getInstance(context).getBIP47();
            } catch (IOException ioe) {
                ioe.printStackTrace();
                Toast.makeText(context, "HD wallet error", Toast.LENGTH_SHORT).show();
            } catch (MnemonicException.MnemonicLengthException mle) {
                mle.printStackTrace();
                Toast.makeText(context, "HD wallet error", Toast.LENGTH_SHORT).show();
            }

            instance = new BIP47Util();
        }

        return instance;
    }

    private BIP47Util() {
        super(AndroidSecretPointFactory.getInstance(), true);
    }

    private static NetworkParameters getNetworkParams() {
        return SamouraiWallet.getInstance().getCurrentNetworkParams();
    }

    public LiveData<Bitmap> getPayNymLogoLive() {
        return paynymLogo;
    }

    public File avatarImage() {
        File directory = ContextCompat.getDataDir(context);
        return new File(directory.getPath().concat(File.separator).concat("paynym.png"));
    }

    public void reset() {
        instance = new BIP47Util();
        wallet = null;
    }

    public BIP47Wallet getWallet() {
        return wallet;
    }

    public HD_Address getNotificationAddress() {
        return wallet.getAccount(0).getNotificationAddress();
    }

    public PaymentCode getPaymentCode() throws AddressFormatException {
        return wallet.getAccount(0).getPaymentCode();
    }

    public PaymentCode getFeaturePaymentCode() throws AddressFormatException {
        PaymentCode payment_code = getPaymentCode();
        return new com.samourai.wallet.bip47.rpc.PaymentCode(payment_code.makePaymentCodeSamourai());
    }

    public SegwitAddress getReceiveAddress(PaymentCode pcode, int idx) throws Exception {
        return super.getReceiveAddress(wallet.getAccount(0), pcode, idx, getNetworkParams());
    }

    // receive funds from bogous dexwpbug addresses
    public SegwitAddress getReceiveAddressFromDexwpBug(PaymentCode pcode, int idx) throws Exception {
        HD_Address address = wallet.getAccount(0).addressAt(idx);
        // dexwp bug
        return this.getPaymentAddress(pcode, idx, (HD_Address)address, getNetworkParams()).getSegwitAddressReceive();
    }

    public String getReceivePubKey(PaymentCode pcode, int idx) throws Exception {
        return super.getReceivePubKey(wallet.getAccount(0), pcode, idx, getNetworkParams());
    }

    public SegwitAddress getSendAddress(PaymentCode pcode, int idx) throws Exception {
        return super.getSendAddress(wallet.getAccount(0), pcode, idx, getNetworkParams());
    }

    public String getSendPubKey(PaymentCode pcode, int idx) throws Exception {
        return super.getSendPubKey(wallet.getAccount(0), pcode, idx, getNetworkParams());
    }

    public byte[] getIncomingMask(byte[] pubkey, byte[] outPoint) throws Exception {
        return super.getIncomingMask(wallet.getAccount(0), pubkey, outPoint, getNetworkParams());
    }

    public void setAvatar(final Bitmap bitmap) {
        paynymLogo.postValue(null); // reset in order to ensure the push with the next post
        if (nonNull(bitmap)) {
            paynymLogo.postValue(bitmap);
        } else {
            Log.d(TAG, "bitmap is null in setAvatar()");
        }
    }

    public Completable fetchBotImage() {
        String url = PayNymApiService.PAYNYM_API + "preview/" + getPaymentCode().toString();
        if(PrefsUtil.getInstance(context).getValue(PrefsUtil.PAYNYM_CLAIMED,false)){
            url = PayNymApiService.PAYNYM_API +  getPaymentCode().toString() + "/avatar";
        }
        String finalUrl = url;
        return Completable.fromCallable(() -> {
                    loadBotImage(finalUrl, 3);
                    return true;
                }).subscribeOn(Schedulers.io())
                .observeOn(AndroidSchedulers.mainThread());
    }

    private void loadBotImage(final String finalUrl, final int maxRetry)
            throws HttpException, IOException {

        final Request.Builder rb = new Request.Builder().url(finalUrl);
        final OkHttpClient client = com.samourai.wallet.util.network.WebUtil
                .getInstance(context)
                .getTorHttpClientBuilder(finalUrl)
                .build();
        final Response response = client.newCall(rb.build()).execute();
        if (response.isSuccessful()) {

            final File file = avatarImage();
            if (!file.exists()) {
                file.createNewFile();
            }

            boolean status = true;
            try (final OutputStream outStream = new FileOutputStream(file)) {
                outStream.write(response.body().bytes());
            } catch (final Exception e) {
                Log.e(TAG, "issue on creating paynym bitmap");
                status = false;
            }

            if (status) {
                final Bitmap bitmap = BitmapFactory.decodeFile(file.getPath());
                if (nonNull(bitmap)) {
                    setAvatar(bitmap);
                    return;
                }
            }
        }

        if (maxRetry > 0) {
            ThreadHelper.pauseMillis(5_000L);
            loadBotImage(finalUrl, maxRetry-1);
        } else {
            Log.e(TAG, "loading bot image failed");
        }
    }

    synchronized public String getSendAddressString(
            final String pcodeAsString
    ) throws Exception {

        return getSendAddressString(pcodeAsString, 0);
    }


    synchronized public String getSendAddressString(
            final String pcodeAsString,
            final int indexOffset
    ) throws Exception {

        if (isBlank(pcodeAsString)) return null;
        return getAddress(pcodeAsString, getPaymentAddressSend(pcodeAsString, indexOffset));
    }

    private static String getAddress(final String pcodeAsString,
                                     final PaymentAddress paymentAddress)
            throws Exception {

        if (ALWAYS_ACCEPT_SEGWIT || BIP47Meta.getInstance().getSegwit(pcodeAsString)) {
            return new SegwitAddress(
                    paymentAddress.getSendECKey(),
                    getNetworkParams()).getBech32AsString();

        } else {
            return paymentAddress.getSendECKey()
                    .toAddress(getNetworkParams()).toString();
        }
    }

    private PaymentAddress getPaymentAddressSend(final String pcodeAsString,
                                                 final int indexOffset)
            throws Exception {
        final int idx = indexOffset + BIP47Meta.getInstance().getOutgoingIdx(pcodeAsString);
        final HD_Address address = wallet.getAccount(0).getNotificationAddress();
        return getPaymentAddress(
                new PaymentCode(pcodeAsString),
                idx,
                address,
                getNetworkParams());
    }

    public int updateOutgoingStatusForNewPayNymConnections() {

        final APIFactory apiFactory = APIFactory.getInstance(context);
        final BIP47Meta bip47Meta = BIP47Meta.getInstance();

        int updatedCount = 0;
        for (final Pair<String, String> codeToTx : bip47Meta.getOutgoingUnconfirmed()) {
            final int status = BIP47Meta.getInstance().getOutgoingStatus(codeToTx.getLeft());
            if (status != STATUS_SENT_CFM) {
                final int confirmations = apiFactory.getNotifTxConfirmations(codeToTx.getRight());
                if (confirmations > 0) {
                    BIP47Meta.getInstance().setOutgoingStatus(
                            codeToTx.getLeft(),
                            codeToTx.getRight(),
                            STATUS_SENT_CFM);

                    ++updatedCount;
                }
            }
        }
        return updatedCount;
    }

    @NonNull
    public static List<String> getBip47Addresses(final Context context) throws Exception {
        final List<String> addressStrings = new ArrayList<>();
        addressStrings.addAll(Arrays.asList(BIP47Meta.getInstance().getIncomingAddresses(false)));
        for(String _s : Arrays.asList(BIP47Meta.getInstance().getIncomingLookAhead(context)))   {
            if(!addressStrings.contains(_s))    {
                addressStrings.add(_s);
            }
        }
        for(String pcode : BIP47Meta.getInstance().getUnspentProviders())   {
            for(String addr : BIP47Meta.getInstance().getUnspentAddresses(context, pcode))   {
                if(!addressStrings.contains(addr))    {
                    addressStrings.add(addr);
                }
            }
            List<Integer> idxs = BIP47Meta.getInstance().getUnspent(pcode);
            for(Integer idx : idxs)   {
                String receivePubKey = BIP47Util.getInstance(context).getReceivePubKey(new PaymentCode(pcode), idx);
                BIP47Meta.getInstance().getIdx4AddrLookup().put(receivePubKey, idx);
                BIP47Meta.getInstance().getPCode4AddrLookup().put(receivePubKey, pcode.toString());
                if(!addressStrings.contains(receivePubKey))    {
                    addressStrings.add(receivePubKey);
                }
            }
        }
        return addressStrings;
    }
}
