package com.samourai.wallet.home;

import static com.samourai.wallet.constants.SamouraiAccountIndex.BADBANK;
import static com.samourai.wallet.constants.SamouraiAccountIndex.DEPOSIT;
import static com.samourai.wallet.constants.SamouraiAccountIndex.POSTMIX;

import android.app.Application;
import android.content.Context;
import android.content.SharedPreferences;
import android.util.Pair;

import androidx.annotation.NonNull;
import androidx.lifecycle.AndroidViewModel;
import androidx.lifecycle.LiveData;
import androidx.lifecycle.MutableLiveData;

import com.samourai.wallet.api.APIFactory;
import com.samourai.wallet.api.Tx;
import com.samourai.wallet.payload.PayloadUtil;
import com.samourai.wallet.send.BlockedUTXO;
import com.samourai.wallet.util.PrefsUtil;
import com.samourai.wallet.util.tech.LogUtil;
import com.samourai.wallet.whirlpool.WhirlpoolMeta;

import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import io.reactivex.Observable;
import io.reactivex.android.schedulers.AndroidSchedulers;
import io.reactivex.disposables.CompositeDisposable;
import io.reactivex.disposables.Disposable;
import io.reactivex.schedulers.Schedulers;

public class BalanceViewModel extends AndroidViewModel {

    private static final String TAG = "BalanceViewModel";
    private MutableLiveData<List<Tx>> txs = new MutableLiveData<>();
    private MutableLiveData<Long> balance = new MutableLiveData<>();
    private int account = 0;

    Context mContext = this.getApplication();
    SharedPreferences sharedpreferences;
    public static final String MyPREFERENCES = "com.samourai.wallet_preferences" ;

    private MutableLiveData<Integer> formatBalance = new MutableLiveData<Integer>();
    private CompositeDisposable compositeDisposables = new CompositeDisposable();

    public BalanceViewModel(@NonNull Application application) {
        super(application);
        Integer format = PrefsUtil.getInstance(this.mContext).getValue(PrefsUtil.BALANCE_FORMAT, 0);
        this.formatBalance.setValue(format);
    }

    public LiveData<List<Tx>> getTxs() {
        return this.txs;
    }

   public void loadOfflineData() {

       final Integer balanceFormat = PrefsUtil.getInstance(this.mContext).getValue(PrefsUtil.BALANCE_FORMAT, 0);

       final Disposable disposableJson = Observable.fromCallable(() -> {
                   if (account == 0) {
                       return PayloadUtil.getInstance(getApplication()).deserializeMultiAddr();
                   } else if (account == WhirlpoolMeta.getInstance(getApplication()).getWhirlpoolPostmix()) {
                       return PayloadUtil.getInstance(getApplication()).deserializeMultiAddrMix();
                   } else {
                       return null;
                   }
               })
               .subscribeOn(Schedulers.io())
               .observeOn(AndroidSchedulers.mainThread())
               .subscribe(response -> {
                   if (response == null) {
                       return;
                   }

                   Observable<Pair<List<Tx>, Long>> parser = account == 0
                           ? APIFactory.getInstance(getApplication()).parseXPUBObservable(new JSONObject(response.toString()))
                           : APIFactory.getInstance(getApplication()).parseMixXPUBObservable(new JSONObject(response.toString()));
                   Disposable disposable = parser
                           .subscribeOn(Schedulers.computation())
                           .observeOn(AndroidSchedulers.mainThread())
                           .subscribe(pairValues -> {
                               List<Tx> txes = pairValues.first;
                               Long xpub_balance = pairValues.second;
                               Collections.sort(txes, new APIFactory.TxMostRecentDateComparator());
                               txs.postValue(txes);
                               this.formatBalance.setValue(balanceFormat);
                               if (account == DEPOSIT) {
                                   balance.postValue(xpub_balance - BlockedUTXO.getInstance().getTotalValueBlocked0());
                               } else if (account == POSTMIX) {
                                   balance.postValue(xpub_balance - BlockedUTXO.getInstance().getTotalValuePostMix());
                               } else if (account == BADBANK) {
                                   balance.postValue(xpub_balance - BlockedUTXO.getInstance().getTotalValueBadBank());
                               }
                           }, error -> {
                               LogUtil.info(TAG,error.getMessage());
                               txs.postValue(new ArrayList<>());
                               this.formatBalance.setValue(balanceFormat);
                               balance.postValue(0L);
                           });

                   compositeDisposables.add(disposable);

               }, error -> {
                   LogUtil.info(TAG,error.getMessage());
                   txs.postValue(new ArrayList<>());
                   this.formatBalance.setValue(balanceFormat);
                   balance.postValue(0L);
               });
       compositeDisposables.add(disposableJson);
    }


    @Override
    protected void onCleared() {
        compositeDisposables.dispose();
        super.onCleared();
    }

    public LiveData<Long> getBalance() {
        return balance;
    }

    MutableLiveData<Integer> getFormatBalance() {
        return this.formatBalance;
    }

    Integer switchBalanceFormat() {
        sharedpreferences = mContext.getSharedPreferences(MyPREFERENCES, Context.MODE_PRIVATE);
        int balanceFormat = PrefsUtil.getInstance(this.mContext).getValue(PrefsUtil.BALANCE_FORMAT, 0);

        switch (balanceFormat){
            case 0: //if set to BTC, switch to sats
                this.formatBalance.setValue(1);
                return this.formatBalance.getValue();
            case 1: //if set to sats, switch to street mode
                this.formatBalance.setValue(2);
                return this.formatBalance.getValue();
            case 2: // if set to street mode, set to BTC
                this.formatBalance.setValue(0);
                return this.formatBalance.getValue();
            default:
                this.formatBalance.setValue(0);
                return this.formatBalance.getValue();
        }

    }

    public void setTx(List<Tx> txes) {
        if (txes == null || txes.size() == 0) {
            return;
        }
        this.txs.postValue(txes);
    }

    public void postNewBalance(Long balance) {
        this.balance.postValue(balance);
    }

    public void setAccount(int account) {
        this.account = account;
    }
}
