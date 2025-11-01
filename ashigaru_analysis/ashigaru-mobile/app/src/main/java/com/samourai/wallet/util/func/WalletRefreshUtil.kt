package com.samourai.wallet.util.func

import android.content.Context
import android.content.Intent
import android.util.Log
import android.widget.Toast
import androidx.localbroadcastmanager.content.LocalBroadcastManager
import com.samourai.wallet.SamouraiWallet
import com.samourai.wallet.access.AccessFactory
import com.samourai.wallet.api.APIFactory
import com.samourai.wallet.bip47.BIP47Meta
import com.samourai.wallet.bip47.BIP47Util
import com.samourai.wallet.crypto.AESUtil
import com.samourai.wallet.crypto.DecryptionException
import com.samourai.wallet.ricochet.RicochetMeta
import com.samourai.wallet.util.CharSequenceX
import com.samourai.wallet.util.PrefsUtil
import com.samourai.wallet.util.tech.AppUtil
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.sync.withPermit
import kotlinx.coroutines.withContext
import org.apache.commons.lang3.tuple.Pair
import org.bitcoinj.core.AddressFormatException
import org.bitcoinj.crypto.MnemonicException
import org.json.JSONException
import java.io.IOException

class WalletRefreshUtil {

    companion object {

        private const val TAG = "WalletRefreshUtil"

        /**
         * mutex, isMethodRunning, deferred are useful to ensure loadingWallet is atomic
         * and also to await the other thread the end of loadingWallet execution
         * without to execute it (in case of concurrence)
         */
        private val mutexForLoadingWallet = Mutex()
        private var isMethodRunning = false
        private var deferred: CompletableDeferred<Unit>? = null

        fun refreshWallet(notifTx: Boolean = false, launch: Boolean = false, context: Context) {
            runBlocking {
                withContext(Dispatchers.IO) {
                    loadingWalletAtomic(launch, notifTx, context)
                }
            }
        }

        suspend private fun loadingWalletAtomic(
            launch: Boolean,
            notifTx: Boolean,
            context: Context
        ) {
            mutexForLoadingWallet.withLock {
                if (isMethodRunning) {
                    Log.i(TAG, "loadingWallet() is currently running, waiting... by ${Thread.currentThread().name}")
                    deferred?.await()
                    Log.i(TAG, "Continuing without calling loadingWallet() by ${Thread.currentThread().name}")
                    return
                } else {
                    Log.i(TAG, "Will execute without loadingWallet() by ${Thread.currentThread().name}")
                    isMethodRunning = true
                    deferred = CompletableDeferred()
                }
            }

            try {
                loadingWallet(launch, notifTx, context)
            } finally {
                isMethodRunning = false
                deferred?.complete(Unit)
                deferred = null
            }
        }

        suspend private fun loadingWallet(
            launch: Boolean,
            notifTx: Boolean,
            context: Context
        ) {

            withContext(Dispatchers.Main) {
                AppUtil.getInstance(context).setWalletLoading(true)
                Log.i(TAG, "executing loadingWallet()...")
            }

            APIFactory.getInstance(context).stayingAlive()

            withContext(Dispatchers.IO) {
                val tasks = listOf(
                    async {
                        if (notifTx && !AppUtil.getInstance(context).isOfflineMode) {
                            updatePayNymConnections(context)
                        }
                    },
                    async {
                        if (launch) {
                            setHashs(context)
                            updateRicochetIndex(context)
                        }
                    }
                )
                tasks.awaitAll()
            }

            APIFactory.getInstance(context).initWallet()

            withContext(Dispatchers.Main) {
                val _intent = Intent("com.samourai.wallet.BalanceFragment.DISPLAY")
                LocalBroadcastManager.getInstance(context).sendBroadcast(_intent)
                AppUtil.getInstance(context).setWalletLoading(false)
                Log.i(TAG, "execution of loadingWallet() is done")
            }

            WalletUtil.saveWallet(context)
        }

        private fun updateRicochetIndex(context: Context) {
            try {
                val prevIdx = RicochetMeta.getInstance(context).index
                APIFactory.getInstance(context).parseRicochetXPUB()
                if (prevIdx > RicochetMeta.getInstance(context).index) {
                    RicochetMeta.getInstance(context).index = prevIdx
                }
            } catch (je: JSONException) {
            } catch (e: Exception) {
            }
        }

        private fun setHashs(context: Context) {
            if (PrefsUtil.getInstance(context).getValue(PrefsUtil.GUID_V, 0) < 4) {

                Log.i(TAG, "guid_v < 4")

                try {
                    val _guid = AccessFactory.getInstance(context).createGUID()
                    val _hash = AccessFactory.getInstance(context).getHash(
                        _guid, CharSequenceX(
                            AccessFactory.getInstance(context).pin
                        ), AESUtil.DefaultPBKDF2Iterations
                    )
                    PrefsUtil.getInstance(context).setValue(PrefsUtil.ACCESS_HASH, _hash)
                    PrefsUtil.getInstance(context).setValue(PrefsUtil.ACCESS_HASH2, _hash)
                    Log.i(TAG, "guid_v == 4")
                } catch (e: MnemonicException.MnemonicLengthException) {
                } catch (e: IOException) {
                } catch (e: JSONException) {
                } catch (e: DecryptionException) {
                }
            }
        }

        suspend private fun updatePayNymConnections(context: Context) {
            //
            // check for incoming payment code notification tx
            //
            withContext(Dispatchers.IO) {
                val tasks = listOf(
                    async { updateIncomingPaynymConnections(context) },
                    async { updateOutgoingPaynymConnections(context) }
                )
                tasks.awaitAll()
            }
            val _intent = Intent("com.samourai.wallet.MainActivity2.RESTART_SERVICE")
            LocalBroadcastManager.getInstance(context).sendBroadcast(_intent)
        }

        private fun updateIncomingPaynymConnections(context: Context) {
            try {
                val pcode = BIP47Util.getInstance(context).paymentCode
                APIFactory.getInstance(context)
                    .getNotifAddress(pcode.notificationAddress(SamouraiWallet.getInstance().currentNetworkParams).addressString)
            } catch (afe: AddressFormatException) {
                afe.printStackTrace()
                Toast.makeText(context, "HD wallet error", Toast.LENGTH_SHORT).show()
            } catch (ex: Exception) {
                ex.printStackTrace()
            }
        }

        suspend private fun updateOutgoingPaynymConnections(context: Context) {
            //
            // check on outgoing payment code notification tx
            //
            val outgoingUnconfirmed: List<Pair<String?, String?>> = BIP47Meta.getInstance().outgoingUnconfirmed
            val semaphore = Semaphore(6)
            withContext(Dispatchers.IO) {
                val deferredList = outgoingUnconfirmed.map {
                    async {
                        semaphore.withPermit {
                            val confirmations = APIFactory.getInstance(context).getNotifTxConfirmations(it.right)
                            if (confirmations > 0) {
                                BIP47Meta.getInstance().setOutgoingStatus(it.left, BIP47Meta.STATUS_SENT_CFM)
                            }
                        }
                    }
                }
                deferredList.awaitAll()
            }
        }

    }
}
