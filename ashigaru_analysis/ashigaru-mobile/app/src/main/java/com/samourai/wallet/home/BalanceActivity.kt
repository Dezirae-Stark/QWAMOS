package com.samourai.wallet.home

import android.content.BroadcastReceiver
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.DialogInterface
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.ActivityInfo
import android.graphics.BitmapFactory
import android.graphics.Typeface
import android.graphics.drawable.BitmapDrawable
import android.net.Uri
import android.os.AsyncTask
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.util.TypedValue
import android.view.Menu
import android.view.MenuItem
import android.view.View
import android.widget.EditText
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.appcompat.app.AlertDialog
import androidx.core.content.ContextCompat
import androidx.core.view.isVisible
import androidx.lifecycle.viewModelScope
import androidx.localbroadcastmanager.content.LocalBroadcastManager
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout.OnRefreshListener
import androidx.transition.ChangeBounds
import androidx.transition.TransitionManager
import com.dm.zbar.android.scanner.ZBarConstants
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.google.android.material.shape.ShapeAppearanceModel
import com.google.common.collect.Lists
import com.google.gson.Gson
import com.samourai.wallet.R
import com.samourai.wallet.ReceiveActivity
import com.samourai.wallet.SamouraiActivity
import com.samourai.wallet.SamouraiWallet
import com.samourai.wallet.access.AccessFactory
import com.samourai.wallet.api.APIFactory
import com.samourai.wallet.api.APIFactory.TxMostRecentDateComparator
import com.samourai.wallet.api.Tx
import com.samourai.wallet.bip47.BIP47Meta
import com.samourai.wallet.bip47.BIP47Util
import com.samourai.wallet.cahoots.Cahoots
import com.samourai.wallet.cahoots.psbt.PSBTUtil
import com.samourai.wallet.collaborate.CollaborateActivity
import com.samourai.wallet.constants.SamouraiAccountIndex.DEPOSIT
import com.samourai.wallet.constants.SamouraiAccountIndex.POSTMIX
import com.samourai.wallet.crypto.AESUtil
import com.samourai.wallet.crypto.DecryptionException
import com.samourai.wallet.databinding.ActivityBalanceBinding
import com.samourai.wallet.fragments.CameraFragmentBottomSheet
import com.samourai.wallet.fragments.ScanFragment
import com.samourai.wallet.hd.HD_WalletFactory
import com.samourai.wallet.home.adapters.TxAdapter
import com.samourai.wallet.network.NetworkDashboard
import com.samourai.wallet.network.dojo.DojoUtil
import com.samourai.wallet.pairing.PairingMenuActivity
import com.samourai.wallet.payload.ExternalBackupManager.askPermission
import com.samourai.wallet.payload.ExternalBackupManager.hasPermissions
import com.samourai.wallet.payload.ExternalBackupManager.onActivityResult
import com.samourai.wallet.payload.PayloadUtil
import com.samourai.wallet.paynym.PayNymHome
import com.samourai.wallet.paynym.api.PayNymApiService
import com.samourai.wallet.paynym.models.NymResponse
import com.samourai.wallet.paynym.paynymDetails.PayNymDetailsActivity
import com.samourai.wallet.ricochet.RicochetMeta
import com.samourai.wallet.segwit.bech32.Bech32Util
import com.samourai.wallet.send.BlockedUTXO
import com.samourai.wallet.send.MyTransactionOutPoint
import com.samourai.wallet.send.SendActivity
import com.samourai.wallet.send.SendActivity.isPSBT
import com.samourai.wallet.send.batch.InputBatchSpendHelper.canParseAsBatchSpend
import com.samourai.wallet.send.cahoots.ManualCahootsActivity
import com.samourai.wallet.settings.SettingsActivity
import com.samourai.wallet.stealth.StealthModeController
import com.samourai.wallet.tools.ToolsBottomSheet
import com.samourai.wallet.tools.viewmodels.Auth47ViewModel
import com.samourai.wallet.tor.EnumTorState
import com.samourai.wallet.tor.SamouraiTorManager
import com.samourai.wallet.tor.TorState
import com.samourai.wallet.tx.TxDetailsActivity
import com.samourai.wallet.util.AppUpdateAvailableBottomSheet
import com.samourai.wallet.util.CharSequenceX
import com.samourai.wallet.util.PrefsUtil
import com.samourai.wallet.util.PrivKeyReader
import com.samourai.wallet.util.TimeOutUtil
import com.samourai.wallet.util.func.FormatsUtil
import com.samourai.wallet.util.func.WalletRefreshUtil
import com.samourai.wallet.util.func.WalletUtil
import com.samourai.wallet.util.func.executeFeaturePayNymUpdate
import com.samourai.wallet.util.network.BlockExplorerUtil
import com.samourai.wallet.util.tech.AppUtil
import com.samourai.wallet.util.tech.LogUtil
import com.samourai.wallet.util.tech.Piccolo
import com.samourai.wallet.util.tech.askNotificationPermission
import com.samourai.wallet.utxos.UTXOSActivity
import com.samourai.wallet.whirlpool.WhirlpoolMeta
import com.samourai.wallet.widgets.ItemDividerDecorator
import com.samourai.wallet.widgets.popUpMenu.popupMenu
import com.squareup.picasso.Callback
import io.reactivex.Observable
import io.reactivex.Single
import io.reactivex.android.schedulers.AndroidSchedulers
import io.reactivex.schedulers.Schedulers
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import kotlinx.coroutines.withContext
import org.apache.commons.lang3.StringUtils
import org.bitcoinj.crypto.MnemonicException.MnemonicLengthException
import org.bitcoinj.script.Script
import org.bouncycastle.util.encoders.Hex
import org.json.JSONException
import org.json.JSONObject
import java.io.IOException
import java.util.Collections
import java.util.Objects.nonNull


open class BalanceActivity : SamouraiActivity() {
    private var txs: MutableList<Tx>? = null
    private var ricochetQueueTask: RicochetQueueTask? = null
    private val balanceViewModel: BalanceViewModel by viewModels()
    private lateinit var binding: ActivityBalanceBinding
    private var menu: Menu? = null
    private val menuTorIcon: ImageView? = null
    private var executeQuitAppProcessStarted = false
    private val uiSemaphore: Semaphore = Semaphore(1)

