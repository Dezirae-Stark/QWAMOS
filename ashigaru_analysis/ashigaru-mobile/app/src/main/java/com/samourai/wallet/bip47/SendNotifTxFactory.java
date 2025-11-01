package com.samourai.wallet.bip47;

import android.util.Log;

import com.samourai.wallet.SamouraiWallet;

import java.math.BigInteger;

public class SendNotifTxFactory {

    public static final BigInteger _bNotifTxValue = SamouraiWallet.bDust;
    public static final BigInteger _bSWFee = SamouraiWallet.bFee;
//    public static final BigInteger _bSWCeilingFee = BigInteger.valueOf(50000L);

    static SendNotifTxFactory _instance = null;

    public String SAMOURAI_NOTIF_TX_FEE_ADDRESS = "bc1qca73k4dt9sfr47rr3wvpmpl08xs5f7tvhsxhdt";
    public String TESTNET_SAMOURAI_NOTIF_TX_FEE_ADDRESS = "tb1qe2s3cre37j2ajlrk0gpdkymujqxs7zt47htwm7";

//    public static final double _dSWFeeUSD = 0.5;

    private SendNotifTxFactory() {
    }


    public static SendNotifTxFactory getInstance() {
        if (_instance == null) {
            _instance = new SendNotifTxFactory();
        }
        return _instance;
    }

    public void setAddress(String address) {
        if(SamouraiWallet.getInstance().isTestNet()){
            TESTNET_SAMOURAI_NOTIF_TX_FEE_ADDRESS = address;
        }else {
            SAMOURAI_NOTIF_TX_FEE_ADDRESS = address;
        }
        Log.i("TAG","address BIP47 ".concat(address));
    }
}
