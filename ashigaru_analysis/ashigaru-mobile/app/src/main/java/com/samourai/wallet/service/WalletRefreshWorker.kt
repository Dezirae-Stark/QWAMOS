//package com.samourai.wallet.service
//
//import android.content.Context
//import android.content.Intent
//import android.util.Log
//import android.widget.Toast
//import androidx.localbroadcastmanager.content.LocalBroadcastManager
//import androidx.work.CoroutineWorker
//import androidx.work.OneTimeWorkRequestBuilder
//import androidx.work.Operation
//import androidx.work.WorkManager
//import androidx.work.WorkerParameters
//import androidx.work.workDataOf
//import com.samourai.wallet.SamouraiWallet
//import com.samourai.wallet.access.AccessFactory
//import com.samourai.wallet.api.APIFactory
//import com.samourai.wallet.bip47.BIP47Meta
//import com.samourai.wallet.bip47.BIP47Util
//import com.samourai.wallet.crypto.AESUtil
//import com.samourai.wallet.crypto.DecryptionException
//import com.samourai.wallet.payload.PayloadUtil
//import com.samourai.wallet.ricochet.RicochetMeta
//import com.samourai.wallet.util.CharSequenceX
//import com.samourai.wallet.util.PrefsUtil
//import com.samourai.wallet.util.func.WalletUtil
//import com.samourai.wallet.util.tech.AppUtil
//import kotlinx.coroutines.Dispatchers
//import kotlinx.coroutines.async
//import kotlinx.coroutines.coroutineScope
//import kotlinx.coroutines.launch
//import kotlinx.coroutines.withContext
//import org.apache.commons.lang3.tuple.Pair
//import org.bitcoinj.core.AddressFormatException
//import org.bitcoinj.crypto.MnemonicException.MnemonicLengthException
//import org.json.JSONException
//import java.io.IOException
//
//class WalletRefreshWorker(private val context: Context, private val parameters: WorkerParameters) :
//    CoroutineWorker(context, parameters) {
//
//
//    override suspend fun doWork(): Result {
//
//        val launch: Boolean = parameters.inputData.getBoolean(LAUNCHED, false)
//        val notifTx: Boolean = parameters.inputData.getBoolean(NOTIF_TX, false)
//
//        AppUtil.getInstance(applicationContext).setWalletLoading(true)
//        APIFactory.getInstance(context).stayingAlive()
//        APIFactory.getInstance(context).initWallet()
//
//        val _intentDisplay = Intent("com.samourai.wallet.BalanceFragment.DISPLAY")
//        LocalBroadcastManager.getInstance(context).sendBroadcast(_intentDisplay)
//
//        if (notifTx && !AppUtil.getInstance(context).isOfflineMode) {
//            //
//            // check for incoming payment code notification tx
//            //
//            try {
//                val pcode = BIP47Util.getInstance(context).paymentCode
//                //                    Log.i("BalanceFragment", "payment code:" + pcode.toString());
////                    Log.i("BalanceFragment", "notification address:" + pcode.notificationAddress().getAddressString());
//                APIFactory.getInstance(context).getNotifAddress(pcode.notificationAddress(SamouraiWallet.getInstance().currentNetworkParams).addressString)
//            } catch (afe: AddressFormatException) {
//                afe.printStackTrace()
//                Toast.makeText(context, "HD wallet error", Toast.LENGTH_SHORT).show()
//            } catch (ex: Exception) {
//                ex.printStackTrace()
//            }
//
//            loadConnectedPaynyms()
//            val _intent = Intent("com.samourai.wallet.MainActivity2.RESTART_SERVICE")
//            LocalBroadcastManager.getInstance(context).sendBroadcast(_intent)
//        }
//
//        if (launch) {
//
//            if (PrefsUtil.getInstance(context).getValue(PrefsUtil.GUID_V, 0) < 4) {
//
//                Log.i(TAG, "guid_v < 4")
//
//                try {
//                    val _guid = AccessFactory.getInstance(context).createGUID()
//                    val _hash = AccessFactory.getInstance(context).getHash(_guid, CharSequenceX(AccessFactory.getInstance(context).pin), AESUtil.DefaultPBKDF2Iterations)
//                    PayloadUtil.getInstance(context).saveWalletToJSON(CharSequenceX(_guid + AccessFactory.getInstance().pin))
//                    PrefsUtil.getInstance(context).setValue(PrefsUtil.ACCESS_HASH, _hash)
//                    PrefsUtil.getInstance(context).setValue(PrefsUtil.ACCESS_HASH2, _hash)
//                    Log.i(TAG, "guid_v == 4")
//                } catch (e: MnemonicLengthException) {
//                } catch (e: IOException) {
//                } catch (e: JSONException) {
//                } catch (e: DecryptionException) {
//                }
//            }
//
//            try {
//                val prevIdx = RicochetMeta.getInstance(context).index
//                APIFactory.getInstance(context).parseRicochetXPUB()
//                if (prevIdx > RicochetMeta.getInstance(context).index) {
//                    RicochetMeta.getInstance(context).index = prevIdx
//                }
//            } catch (je: JSONException) {
//            } catch (e: Exception) {
//            }
//        }
//
//        withContext(Dispatchers.IO) {
//            try {
//                WalletUtil.saveWallet(context)
//            } catch (ignored: Exception) {
//            }
//        }
//
//        withContext(Dispatchers.Main) {
//            val _intent = Intent("com.samourai.wallet.BalanceFragment.DISPLAY")
//            LocalBroadcastManager.getInstance(context).sendBroadcast(_intent)
//        }
//
//        AppUtil.getInstance(applicationContext).setWalletLoading(false)
//        val data = workDataOf();
//        return Result.success(data)
//    }
//
//    private fun loadConnectedPaynyms() {
//        //
//        // check on outgoing payment code notification tx
//        //
//        val outgoingUnconfirmed: List<Pair<String?, String?>> = BIP47Meta.getInstance().outgoingUnconfirmed
//        for (pair in outgoingUnconfirmed) {
//            val confirmations = APIFactory.getInstance(context).getNotifTxConfirmations(pair.right)
//            if (confirmations > 0) {
//                BIP47Meta.getInstance().setOutgoingStatus(pair.left, BIP47Meta.STATUS_SENT_CFM)
//            }
//            if (confirmations == -1) {
//                BIP47Meta.getInstance().setOutgoingStatus(pair.left, BIP47Meta.STATUS_NOT_SENT)
//            }
//        }
//    }
//
//    companion object {
//        const val LAUNCHED = "LAUNCHED"
//        const val NOTIF_TX = "NOTIF_TX"
//        private const val TAG = "WalletRefreshWorker"
//
//        fun enqueue(context: Context, notifTx: Boolean = false, launched: Boolean = false): Operation {
//            val workManager = WorkManager.getInstance(context)
//            val workRequest = OneTimeWorkRequestBuilder<WalletRefreshWorker>().apply {
//                setInputData(
//                    workDataOf(
//                        LAUNCHED to launched,
//                        NOTIF_TX to notifTx
//                    )
//                )
//            }.build()
//            return workManager.enqueue(workRequest)
//        }
//    }
//
//
//}