    private var receiver: BroadcastReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            if (ACTION_INTENT == intent.action) {
                if (binding.progressBar != null) {
                    showProgress()
                }
                val notifTx = intent.getBooleanExtra("notifTx", false)
                val fetch = intent.getBooleanExtra("fetch", false)
                val rbfHash: String?
                val blkHash: String?
                rbfHash = if (intent.hasExtra("rbf")) {
                    intent.getStringExtra("rbf")
                } else {
                    null
                }
                blkHash = if (intent.hasExtra("hash")) {
                    intent.getStringExtra("hash")
                } else {
                    null
                }
                val handler = Handler()
                handler.post {
                    refreshTx(notifTx, false)
                    if (this@BalanceActivity != null) {
                        if (rbfHash != null) {
                            MaterialAlertDialogBuilder(this@BalanceActivity)
                                .setTitle(R.string.app_name)
                                .setMessage(rbfHash + "\n\n" + getString(R.string.rbf_incoming))
                                .setCancelable(true)
                                .setPositiveButton(R.string.yes, DialogInterface.OnClickListener { dialog, whichButton -> doExplorerView(rbfHash) })
                                .setNegativeButton(R.string.no, object : DialogInterface.OnClickListener {
                                    override fun onClick(dialog: DialogInterface, whichButton: Int) {
                                    }
                                }).show()
                        }
                    }
                }
            }
        }
    }
    private var receiverDisplay: BroadcastReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            if (DISPLAY_INTENT == intent.action) {
                updateDisplay(true)
                checkDust()
            }
        }
    }

    private fun checkDust() {
        balanceViewModel.viewModelScope.launch {
            withContext(Dispatchers.Default) {
                val utxos = APIFactory.getInstance(this@BalanceActivity).getUtxos(false)
                val utxoWarnings = arrayListOf<MyTransactionOutPoint>()
                for (utxo in utxos) {
                    val outpoints = utxo.outpoints
                    for (out in outpoints) {
                        val scriptBytes = out.scriptBytes
                        var address: String? = null
                        try {
                            address = if (Bech32Util.getInstance().isBech32Script(Hex.toHexString(scriptBytes))) {
                                Bech32Util.getInstance().getAddressFromScript(Hex.toHexString(scriptBytes))
                            } else {
                                Script(scriptBytes).getToAddress(SamouraiWallet.getInstance().currentNetworkParams).toString()
                            }
                        } catch (e: Exception) {
                        }
                        val path = APIFactory.getInstance(this@BalanceActivity).unspentPaths[address]
                        if (path != null && path.startsWith("M/1/")) {
                            continue
                        }
                        val hash = out.hash.toString()
                        val idx = out.txOutputN
                        val amount = out.value.longValue()
                        val contains = BlockedUTXO.getInstance().contains(hash, idx) || BlockedUTXO.getInstance().containsNotDusted(hash, idx)
                        val containsInPostMix = BlockedUTXO.getInstance().containsPostMix(hash, idx) || BlockedUTXO.getInstance().containsNotDustedPostMix(hash, idx)
                        if (amount < BlockedUTXO.BLOCKED_UTXO_THRESHOLD && !contains && !containsInPostMix) {
                            utxoWarnings.add(out);
//                            BalanceActivity.this.runOnUiThread(new Runnable() {
//                            @Override
                        }
                    }
                }
                if(! utxoWarnings.isEmpty()) {
                    withContext(Dispatchers.Main) {
                        utxoWarnings.forEach {
                            val hash = it.hash.toString()
                            val idx = it.txOutputN
                            val amount = it.value.longValue()
                            var message: String? = this@BalanceActivity.getString(R.string.dusting_attempt)
                            message += "\n\n"
                            message += this@BalanceActivity.getString(R.string.dusting_attempt_amount)
                            message += " "
                            message += FormatsUtil.formatBTC(amount)
                            message += this@BalanceActivity.getString(R.string.dusting_attempt_id)
                            message += " "
                            message += "$hash-$idx"
                            val dlg = MaterialAlertDialogBuilder(this@BalanceActivity)
                                .setTitle(R.string.dusting_tx)
                                .setMessage(message)
                                .setCancelable(false)
                                .setPositiveButton(R.string.dusting_attempt_mark_unspendable) { dialog, whichButton ->
                                    if (account == WhirlpoolMeta.getInstance(this@BalanceActivity).whirlpoolPostmix) {
                                        BlockedUTXO.getInstance().addPostMix(hash, idx, amount)
                                    } else {
                                        BlockedUTXO.getInstance().add(hash, idx, amount)
                                    }
                                    saveState()
                                }.setNegativeButton(R.string.dusting_attempt_ignore) { dialog, whichButton ->
                                    if (account == WhirlpoolMeta.getInstance(this@BalanceActivity).whirlpoolPostmix) {
                                        BlockedUTXO.getInstance().addNotDustedPostMix(hash, idx)
                                    } else {
                                        BlockedUTXO.getInstance().addNotDusted(hash, idx)
                                    }
                                    saveState()
                                }
                            if (!isFinishing) {
                                dlg.show()
                            }
                        }
                    }
                }
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        //Switch themes based on accounts (blue theme for whirlpool account)
        setSwitchThemes(true)
        super.onCreate(savedInstanceState)
        val comeFromPostmix = isFromPostmix()
        binding = ActivityBalanceBinding.inflate(layoutInflater)
        setContentView(binding.root)
        balanceViewModel.setAccount(account)
        if (account == DEPOSIT) {
            val biP47Util = BIP47Util.getInstance(applicationContext)
            biP47Util.payNymLogoLive.observe(this@BalanceActivity) {
                binding.toolbarIcon.setImageBitmap(it)
            }
        }
        makePaynymAvatarCache()
        requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_PORTRAIT
        setSupportActionBar(binding.toolbar)
        binding.rvTxes.layoutManager = LinearLayoutManager(this)
        val drawable = ContextCompat.getDrawable(this, R.drawable.divider_grey)
        binding.rvTxes.addItemDecoration(ItemDividerDecorator(drawable))
        txs = ArrayList()
        /*
        findViewById<View>(R.id.whirlpool_fab).setOnClickListener { view: View? ->
            val intent = Intent(this@BalanceActivity, WhirlpoolHome::class.java)
            startActivity(intent)
            binding.fabMenu.toggle(true)
        }
         */
        binding.sendFab.setOnClickListener(View.OnClickListener { view: View? ->

            val isPostmixAccount = account == POSTMIX

            val activityType =
                if (isPostmixAccount) SendActivity::class.java
                else AccountSelectionActivity::class.java

            val intent = Intent(this@BalanceActivity, activityType)
            intent.putExtra("via_menu", true)
            if (isPostmixAccount) {
                intent.putExtra("_account", account)
            }
            startActivity(intent)
            binding.fabMenu.toggle(true)
        })
        if (!comeFromPostmix) {
            loadBalance()
        }
        binding.receiveFab.setOnClickListener { view: View? ->
            binding.fabMenu.toggle(true)
            val hdw = HD_WalletFactory.getInstance(this@BalanceActivity).get()
            if (hdw != null) {
                val intent = Intent(this@BalanceActivity, ReceiveActivity::class.java)
                startActivity(intent)
            }
        }
        binding.paynymFab.setOnClickListener { view: View? ->
            binding.fabMenu.toggle(true)
            val intent = Intent(this@BalanceActivity, PayNymHome::class.java)
            startActivity(intent)
        }
        binding.txSwipeContainer.setOnRefreshListener(OnRefreshListener {
            doClipboardCheck()
            refreshTx(false, false)
            binding.txSwipeContainer.isRefreshing = false
            showProgress()
        })

        binding.appBar.addOnOffsetChangedListener { appBarLayout, verticalOffset ->
            if (Math.abs(verticalOffset) == appBarLayout.totalScrollRange) {
                binding.utxoIcon.visibility = View.GONE
            } else if (verticalOffset == 0) {
                binding.utxoIcon.visibility = View.VISIBLE
            } else {
                binding.utxoIcon.visibility = View.GONE
            }
        }

        val filter = IntentFilter(ACTION_INTENT)
        LocalBroadcastManager.getInstance(this@BalanceActivity).registerReceiver(receiver, filter)
        val filterDisplay = IntentFilter(DISPLAY_INTENT)
        LocalBroadcastManager.getInstance(this@BalanceActivity).registerReceiver(receiverDisplay, filterDisplay)

        balanceViewModel.viewModelScope.launch(Dispatchers.IO) {
            if (PrefsUtil.getInstance(applicationContext).getValue(PrefsUtil.AUTO_BACKUP, true)) {
                if (!hasPermissions()) askPermission(this@BalanceActivity)
            }
        }

        if (!comeFromPostmix) {
            doFeaturePayNymUpdate()
        }

        if (RicochetMeta.getInstance(this@BalanceActivity).queue.size > 0) {
            if (ricochetQueueTask == null || ricochetQueueTask!!.status == AsyncTask.Status.FINISHED) {
                ricochetQueueTask = RicochetQueueTask()
                ricochetQueueTask!!.executeOnExecutor(AsyncTask.SERIAL_EXECUTOR)
            }
        }
        if (!AppUtil.getInstance(this@BalanceActivity).isClipboardSeen) {
            doClipboardCheck()
        }
        setUpTor()
        initViewModel()
        if (account == DEPOSIT) {
            binding.toolbarIcon.setOnClickListener {
                showToolOptions(it)
            }
            if (! comeFromPostmix && !intent.getBooleanExtra("refresh", false)) {
                Handler(Looper.getMainLooper()).postDelayed({
                    var notifTx = intent.getBooleanExtra("notifTx", false)
                    refreshTx(notifTx, true)
                }, 1100L)
            } else {
                updateDisplay(false)
            }
        } else {
            binding.toolbarIcon.visibility = View.GONE
            binding.toolbar.setTitleMargin(0, 0, 0, 0)
            binding.toolbar.titleMarginEnd = -50
            binding.toolbar.setNavigationIcon(R.drawable.ic_piggy_bank )
            binding.toolbar.setNavigationOnClickListener {
                val intent = Intent(this, BalanceActivity::class.java)
                intent.putExtra("_account", DEPOSIT)
                intent.putExtra("come_from_postmix", true)
                intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_NEW_TASK)
                finish()
                startActivity(intent)
            }
            binding.receiveFab.visibility = View.GONE
            //binding.whirlpoolFab.visibility = View.GONE
            binding.paynymFab.visibility = View.GONE
            Handler(Looper.getMainLooper()).postDelayed({ updateDisplay(true) }, 600L)
        }
        balanceViewModel.loadOfflineData()

        checkDeepLinks()
        doExternalBackUp()

        balanceViewModel.viewModelScope.launch {
            withContext(Dispatchers.Main) {
                askNotificationPermission(this@BalanceActivity)
            }
        }
    }

    private fun showAppUpdate(show: Boolean) {
        if (appUpdateShowed) return
        if (show && nonNull(SamouraiWallet.getInstance().releaseNotes)) {
            AppUtil.getInstance(this).setHasUpdateBeenShown(true)
            appUpdateShowed = true
            val bottomSheetFragment = AppUpdateAvailableBottomSheet(SamouraiWallet.getInstance().releaseNotes.getString("version"))
            bottomSheetFragment.show(supportFragmentManager, bottomSheetFragment.tag)
            return
        }
    }

    private fun loadBalance() {
        balanceViewModel.viewModelScope.launch(Dispatchers.IO) {
            val balanceFormat = PrefsUtil.getInstance(applicationContext).getValue(PrefsUtil.BALANCE_FORMAT, 0)

            val payloadWrapper : MutableList<JSONObject> = Lists.newArrayList();
            val job = balanceViewModel.viewModelScope.launch(Dispatchers.IO) {
                payloadWrapper.add(PayloadUtil.getInstance(this@BalanceActivity).payload)
            }

            balanceViewModel.viewModelScope.launch(Dispatchers.Main) {
                job.invokeOnCompletion { it ->
                    if (it != null) {
                        AppUtil.getInstance(applicationContext).restartApp()
                        Log.e(TAG, "issue on payload loading")
                        it.printStackTrace()
                    } else {
                        val payload = if (payloadWrapper.size == 1) payloadWrapper[0] else null
                        if (account == DEPOSIT &&
                            payload != null &&
                            payload.has("meta") &&
                            payload.getJSONObject("meta").has("prev_balance")) {

                            try {
                                setBalance(payload.getJSONObject("meta").getLong("prev_balance"), balanceFormat)
                            } catch (e: Exception) {
                                Log.e(TAG, "issue on setBalance()", e)
                                setBalance(0L, balanceFormat)
                            }

                        } else {
                            if (account == DEPOSIT) {
                                Log.e(TAG, "issue on payload loading")
                            }
                            setBalance(0L, balanceFormat)
                        }
                    }
                }
            }
        }
    }

    private fun showToolOptions(it: View) {

        balanceViewModel.viewModelScope.launch(Dispatchers.IO) {

            val bitmapImage = BIP47Util.getInstance(applicationContext).payNymLogoLive.value
            var drawable = ContextCompat.getDrawable(this@BalanceActivity, R.drawable.ic_ashigaru_logo)
            var nym = PrefsUtil.getInstance(applicationContext)
                .getValue(PrefsUtil.PAYNYM_BOT_NAME, BIP47Meta.getInstance().getDisplayLabel(BIP47Util.getInstance(applicationContext).paymentCode.toString()))
            if (bitmapImage != null) {
                drawable = BitmapDrawable(resources, bitmapImage)
            }
            if (nym.isNullOrEmpty()) {
                nym = BIP47Meta.getInstance().getDisplayLabel(BIP47Util.getInstance(applicationContext).paymentCode.toString())
            }

            withContext(Dispatchers.Main) {
                val toolWindowSize = applicationContext.resources.displayMetrics.density * 220;
                val popupMenu = popupMenu {
                    fixedContentWidthInPx = toolWindowSize.toInt()
                    style = R.style.Theme_Samourai_Widget_MPM_Menu_Dark
                    section {
                        item {
                            label = nym
                            iconDrawable = drawable
                            iconSize = 34
                            labelColor = ContextCompat.getColor(applicationContext, R.color.white)
                            disableTint = true
                            iconShapeAppearanceModel = ShapeAppearanceModel().toBuilder()
                                .setAllCornerSizes(resources.getDimension(R.dimen.qr_image_corner_radius))
                                .build()
                            callback = {
                                val intent = Intent(this@BalanceActivity, PayNymHome::class.java)
                                startActivity(intent)
                            }
                        }
                        item {
                            label = "Collaborate"
                            iconSize = 18
                            callback = {
                                val intent = Intent(this@BalanceActivity, CollaborateActivity::class.java)
                                startActivity(intent)
                            }
                            icon = R.drawable.ic_connect_without_contact
                        }
                        item {
                            label = "Tools"
                            icon = R.drawable.ic_tools
                            iconSize = 18
                            hasNestedItems
                            callback = {
                                ToolsBottomSheet.showTools(supportFragmentManager)
                            }
                        }
                    }
                    section {

                        item {
                            label = "Pairing"
                            icon = R.drawable.pairing_icon
                            iconSize = 18
                            hasNestedItems
                            callback = {
                                val intent = Intent(this@BalanceActivity, PairingMenuActivity::class.java)
                                startActivity(intent)
                            }
                        }

                        item {
                            label = getString(R.string.action_settings)
                            icon = R.drawable.ic_cog
                            iconSize = 18
                            callback = {
                                TimeOutUtil.getInstance().updatePin()
                                val intent = Intent(this@BalanceActivity, SettingsActivity::class.java)
                                startActivity(intent)
                            }
                        }
                        item {
                            label = "Exit Wallet"
                            iconSize = 18
                            iconColor = ContextCompat.getColor(this@BalanceActivity, R.color.mpm_red)
                            labelColor = ContextCompat.getColor(this@BalanceActivity, R.color.mpm_red)
                            icon = R.drawable.ic_baseline_power_settings_new_24
                            callback = {
                                this@BalanceActivity.onBackPressed()
                            }
                        }
                    }
                }
                popupMenu.show(this@BalanceActivity, it)
            }
        }
    }

    private fun hideProgress() {
        balanceViewModel.viewModelScope.launch(Dispatchers.IO) {
            delay(150L)
            withContext(Dispatchers.Main) {
                uiSemaphore.withPermit {
                    val loading = AppUtil.getInstance(applicationContext).walletLoading.value?:false
                    if (!loading) {
                        val progressIndicator = binding.progressBar
                        if (progressIndicator.isVisible) {
                            progressIndicator.apply {
                                hide()
                            }
                        }
                    }
                }
            }
        }
    }

    private fun showProgress() {
        balanceViewModel.viewModelScope.launch(Dispatchers.IO) {
            delay(150L)
            withContext(Dispatchers.Main) {
                uiSemaphore.withPermit {
                    val loading = AppUtil.getInstance(applicationContext).walletLoading.value?:false
                    if (loading) {
                        val progressIndicator = binding.progressBar
                        if (!progressIndicator.isVisible) {
                            progressIndicator.apply {
                                isIndeterminate = true
                                show()
                            }
                        }
                    }
                }
            }
        }
    }

    private fun checkDeepLinks() {
        val bundle = intent.extras ?: return
        if (bundle.containsKey("pcode") || bundle.containsKey("uri") || bundle.containsKey("amount")) {
            if (bundle.containsKey("uri")) {
                if (bundle.getString("uri")?.startsWith("auth47") == true) {
                    ToolsBottomSheet.showTools(supportFragmentManager, ToolsBottomSheet.ToolType.AUTH47,
                        bundle = Bundle().apply {
                            putString("KEY", bundle.getString("uri"))
                        })
                    return;
                }
                if (bundle.getString("uri")?.startsWith("bitcoin:PM8") == true) {
                    val intent = Intent(this, PayNymDetailsActivity::class.java)
                    intent.putExtra("pcode",
                        StringUtils.substringBetween(
                            bundle.getString("uri"),
                            "bitcoin:",
                            "?"
                        ))
                    startActivity(intent)
                    return
                }
            }
            if (balanceViewModel.balance.value != null)
                bundle.putLong("balance", balanceViewModel.balance.value!!)
            val intent = Intent(this, AccountSelectionActivity::class.java)
            intent.putExtra("_account", account)
            intent.putExtras(bundle)
            startActivity(intent)
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
    }

    private fun initViewModel() {
        val adapter = TxAdapter(applicationContext, ArrayList(), account)
        adapter.setClickListener { position: Int, tx: Tx -> txDetails(tx) }
        binding.rvTxes.adapter = adapter
        val balanceFormat = PrefsUtil.getInstance(applicationContext).getValue(PrefsUtil.BALANCE_FORMAT, 0)
        balanceViewModel.balance.observe(this) { balance: Long? ->
            if (balance == null || balance <= 0L) {
                setBalance(0L, balanceFormat)
            } else {
                setBalance(balance, balanceFormat)
            }
        }
        adapter.setTxes(balanceViewModel.txs.value)
        setBalance(balanceViewModel.balance.value, balanceFormat)
        balanceViewModel.formatBalance.observe(this) { state: Int? ->
            var format = 0
            if (state != null) {
                format = state
            }
            setBalance(balanceViewModel.balance.value, format)
            adapter.notifyDataSetChanged()
        }
        balanceViewModel.txs.observe(this) {
            list -> adapter.setTxes(list)
        }
        binding.toolbarLayout.setOnClickListener { v: View? ->
            val newFormat = balanceViewModel.switchBalanceFormat()
            PrefsUtil.getInstance(this@BalanceActivity).setValue(PrefsUtil.BALANCE_FORMAT, newFormat)
        }
        binding.toolbarLayout.setOnLongClickListener {
            val intent = Intent(this@BalanceActivity, UTXOSActivity::class.java)
            intent.putExtra("_account", account)
            startActivityForResult(intent, UTXO_REQUESTCODE)
            false
        }

        binding.utxoIcon.setOnClickListener {
            val intent = Intent(this@BalanceActivity, UTXOSActivity::class.java)
            intent.putExtra("_account", account)
            startActivityForResult(intent, UTXO_REQUESTCODE)
        }

        binding.utxoIcon.setOnLongClickListener {
            if (SamouraiWallet.getInstance().isTestNet) {
                SamouraiWallet.setMockFee( !SamouraiWallet.isMockFee() )
                refreshTx(false, false)
                binding.txSwipeContainer.isRefreshing = false
                showProgress()
            }
            false
        }
    }

    private fun setBalance(balance: Long?, format: Int) {
        if (balance == null) {
            return
        }
        balanceViewModel.viewModelScope.launch(Dispatchers.Main) {
            if (supportActionBar != null) {
                TransitionManager.beginDelayedTransition(binding.toolbarLayout, ChangeBounds())
                val displayAmount = if (format == 1) FormatsUtil.formatSats(balance) else if (format == 2) "**********" else FormatsUtil.formatBTC(balance)
                binding.toolbar.title = displayAmount
                title = displayAmount
                binding.toolbarLayout.title = displayAmount
            }
        }
    }

    public override fun onResume() {
        super.onResume()
        executeQuitAppProcessStarted = false;

        // useful to display the freshly added notes from TxDetailsScreen
        binding.rvTxes.adapter?.notifyDataSetChanged()

        showProgress()
        AppUtil.getInstance(applicationContext).walletLoading.observe(this) {
            if (it) {
                showProgress()
            } else {
                hideProgress()
            }
        }
        if (! isFromPostmix() && intent.getBooleanExtra("refresh", false)) {
            Handler(Looper.getMainLooper()).postDelayed({
                refreshTx(false, false)
            }, 1100L)
        }

        AppUtil.getInstance(applicationContext).hasUpdateBeenShown.observe(this) {
            showAppUpdate(!it)
        }

        AppUtil.getInstance(this@BalanceActivity).checkTimeOut()
        try {
            val balanceFormat = PrefsUtil.getInstance(applicationContext).getValue(PrefsUtil.BALANCE_FORMAT, 0)
            if (balanceFormat != balanceViewModel.formatBalance.value) {
                balanceViewModel.switchBalanceFormat()
            }
        } catch (e: Exception) {
            LogUtil.error(TAG, e)
        }
    }

    fun createTag(text: String?): View {
        val scale = resources.displayMetrics.density
        val lparams = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT
        )
        val textView = TextView(applicationContext)
        textView.text = text
        textView.setTextColor(ContextCompat.getColor(applicationContext, R.color.white))
        textView.layoutParams = lparams
        textView.setBackgroundResource(R.drawable.tag_round_shape)
        textView.setPadding((8 * scale + 0.5f).toInt(), (6 * scale + 0.5f).toInt(), (8 * scale + 0.5f).toInt(), (6 * scale + 0.5f).toInt())
        textView.typeface = Typeface.DEFAULT_BOLD
        textView.setTextSize(TypedValue.COMPLEX_UNIT_SP, 11f)
        return textView
    }

    private fun makePaynymAvatarCache() {
        try {
            balanceViewModel.viewModelScope.launch(Dispatchers.IO) {

                if (PrefsUtil.getInstance(applicationContext).getValue(PrefsUtil.PAYNYM_BOT_NAME, "").isNullOrEmpty()
                    && PrefsUtil.getInstance(applicationContext).getValue(PrefsUtil.PAYNYM_CLAIMED,false))  {
                    val strPaymentCode = BIP47Util.getInstance(application).paymentCode.toString()
                    val apiService = PayNymApiService.getInstance(strPaymentCode, getApplication());
                    balanceViewModel.viewModelScope.launch(Dispatchers.IO) {
                        try {
                            val response = apiService.getNymInfo()
                            if (response.isSuccessful) {
                                val responseJson = response.body?.string()
                                if (responseJson != null) {
                                    val jsonObject = JSONObject(responseJson)
                                    val nym = Gson().fromJson(jsonObject.toString(), NymResponse::class.java);
                                    PrefsUtil.getInstance(applicationContext).setValue(PrefsUtil.PAYNYM_BOT_NAME, nym.nymName)

                                } else
                                    throw Exception("Invalid response ")
                            }
                        } catch (_: Exception) {

                        }
                    }
                }

                if (!BIP47Util.getInstance(applicationContext).avatarImage().exists()) {
                    loadAvatar()
                } else {
                    balanceViewModel.viewModelScope.launch(Dispatchers.IO) {
                        val bitmap = BitmapFactory.decodeFile(BIP47Util.getInstance(applicationContext).avatarImage().path)
                        if (bitmap != null) {
                            BIP47Util.getInstance(applicationContext).setAvatar(bitmap)
                        } else {
                            loadAvatar()
                        }
                    }
                }

                val paymentCodes = ArrayList(BIP47Meta.getInstance().getSortedByLabels(false, true))
                if (!AppUtil.getInstance(this@BalanceActivity).isOfflineMode) {
                    for (code in paymentCodes) {
                        Piccolo.get()
                            .load(PayNymApiService.PAYNYM_API + code + "/avatar")
                            .fetch(object : Callback {
                                override fun onSuccess() {
                                    /*NO OP*/
                                }

                                override fun onError(e: Exception) {
                                    /*NO OP*/
                                }
                            })
                    }
                }
            }

        } catch (ignored: Exception) {
        }
    }

    private fun loadAvatar() {
        BIP47Util.getInstance(applicationContext).fetchBotImage()
            .subscribe()
            .apply {
                registerDisposable(this)
            }
    }

    public override fun onDestroy() {
        LocalBroadcastManager.getInstance(this@BalanceActivity).unregisterReceiver(receiver)
        LocalBroadcastManager.getInstance(this@BalanceActivity).unregisterReceiver(receiverDisplay)

        if (PrefsUtil.getInstance(this.application).getValue(StealthModeController.PREF_ENABLED, false)) {
            StealthModeController.enableStealth(applicationContext)
        }
        super.onDestroy()
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menuInflater.inflate(R.menu.main, menu)
        menu.findItem(R.id.action_mock_fees).isVisible = false
        menu.findItem(R.id.action_refresh).isVisible = false
        menu.findItem(R.id.action_share_receive).isVisible = false
        menu.findItem(R.id.action_ricochet).isVisible = false
        menu.findItem(R.id.action_empty_ricochet).isVisible = false
        menu.findItem(R.id.action_sign).isVisible = false
        menu.findItem(R.id.action_fees).isVisible = false
        menu.findItem(R.id.action_batch).isVisible = false
        menu.findItem(R.id.action_backup).isVisible = false
        menu.findItem(R.id.action_utxo).isVisible = false
        WhirlpoolMeta.getInstance(applicationContext)
        if (account == POSTMIX) {
            menu.findItem(R.id.action_network_dashboard).isVisible = false
            menu.findItem(R.id.action_postmix_balance).isVisible = false
            val item = menu.findItem(R.id.action_menu_account)
            item.actionView = createTag(" POST-MIX ")
            item.isVisible = true
            item.setShowAsAction(MenuItem.SHOW_AS_ACTION_ALWAYS)
        }
        this.menu = menu
        return super.onCreateOptionsMenu(menu)
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        val id = item.itemId
        if (id == android.R.id.home) {
            finish()
            return super.onOptionsItemSelected(item)
        }
        if (id == R.id.action_mock_fees) {
            SamouraiWallet.setMockFee( !SamouraiWallet.isMockFee() )
            refreshTx(false, false)
            binding.txSwipeContainer.isRefreshing = false
            showProgress()
            return super.onOptionsItemSelected(item)
        }
        if (id == R.id.action_postmix_balance) {
            val intent = Intent(this, BalanceActivity::class.java)
            intent.putExtra("_account", POSTMIX)
            intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_NEW_TASK)
            finish()
            startActivity(intent)
            return super.onOptionsItemSelected(item)
        }

        // noinspection SimplifiableIfStatement
        if (id == R.id.action_network_dashboard) {
            startActivity(Intent(this, NetworkDashboard::class.java))
        } // noinspection SimplifiableIfStatement
        /*
        if (id == R.id.action_support) {
            ActivityHelper.launchSupportPageInBrowser(this, SamouraiTorManager.isConnected())
        } else */
        if (id == R.id.action_utxo) {
            doUTXO()
        } else if (id == R.id.action_backup) {
            if (SamouraiWallet.getInstance().hasPassphrase(this@BalanceActivity)) {
                if (HD_WalletFactory.getInstance(this@BalanceActivity).get() != null && SamouraiWallet.getInstance().hasPassphrase(this@BalanceActivity)) {
                    doBackup(HD_WalletFactory.getInstance(this@BalanceActivity).get().passphrase)
                }
            } else {
                val builder = MaterialAlertDialogBuilder(this)
                builder.setTitle(R.string.enter_backup_password)
                val view = layoutInflater.inflate(R.layout.password_input_dialog_layout, null)
                val password = view.findViewById<EditText>(R.id.restore_dialog_password_edittext)
                val message = view.findViewById<TextView>(R.id.dialogMessage)
                message.setText(R.string.backup_password)
                builder.setPositiveButton(R.string.confirm) { dialog: DialogInterface, which: Int ->
                    val pw = password.text.toString()
                    if (pw.length >= AppUtil.MIN_BACKUP_PW_LENGTH && pw.length <= AppUtil.MAX_BACKUP_PW_LENGTH) {
                        doBackup(pw)
                    } else {
                        Toast.makeText(applicationContext, R.string.password_error, Toast.LENGTH_SHORT).show()
                    }
                    dialog.dismiss()
                }
                builder.setNegativeButton(R.string.cancel) { dialog: DialogInterface, which: Int -> dialog.dismiss() }
                builder.setView(view)
                builder.show()
            }
        } else if (id == R.id.action_scan_qr) {
            doScan()
        } else {
        }
        return super.onOptionsItemSelected(item)
    }

    private fun setUpTor() {
        SamouraiTorManager.getTorStateLiveData().observe(this) { torState: TorState ->

            if (torState.state == EnumTorState.ON) {
                balanceViewModel.viewModelScope.launch(Dispatchers.IO) {
                    PrefsUtil.getInstance(this@BalanceActivity).setValue(PrefsUtil.ENABLE_TOR, true)
                    balanceViewModel.viewModelScope.launch(Dispatchers.Main) {
                        binding.progressBar.visibility = View.INVISIBLE
                        menuTorIcon?.setImageResource(R.drawable.tor_on)
                    }
                }

            } else if (torState.state == EnumTorState.STARTING) {
                binding.progressBar.visibility = View.VISIBLE
                menuTorIcon?.setImageResource(R.drawable.tor_on)

            } else {
                balanceViewModel.viewModelScope.launch(Dispatchers.IO) {
                    if (torState.state == EnumTorState.OFF && !executeQuitAppProcessStarted) {
                        PrefsUtil.getInstance(this@BalanceActivity).setValue(PrefsUtil.ENABLE_TOR, false)
                    }
                    balanceViewModel.viewModelScope.launch(Dispatchers.Main) {
                        binding.progressBar.visibility = View.INVISIBLE
                        menuTorIcon?.setImageResource(R.drawable.tor_off)
                    }
                }
            }
        }
    }

    public override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        onActivityResult(requestCode, resultCode, data, application)
        if (resultCode == RESULT_OK && requestCode == SCAN_COLD_STORAGE) {
            if (data?.getStringExtra(ZBarConstants.SCAN_RESULT) != null) {
                val strResult = data.getStringExtra(ZBarConstants.SCAN_RESULT)
                doPrivKey(strResult)
            }
        } else if (resultCode == RESULT_CANCELED && requestCode == SCAN_COLD_STORAGE) {
        } else if (resultCode == RESULT_OK && requestCode == SCAN_QR) {

            if (data?.getStringExtra(ZBarConstants.SCAN_RESULT) != null) {
                val strResult = data.getStringExtra(ZBarConstants.SCAN_RESULT)
                val params = SamouraiWallet.getInstance().currentNetworkParams
                val privKeyReader = PrivKeyReader(strResult, params)
                try {
                    if (privKeyReader.format != null) {
                        doPrivKey(strResult!!.trim { it <= ' ' })
                    } else if (strResult?.lowercase()?.startsWith(Auth47ViewModel.AUTH_SCHEME.lowercase()) == true) {
                        ToolsBottomSheet.showTools(supportFragmentManager, ToolsBottomSheet.ToolType.AUTH47,
                            bundle = Bundle().apply {
                                putString("KEY", strResult)
                            })
                    } else if (Cahoots.isCahoots(strResult!!.trim { it <= ' ' })) {
                        val cahootIntent = ManualCahootsActivity.createIntentResume(this, account, strResult.trim { it <= ' ' })
                        startActivity(cahootIntent)
                    } else if (isPSBT(strResult.trim { it <= ' ' })) {
                        PSBTUtil.getInstance(this@BalanceActivity).doPSBT(strResult.trim { it <= ' ' })
                    } else if (DojoUtil.getInstance(this@BalanceActivity).isValidPairingPayload(strResult.trim { it <= ' ' })) {
                        val intent = Intent(this@BalanceActivity, NetworkDashboard::class.java)
                        intent.putExtra("params", strResult.trim { it <= ' ' })
                        startActivity(intent)
                    } else {
                        val intent = Intent(this@BalanceActivity, AccountSelectionActivity::class.java)
                        intent.putExtra("uri", strResult.trim { it <= ' ' })
                        intent.putExtra("_account", account)
                        startActivity(intent)
                    }
                } catch (e: Exception) {
                }
            }
        }
        if (resultCode == RESULT_OK && requestCode == UTXO_REQUESTCODE) {
            refreshTx(false, false)
            showProgress()
        } else {
        }
    }

    override fun onBackPressed() {
        if (account == DEPOSIT || account == POSTMIX) {
            val builder = MaterialAlertDialogBuilder(this)
            builder.setMessage(R.string.ask_you_sure_exit)
            val alert = builder.create()
            alert.setButton(AlertDialog.BUTTON_POSITIVE, getString(R.string.yes)) { dialog: DialogInterface?, id: Int ->
                executeQuitAppProcesses()
            }
            alert.setButton(AlertDialog.BUTTON_NEGATIVE, getString(R.string.no)) { dialog: DialogInterface, id: Int -> dialog.dismiss() }
            alert.show()
        } else {
            super.onBackPressed()
        }
    }

    private fun doExternalBackUp() {
        balanceViewModel.viewModelScope.launch(Dispatchers.IO) {
            try {
                if (hasPermissions() && PrefsUtil.getInstance(application).getValue(PrefsUtil.AUTO_BACKUP, false)) {
                    val disposable = Observable.fromCallable {
                        PayloadUtil.getInstance(this@BalanceActivity).saveWalletToJSON(CharSequenceX(AccessFactory.getInstance(this@BalanceActivity).guid + AccessFactory.getInstance(this@BalanceActivity).pin))
                        true
                    }.subscribeOn(Schedulers.io())
                        .observeOn(AndroidSchedulers.mainThread()).subscribe({ t: Boolean? -> }) { throwable: Throwable? -> LogUtil.error(TAG, throwable) }
                    registerDisposable(disposable)
                }
            } catch (exception: Exception) {
                LogUtil.error(TAG, exception)
            }
        }
    }

    private fun executeQuitAppProcesses() {

        executeQuitAppProcessStarted = true;
        appUpdateShowed = false;

        try {
            if (hasPermissions() &&
                PrefsUtil.getInstance(application).getValue(PrefsUtil.AUTO_BACKUP, false)) {

                val disposable = Observable.fromCallable {
                    PayloadUtil.getInstance(this@BalanceActivity)
                        .saveWalletToJSON(CharSequenceX(
                            AccessFactory.getInstance(this@BalanceActivity).guid +
                                AccessFactory.getInstance(this@BalanceActivity).pin))
                    true
                }.subscribeOn(Schedulers.io())
                    .observeOn(AndroidSchedulers.mainThread())
                    .subscribe({ t: Boolean? ->
                        stopingServices()
                    }) { throwable: Throwable? ->
                        LogUtil.error(TAG, throwable)
                        stopingServices()
                    }
                registerDisposable(disposable)
            } else {
                stopingServices()
            }
        } catch (exception: Exception) {
            LogUtil.error(TAG, exception)
            stopingServices()
        }
    }

    private fun stopingServices() {
        WalletUtil.stop(this);
        super.onBackPressed()
    }

    private fun updateDisplay(fromRefreshService: Boolean) {
        val txDisposable = getTxes(account)
            .subscribeOn(Schedulers.io())
            .observeOn(AndroidSchedulers.mainThread())
            .subscribe { txes: List<Tx>?, throwable: Throwable? ->
                throwable?.printStackTrace()
                if (txes != null) {
                    if (txes.isNotEmpty()) {
                        balanceViewModel.setTx(txes)
                    } else {
                        if (balanceViewModel.txs.value != null && balanceViewModel.txs.value!!.size == 0) {
                            balanceViewModel.setTx(txes)
                        }
                    }
                    Collections.sort(txes, TxMostRecentDateComparator())
                    txs!!.clear()
                    txs!!.addAll(txes)
                }
                if (binding.progressBar.visibility == View.VISIBLE &&
                    fromRefreshService &&
                    !(AppUtil.getInstance(applicationContext).walletLoading.value?:false)) {

                    hideProgress()
                }
            }
        val balanceDisposable = getBalance(account)
            .subscribeOn(Schedulers.io())
            .observeOn(AndroidSchedulers.mainThread())
            .subscribe { balance: Long?, throwable: Throwable? ->
                throwable?.printStackTrace()
                balanceViewModel.postNewBalance(balance)
            }
        registerDisposable(balanceDisposable)
        registerDisposable(txDisposable)
        //        displayBalance();
//        txAdapter.notifyDataSetChanged();
    }

    private fun getTxes(account: Int): Single<List<Tx>> {
        return Single.fromCallable {
            var loadedTxes: List<Tx> = ArrayList()
            if (account == 0) {
                loadedTxes = APIFactory.getInstance(this@BalanceActivity).allXpubTxs
            } else if (account == WhirlpoolMeta.getInstance(applicationContext).whirlpoolPostmix) {
                loadedTxes = APIFactory.getInstance(this@BalanceActivity).allPostMixTxs
            }
            loadedTxes
        }
    }

    private fun getBalance(account: Int): Single<Long> {
        return Single.fromCallable {
            var loadedBalance = 0L
            if (account == 0) {
                loadedBalance = APIFactory.getInstance(this@BalanceActivity).xpubBalance
            } else if (account == WhirlpoolMeta.getInstance(applicationContext).whirlpoolPostmix) {
                loadedBalance = APIFactory.getInstance(this@BalanceActivity).xpubPostMixBalance
            }
            loadedBalance
        }
    }

    private fun doSettings() {
        TimeOutUtil.getInstance().updatePin()
        val intent = Intent(this@BalanceActivity, SettingsActivity::class.java)
        startActivity(intent)
    }

    var utxoListResult = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) {
        run {
            showProgress()
            refreshTx(false, false)
        }
    }

    private fun doUTXO() {
        val intent = Intent(this@BalanceActivity, UTXOSActivity::class.java)
        intent.putExtra("_account", account)
        utxoListResult.launch(intent)
    }

    private fun doScan() {
        val cameraFragmentBottomSheet = ScanFragment()
        cameraFragmentBottomSheet.show(supportFragmentManager, cameraFragmentBottomSheet.tag)
        cameraFragmentBottomSheet.setOnScanListener { code ->
            cameraFragmentBottomSheet.dismissAllowingStateLoss()
            val params = SamouraiWallet.getInstance().currentNetworkParams
            val privKeyReader = PrivKeyReader(code, params)
            try {
                when {
                    FormatsUtil.getInstance().isValidPaymentCode(code) -> {
                        val intent = Intent(this, PayNymDetailsActivity::class.java)
                        intent.putExtra("pcode",code);
                        startActivity(intent);
                    }
                    canParseAsBatchSpend(code) -> {
                        launchBatchSpend(code)
                    }
                    privKeyReader.format != null -> {
                        doPrivKey(code.trim { it <= ' ' })
                    }
                    code.lowercase().startsWith(Auth47ViewModel.AUTH_SCHEME) -> {
                        ToolsBottomSheet.showTools(supportFragmentManager, ToolsBottomSheet.ToolType.AUTH47,
                            bundle = Bundle().apply {
                                putString("KEY", code)
                            })
                    }
                    Cahoots.isCahoots(code.trim { it <= ' ' }) -> {
                        val cahootIntent = ManualCahootsActivity.createIntentResume(this, account, code.trim { it <= ' ' })
                        startActivity(cahootIntent)
                    }
                    isPSBT(code.trim { it <= ' ' }) -> {
                        ToolsBottomSheet.showTools(supportFragmentManager, ToolsBottomSheet.ToolType.PSBT,
                            bundle = Bundle().apply {
                                putString("KEY", code)
                            })
                    }
                    DojoUtil.getInstance(this@BalanceActivity).isValidPairingPayload(code.trim { it <= ' ' }) -> {
                        val intent = Intent(this@BalanceActivity, NetworkDashboard::class.java)
                        intent.putExtra("params", code.trim { it <= ' ' })
                        startActivity(intent)
                    }
                    else -> {

                        val isPostmixAccount = account == POSTMIX

                        val activityType =
                            if (isPostmixAccount) SendActivity::class.java
                            else AccountSelectionActivity::class.java

                        val intent = Intent(this@BalanceActivity, activityType)
                        intent.putExtra("uri", code.trim { it <= ' ' })
                        if (isPostmixAccount) {
                            intent.putExtra("_account", account)
                        }
                        startActivity(intent)
                    }
                }
            } catch (e: Exception) {
            }
        }
    }

    private fun launchBatchSpend(inputBatchSpendAsJson: String) {
        val intent = Intent(this@BalanceActivity, AccountSelectionActivity::class.java)
        intent.putExtra("inputBatchSpend", inputBatchSpendAsJson)
        startActivity(intent)
    }

    private fun doSweepViaScan() {
        val cameraFragmentBottomSheet = CameraFragmentBottomSheet()
        cameraFragmentBottomSheet.show(supportFragmentManager, cameraFragmentBottomSheet.tag)
        cameraFragmentBottomSheet.setQrCodeScanListener { code: String ->
            cameraFragmentBottomSheet.dismissAllowingStateLoss()
            val params = SamouraiWallet.getInstance().currentNetworkParams
            val privKeyReader = PrivKeyReader(code, params)
            try {
                when {
                    privKeyReader.format != null -> {
                        doPrivKey(code.trim { it <= ' ' })
                    }
                    Cahoots.isCahoots(code.trim { it <= ' ' }) -> {
                        val cahootIntent = ManualCahootsActivity.createIntentResume(this, account, code.trim { it <= ' ' })
                        startActivity(cahootIntent)
                    }
                    isPSBT(code.trim { it <= ' ' }) -> {
                        PSBTUtil.getInstance(this@BalanceActivity).doPSBT(code.trim { it <= ' ' })
                    }
                    DojoUtil.getInstance(this@BalanceActivity).isValidPairingPayload(code.trim { it <= ' ' }) -> {
                        Toast.makeText(this@BalanceActivity, "Samourai Dojo full node coming soon.", Toast.LENGTH_SHORT).show()
                    }
                    else -> {
                        val intent = Intent(this@BalanceActivity, AccountSelectionActivity::class.java)
                        intent.putExtra("uri", code.trim { it <= ' ' })
                        intent.putExtra("_account", account)
                        startActivity(intent)
                    }
                }
            } catch (e: Exception) {
            }
        }
    }

    private fun doPrivKey(data: String?) {

        val params = SamouraiWallet.getInstance().currentNetworkParams
        var privKeyReader: PrivKeyReader? = null
        var format: String? = null
        try {
            privKeyReader = PrivKeyReader(data, params)
            format = privKeyReader.format
        } catch (e: Exception) {
            Toast.makeText(this@BalanceActivity, e.message, Toast.LENGTH_SHORT).show()
            return
        }
        if (format != null) {
            ToolsBottomSheet.showTools(supportFragmentManager, ToolsBottomSheet.ToolType.SWEEP,
                bundle = Bundle().apply {
                    putString("KEY", data)
                })
        } else {
            Toast.makeText(this@BalanceActivity, R.string.cannot_recognize_privkey, Toast.LENGTH_SHORT).show()
        }
    }

    private fun doBackup(passphrase: String) {
        val export_methods = arrayOfNulls<String>(2)
        export_methods[0] = getString(R.string.export_to_clipboard)
        export_methods[1] = getString(R.string.export_to_email)
        MaterialAlertDialogBuilder(this@BalanceActivity)
            .setTitle(R.string.options_export)
            .setSingleChoiceItems(export_methods, 0, DialogInterface.OnClickListener { dialog, which ->
                try {
                    PayloadUtil.getInstance(this@BalanceActivity).saveWalletToJSON(CharSequenceX(AccessFactory.getInstance(this@BalanceActivity).guid + AccessFactory.getInstance(this@BalanceActivity).pin))
                } catch (ioe: IOException) {
                } catch (je: JSONException) {
                } catch (de: DecryptionException) {
                } catch (mle: MnemonicLengthException) {
                }
                var encrypted: String? = null
                try {
                    encrypted = AESUtil.encryptSHA256(PayloadUtil.getInstance(this@BalanceActivity).payload.toString(), CharSequenceX(passphrase))
                } catch (e: Exception) {
                    Toast.makeText(this@BalanceActivity, e.message, Toast.LENGTH_SHORT).show()
                } finally {
                    if (encrypted == null) {
                        Toast.makeText(this@BalanceActivity, R.string.encryption_error, Toast.LENGTH_SHORT).show()
                        return@OnClickListener
                    }
                }
                val obj = PayloadUtil.getInstance(this@BalanceActivity).putPayload(encrypted, true)
                if (which == 0) {
                    val clipboard = getSystemService(CLIPBOARD_SERVICE) as ClipboardManager
                    var clip: ClipData? = null
                    clip = ClipData.newPlainText("Wallet backup", obj.toString())
                    clipboard.setPrimaryClip(clip)
                    Toast.makeText(this@BalanceActivity, R.string.copied_to_clipboard, Toast.LENGTH_SHORT).show()
                } else {
                    val email = Intent(Intent.ACTION_SEND)
                    email.putExtra(Intent.EXTRA_SUBJECT, "Ashigaru backup")
                    email.putExtra(Intent.EXTRA_TEXT, obj.toString())
                    email.type = "message/rfc822"
                    startActivity(Intent.createChooser(email, getText(R.string.choose_email_client)))
                }
                dialog.dismiss()
            }
            ).show()
    }

    private fun doClipboardCheck() {
        val clipboard = this@BalanceActivity.getSystemService(CLIPBOARD_SERVICE) as ClipboardManager
        if (clipboard.hasPrimaryClip()) {
            val clip = clipboard.primaryClip
            val item = clip!!.getItemAt(0)
            if (item.text != null) {
                val text = item.text.toString()
                val s = text.split("\\s+").toTypedArray()
                try {
                    for (i in s.indices) {
                        val params = SamouraiWallet.getInstance().currentNetworkParams
                        val privKeyReader = PrivKeyReader(s[i], params)
                        if (privKeyReader.format != null &&
                            (privKeyReader.format == PrivKeyReader.WIF_COMPRESSED || privKeyReader.format == PrivKeyReader.WIF_UNCOMPRESSED || privKeyReader.format == PrivKeyReader.BIP38 ||
                                    FormatsUtil.getInstance().isValidXprv(s[i]))
                        ) {
                            MaterialAlertDialogBuilder(this@BalanceActivity)
                                .setTitle(R.string.app_name)
                                .setMessage(R.string.privkey_clipboard)
                                .setCancelable(false)
                                .setPositiveButton(R.string.yes) { _, _ -> clipboard.setPrimaryClip(ClipData.newPlainText("", "")) }.setNegativeButton(R.string.no) { _, _ -> }.show()
                        }
                    }
                } catch (e: Exception) {
                }
            }
        }
    }

    private fun refreshTx(notifTx: Boolean, launch: Boolean) {
        if (AppUtil.getInstance(this@BalanceActivity).isOfflineMode) {
            Toast.makeText(this@BalanceActivity, R.string.in_offline_mode, Toast.LENGTH_SHORT).show()
            /*
            CoordinatorLayout coordinatorLayout = new CoordinatorLayout(BalanceActivity.this);
            Snackbar snackbar = Snackbar.make(coordinatorLayout, R.string.in_offline_mode, Snackbar.LENGTH_LONG);
            snackbar.show();
            */
        }

        balanceViewModel.viewModelScope.launch {
            withContext(Dispatchers.IO) {
                async {
                    WalletRefreshUtil.refreshWallet(
                        notifTx = notifTx,
                        launch = launch,
                        context = applicationContext)
                }
            }
        }
//
//        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
//            startForegroundService(intent);
//        } else {
//            startService(intent);
//        }
    }

    private fun doExplorerView(strHash: String?) {
        if (strHash != null) {
            val blockExplorer = BlockExplorerUtil.getInstance().getUri(true)
            val blockExplorerURL = PrefsUtil.getInstance(applicationContext).getValue(PrefsUtil.BLOCK_EXPLORER_URL, "") + "/tx/"
            val browserIntent = Intent(Intent.ACTION_VIEW, Uri.parse(blockExplorerURL + strHash))
            startActivity(browserIntent)
        }
    }

    private fun txDetails(tx: Tx) {
        if (account == WhirlpoolMeta.getInstance(applicationContext).whirlpoolPostmix && tx.amount == 0.0) {
            return
        }
        val txIntent = Intent(this, TxDetailsActivity::class.java)
        txIntent.putExtra("TX", tx.toJSON().toString())
        txIntent.putExtra("_account", account)
        startActivity(txIntent)
    }

    private inner class RicochetQueueTask : AsyncTask<String?, Void?, String>() {

        override fun onPostExecute(result: String) {
        }

        override fun onPreExecute() {
        }

        override fun doInBackground(vararg params: String?): String {
            if (RicochetMeta.getInstance(this@BalanceActivity).queue.size > 0) {
                var count = 0
                val itr = RicochetMeta.getInstance(this@BalanceActivity).iterator
                while (itr.hasNext()) {
                    if (count == 3) {
                        break
                    }
                    try {
                        val jObj = itr.next()
                        val jHops = jObj.getJSONArray("hops")
                        if (jHops.length() > 0) {
                            val jHop = jHops.getJSONObject(jHops.length() - 1)
                            val txHash = jHop.getString("hash")
                            val txObj = APIFactory.getInstance(this@BalanceActivity).getTxInfo(txHash)
                            if (txObj != null && txObj.has("block_height") && txObj.getInt("block_height") != -1) {
                                itr.remove()
                                count++
                            }
                        }
                    } catch (je: JSONException) {
                    }
                }
            }
            if (RicochetMeta.getInstance(this@BalanceActivity).staggered.size > 0) {
                var count = 0
                val staggered = RicochetMeta.getInstance(this@BalanceActivity).staggered
                val _staggered: MutableList<JSONObject> = ArrayList()
                for (jObj in staggered) {
                    if (count == 3) {
                        break
                    }
                    try {
                        val jHops = jObj.getJSONArray("script")
                        if (jHops.length() > 0) {
                            val jHop = jHops.getJSONObject(jHops.length() - 1)
                            val txHash = jHop.getString("tx")
                            val txObj = APIFactory.getInstance(this@BalanceActivity).getTxInfo(txHash)
                            if (txObj != null && txObj.has("block_height") && txObj.getInt("block_height") != -1) {
                                count++
                            } else {
                                _staggered.add(jObj)
                            }
                        }
                    } catch (je: JSONException) {
                    } catch (cme: ConcurrentModificationException) {
                    }
                }
            }
            return "OK"
        }
    }

    private fun doFeaturePayNymUpdate() {
        balanceViewModel.viewModelScope.launch(Dispatchers.IO) {
            if (PrefsUtil.getInstance(this@BalanceActivity).getValue(PrefsUtil.PAYNYM_CLAIMED, false) &&
                !PrefsUtil.getInstance(this@BalanceActivity).getValue(PrefsUtil.PAYNYM_FEATURED_SEGWIT, false)) {
                try {
                    executeFeaturePayNymUpdate(this@BalanceActivity)
                    Log.i(TAG, "executeFeaturePayNymUpdate: Feature update complete")
                } catch (e : Exception) {
                    Log.i(TAG, "executeFeaturePayNymUpdate: Feature update Fail")
                }
            }
        }
    }

    private fun isFromPostmix() = intent.getBooleanExtra("come_from_postmix", false)

    companion object {
        private const val SCAN_COLD_STORAGE = 2011
        private const val SCAN_QR = 2012
        private const val UTXO_REQUESTCODE = 2012
        private const val TAG = "BalanceActivity"
        const val ACTION_INTENT = "com.samourai.wallet.BalanceFragment.REFRESH"
        const val DISPLAY_INTENT = "com.samourai.wallet.BalanceFragment.DISPLAY"

        public var appUpdateShowed : Boolean = false
    }
}