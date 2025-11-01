package com.samourai.wallet.onboard

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.core.content.res.ResourcesCompat
import androidx.lifecycle.Observer
import androidx.lifecycle.viewModelScope
import com.samourai.wallet.R
import com.samourai.wallet.SamouraiWallet
import com.samourai.wallet.access.AccessFactory
import com.samourai.wallet.databinding.ActivitySetDojoBinding
import com.samourai.wallet.fragments.CameraFragmentBottomSheet
import com.samourai.wallet.network.dojo.DojoUtil
import com.samourai.wallet.payload.PayloadUtil
import com.samourai.wallet.tor.EnumTorState
import com.samourai.wallet.tor.SamouraiTorManager
import com.samourai.wallet.tor.TorState
import com.samourai.wallet.util.CharSequenceX
import com.samourai.wallet.util.PrefsUtil
import com.samourai.wallet.util.TimeOutUtil
import com.samourai.wallet.util.tech.AppUtil
import com.samourai.wallet.util.tech.askNotificationPermission
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import kotlin.properties.Delegates


class SetDojoActivity : AppCompatActivity() {

    private lateinit var binding: ActivitySetDojoBinding
    private var isOffline by Delegates.notNull<Boolean>()
    private val setUpWalletViewModel: SetUpWalletViewModel by viewModels()
    private var activeColor = 0
    private var disabledColor: Int = 0
    private var waiting: Int = 0
    private lateinit var dojoURL: String
    private lateinit var explorerURL: String
    private lateinit var apiKey: String

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySetDojoBinding.inflate(layoutInflater)
        setContentView(binding.root)
        window.statusBarColor = ContextCompat.getColor(this, R.color.networking);

        if(intent.hasExtra("dojoURL")) {
            doDojoFromBackup()
        }

        isOffline = AppUtil.getInstance(getApplicationContext()).isOfflineMode()
        AppUtil.getInstance(applicationContext).offlineStateLive().observe(
            this
        ) { aBoolean: Boolean? -> isOffline = aBoolean!! }



        SamouraiTorManager.start()
        activeColor = ContextCompat.getColor(this, R.color.green_ui_2)
        disabledColor = ContextCompat.getColor(this, R.color.disabledRed)
        waiting = ContextCompat.getColor(this, R.color.warning_yellow)

        SamouraiTorManager.getTorStateLiveData().observe(this) {
            setTorState(it)
        }

        if (isOffline) {
            enableOfflineMode(true)
        }
        else {
            SamouraiTorManager.start()
        }

        binding.changeDojoCredsBtn.setOnClickListener {
            binding.dojoCredsFoundText.visibility = View.GONE
            binding.changeDojoCredsBtn.visibility = View.GONE
            binding.setUpWalletScanDojo.visibility = View.VISIBLE
            binding.setUpWalletPasteJSON.visibility = View.VISIBLE
            setCredentials(
                listOf(
                    "",
                    "",
                    ""
                )
            )
        }

        binding.setUpWalletScanDojo.setOnClickListener {
            val cameraFragmentBottomSheet = CameraFragmentBottomSheet()
            cameraFragmentBottomSheet.show(supportFragmentManager, cameraFragmentBottomSheet.tag)
            cameraFragmentBottomSheet.setQrCodeScanListener { code: String ->
                cameraFragmentBottomSheet.dismissAllowingStateLoss()

                DojoUtil.getInstance(applicationContext).getUrl(code)
                setCredentials(
                    listOf(
                        DojoUtil.getInstance(applicationContext).getUrl(code),
                        DojoUtil.getInstance(applicationContext).getApiKey(code),
                        if (DojoUtil.getInstance(applicationContext).getExplorerUrl(code) == null) "Not configured" else DojoUtil.getInstance(applicationContext).getExplorerUrl(code)
                    )
                )

                binding.setUpWalletCreateNewWallet.setBackgroundColor(ContextCompat.getColor(applicationContext, R.color.warning_yellow))
                binding.setUpWalletCreateNewWallet.isEnabled = true
            }
        }

        binding.setUpWalletPasteJSON.setOnClickListener {
            val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
            val clipData: ClipData? = clipboard.primaryClip
            if (clipData != null && clipData.itemCount > 0) {
                val dojoPastedText = clipData.getItemAt(0).text.toString()
                parseDojoJSON(dojoPastedText)
            }
        }

        binding.setUpWalletCreateNewWallet.setOnClickListener {
            binding.setUpWalletCreateNewWallet.visibility = View.GONE
            binding.changeDojoCredsBtn.visibility = View.GONE
            binding.dojoConnectingCircle.visibility = View.VISIBLE
            connectDojo()
        }

        setUpWalletViewModel.viewModelScope.launch {
            withContext(Dispatchers.Main) {
                askNotificationPermission(this@SetDojoActivity)
            }
        }
    }

    private fun doDojoFromBackup() {
        binding.setUpWalletCreateNewWallet.setBackgroundColor(ContextCompat.getColor(applicationContext, R.color.warning_yellow))
        binding.setUpWalletCreateNewWallet.isEnabled = true

        binding.dojoCredsFoundText.visibility = View.VISIBLE
        binding.changeDojoCredsBtn.visibility = View.VISIBLE
        binding.setUpWalletScanDojo.visibility = View.GONE
        binding.setUpWalletPasteJSON.visibility = View.GONE
        setCredentials(
            listOf(
                intent.getStringExtra("dojoURL")!!,
                intent.getStringExtra("apikey")!!,
                if (intent.getStringExtra("explorerURL").isNullOrEmpty()) "Not configured" else intent.getStringExtra("explorerURL")!!
            )
        )

    }

    private fun enableOfflineMode(enable: Boolean) {
        if (enable) {
            binding.torStatus.text = "Disconnected"
            binding.torStatus.setTextColor(disabledColor)
            binding.offlineModeMessage.visibility = View.VISIBLE

            binding.setUpWalletCreateNewWallet.setBackgroundColor(
                ContextCompat.getColor(
                    this,
                    R.color.warning_yellow
                )
            )
            binding.setUpWalletCreateNewWallet.isEnabled = true
        }
        else {
            binding.offlineModeMessage.visibility = View.GONE

            binding.dojoURL.visibility = View.VISIBLE
            binding.dojoAPI.visibility = View.VISIBLE
            binding.explorerURL.visibility = View.VISIBLE
            binding.dojoUrlText.visibility = View.VISIBLE
            binding.dojoAPIText.visibility = View.VISIBLE
            binding.explorerURLText.visibility = View.VISIBLE

            binding.setUpWalletPasteJSON.visibility = View.VISIBLE
            binding.setUpWalletScanDojo.visibility = View.VISIBLE
        }
    }

    private fun disableButtons(enable: Boolean) {
        binding.setUpWalletScanDojo.isEnabled = !enable
        binding.setUpWalletPasteJSON.isEnabled = !enable
    }

    private fun setCredentials(credsList: List<String>) {
        dojoURL = credsList[0]
        apiKey = credsList[1]
        explorerURL = credsList[2]

        if (explorerURL.isNullOrEmpty())
            binding.explorerURL.text = ""
        else if (explorerURL.equals("Not configured")) {
            binding.explorerURL.text = explorerURL
            binding.explorerURL.typeface = ResourcesCompat.getFont(this, R.font.roboto_mono)
            binding.explorerURL.setTextColor( ContextCompat.getColor(this, R.color.white))
        } else {
            binding.explorerURL.text = explorerURL.substring(7, 11) + "....." + explorerURL.takeLast(9)
            binding.explorerURL.setTextColor( ContextCompat.getColor(this, R.color.warning_yellow))
        }

        binding.dojoAPI.text =
            if (apiKey.isNullOrEmpty())
                ""
            else
                apiKey.take(3) + "....." + apiKey.takeLast(3)
        binding.dojoURL.text =
            if (dojoURL.isNullOrEmpty())
                ""
            else
                "${dojoURL.substring(7, 11)}.....${if (SamouraiWallet.getInstance().isTestNet) dojoURL.takeLast(17) else dojoURL.takeLast(12)}"
    }

    private fun parseDojoJSON(jsonText: String) {
        try {
            val dojoJson = JSONObject(jsonText)

            if (dojoJson.has("pairing")) {

                setCredentials(
                    listOf(
                        dojoJson.getJSONObject("pairing").getString("url"),
                        dojoJson.getJSONObject("pairing").getString("apikey"),
                        if (dojoJson.has("explorer")) dojoJson.getJSONObject("explorer").getString("url") else "Not configured"
                    )
                )
                binding.setUpWalletCreateNewWallet.setBackgroundColor(ContextCompat.getColor(applicationContext, R.color.warning_yellow))
                binding.setUpWalletCreateNewWallet.isEnabled = true
                disableButtons(true)
            }
        } catch (e: Exception) {
            Toast.makeText(applicationContext, "Clipboard doesn't contain a valid Dojo pairing payload", Toast.LENGTH_LONG).show()
        }
    }

    private fun connectDojo() {
        if (isOffline && this::dojoURL.isInitialized) {
            PrefsUtil.getInstance(applicationContext).setValue(PrefsUtil.ENABLE_TOR, true);
            if (dojoURL.isNullOrEmpty()) {
                DojoUtil.getInstance(applicationContext).removeDojoParams()
                PayloadUtil.getInstance(applicationContext).saveWalletToJSON(CharSequenceX(AccessFactory.getInstance(applicationContext).guid + AccessFactory.getInstance(applicationContext).pin))
                PrefsUtil.getInstance(applicationContext).setValue(PrefsUtil.BLOCK_EXPLORER_URL, null);
            }

            val paring = JSONObject().apply {
                put("type", "dojo.api")
                put("apikey", apiKey)
                put("url", dojoURL)
                put("version", "1.4.5")
            }
            val dojoParams = JSONObject().apply {
                put("pairing", paring)
            }

            DojoUtil.getInstance(applicationContext)
                .setDojoParamsOfflineMode(dojoParams.toString())

            PayloadUtil.getInstance(applicationContext).saveWalletToJSON(CharSequenceX(AccessFactory.getInstance(applicationContext).guid + AccessFactory.getInstance(applicationContext).pin))

            AccessFactory.getInstance(applicationContext).setIsLoggedIn(false)
            TimeOutUtil.getInstance().updatePin()
            AppUtil.getInstance(applicationContext).restartApp()
            return
        }

        if (!this::dojoURL.isInitialized) {
            AccessFactory.getInstance(applicationContext).setIsLoggedIn(false)
            TimeOutUtil.getInstance().updatePin()
            AppUtil.getInstance(applicationContext).restartApp()
            return
        }


        setUpWalletViewModel.setApiUrl(dojoURL)
        setUpWalletViewModel.setApiKey(apiKey)
        if (!explorerURL.isEmpty() && !explorerURL.equals("Not configured"))
            PrefsUtil.getInstance(applicationContext).setValue(PrefsUtil.BLOCK_EXPLORER_URL, explorerURL);

        val paring = JSONObject().apply {
            put("type", "dojo.api")
            put("apikey", apiKey)
            put("url", dojoURL)
            put("version", "1.4.5")
        }
        val dojoParams = JSONObject().apply {
            put("pairing", paring)
        }

        DojoUtil.getInstance(applicationContext)
            .setDojoParamsOfflineMode(dojoParams.toString())

        PayloadUtil.getInstance(applicationContext).saveWalletToJSON(CharSequenceX(AccessFactory.getInstance(applicationContext).guid + AccessFactory.getInstance(applicationContext).pin))


        if (isOffline) {
            AccessFactory.getInstance(applicationContext).setIsLoggedIn(false)
            TimeOutUtil.getInstance().updatePin()
            AppUtil.getInstance(applicationContext).restartApp()
            return
        }

        SamouraiTorManager.start()
        SamouraiTorManager.getTorStateLiveData().observe(this, Observer {
            if (it.state == EnumTorState.ON) {
                AccessFactory.getInstance(applicationContext).setIsLoggedIn(false)
                TimeOutUtil.getInstance().updatePin()
                AppUtil.getInstance(applicationContext).restartApp()
            }
        })
    }

    private fun setTorState(torState: TorState) {
        val onBoardingTorStatus = binding.torStatus
        when (torState.state) {
            EnumTorState.STARTING -> {
                onBoardingTorStatus.text = "Disconnected"
                onBoardingTorStatus.setTextColor(disabledColor)
            }
            EnumTorState.ON -> {
                PrefsUtil.getInstance(applicationContext).setValue(PrefsUtil.ENABLE_TOR, true)
                onBoardingTorStatus.text = getString(R.string.active)
                onBoardingTorStatus.setTextColor(activeColor)
            }
            EnumTorState.OFF -> {
                PrefsUtil.getInstance(applicationContext).setValue(PrefsUtil.ENABLE_TOR, false)
                onBoardingTorStatus.text = getString(R.string.off)
                onBoardingTorStatus.setTextColor(disabledColor)
            }
            EnumTorState.STOPPING -> {
                PrefsUtil.getInstance(applicationContext).setValue(PrefsUtil.ENABLE_TOR, false)
                onBoardingTorStatus.text = getString(R.string.off)
                onBoardingTorStatus.setTextColor(waiting)
            }
        }
    }

}