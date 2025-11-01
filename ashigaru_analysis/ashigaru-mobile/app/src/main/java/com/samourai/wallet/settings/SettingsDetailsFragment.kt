package com.samourai.wallet.settings

import android.content.DialogInterface
import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.lifecycle.ViewModelProvider
import androidx.preference.Preference
import androidx.preference.PreferenceFragmentCompat
import androidx.transition.Transition
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.samourai.wallet.R
import com.samourai.wallet.SamouraiWallet
import com.samourai.wallet.aboutSettings.AboutActivity
import com.samourai.wallet.access.AccessFactory
import com.samourai.wallet.crypto.AESUtil
import com.samourai.wallet.hd.HD_WalletFactory
import com.samourai.wallet.payload.ExternalBackupManager
import com.samourai.wallet.payload.PayloadUtil
import com.samourai.wallet.pin.PinChangeDialog
import com.samourai.wallet.pin.PinEntryDialog
import com.samourai.wallet.ricochet.RicochetMeta
import com.samourai.wallet.segwit.BIP49Util
import com.samourai.wallet.segwit.BIP84Util
import com.samourai.wallet.settings.bottomsheets.CheckPassphraseFragment
import com.samourai.wallet.settings.bottomsheets.PruneBackupBottomsheet
import com.samourai.wallet.settings.bottomsheets.PubkeyViewerFragment
import com.samourai.wallet.settings.bottomsheets.ShareBackupBottomsheet
import com.samourai.wallet.settings.bottomsheets.ShowMnemonicBottomSheet
import com.samourai.wallet.settings.bottomsheets.TestBackupBottomsheet
import com.samourai.wallet.settings.bottomsheets.WipeWalletBottomSheet
import com.samourai.wallet.stealth.StealthModeSettings
import com.samourai.wallet.swaps.SwapsMeta
import com.samourai.wallet.util.CharSequenceX
import com.samourai.wallet.util.PrefsUtil
import com.samourai.wallet.util.func.FormatsUtil
import com.samourai.wallet.util.tech.AppUtil
import com.samourai.wallet.whirlpool.WhirlpoolMeta
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.isActive
import kotlinx.coroutines.plus
import org.bitcoinj.crypto.MnemonicException.MnemonicLengthException
import java.io.IOException
import java.util.concurrent.CancellationException


class SettingsDetailsFragment(private val key: String?) : PreferenceFragmentCompat() {

    var targetTransition: Transition? = null
    private val scope = CoroutineScope(Dispatchers.IO) + SupervisorJob();

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        targetTransition?.addTarget(view)
        super.onViewCreated(view, savedInstanceState)
    }

    override fun onCreatePreferences(savedInstanceState: Bundle?, rootKey: String?) {
        when (key) {
            "change_pin2" -> {
                setPreferencesFromResource(R.xml.settings_pin_entry, rootKey)
                activity?.title = "Security"
            }
            "viewExtendedPubkeys" -> {
                setPreferencesFromResource(R.xml.settings_pubkeys, rootKey)
                activity?.title = "Extended Public Keys"
                (activity as SettingsActivity).activePreferences = "VIEW_PUBKEYS"
            }
            "security" -> {
                setPreferencesFromResource(R.xml.settings_security, rootKey)
                activity?.title = "Security"
                securitySettings(rootKey)
            }
            "wallet" -> {
                setPreferencesFromResource(R.xml.settings_wallet, rootKey)
                activity?.title = "Wallet"
                walletSettings(rootKey)
            }
            "txs" -> {
                activity?.title = "Transactions"
                setPreferencesFromResource(R.xml.settings_txs, rootKey)
                transactionsSettings()
            }
            "troubleshoot" -> {
                activity?.title = "Backups"
                setPreferencesFromResource(R.xml.settings_troubleshoot, rootKey)
                troubleShootSettings()
            }
            "other" -> {
                activity?.title = "About"
                startActivity(Intent(this.activity, AboutActivity::class.java))
                requireActivity().finish()
            }
        }
    }

    private fun securitySettings(rootKey: String?) {

        val wipePreference = findPreference("wipe") as Preference?
        wipePreference!!.onPreferenceClickListener = Preference.OnPreferenceClickListener {
            val dialog = WipeWalletBottomSheet()
            dialog.show(requireFragmentManager(), dialog.tag)
            true
        }

        val changePinPref = findPreference("change_pin2") as Preference?
        changePinPref!!.onPreferenceClickListener = Preference.OnPreferenceClickListener {
            setPreferencesFromResource(R.xml.settings_pin_entry, rootKey)
            (activity as SettingsActivity).activePreferences = "PIN_ENTRY"
            activity?.title = "PIN Entry"
            pinSettings()
            true
        }

        val stealthPreference: CustomPreference? = findPreference("stealth") as? CustomPreference
        stealthPreference!!.setOnPreferenceClickListener {
            startActivity(Intent(this.activity,StealthModeSettings::class.java))
            true
        }
    }

    private fun pinSettings() {
        val cbPref5: CustomPreference? = findPreference("scramble") as? CustomPreference
        val viewModelScramble = ViewModelProvider(this, CustomPrefViewModelFactory()).get("viewModelScramble", CustomPreferenceViewModel::class.java)
        cbPref5!!.bindViewModel(viewModelScramble, this)

        viewModelScramble.setSwitchState(PrefsUtil.getInstance(requireContext()).getValue(PrefsUtil.SCRAMBLE_PIN, true))
        viewModelScramble.setPrefToChange(PrefsUtil.SCRAMBLE_PIN)
        cbPref5.setOnPreferenceClickListener {
            val currentValue = viewModelScramble.isSwitchOn.value ?: true
            viewModelScramble.setSwitchState(!currentValue)
            PrefsUtil.getInstance(requireContext()).setValue(PrefsUtil.SCRAMBLE_PIN, !currentValue)
            PayloadUtil.getInstance(context).saveWalletToJSON(CharSequenceX(AccessFactory.getInstance(context).guid + AccessFactory.getInstance(context).pin))
            true
        }

        val cbPref11: CustomPreference? = findPreference("haptic_feedback") as? CustomPreference
        val viewModelHaptic = ViewModelProvider(this, CustomPrefViewModelFactory()).get("viewModelHaptic", CustomPreferenceViewModel::class.java)
        cbPref11!!.bindViewModel(viewModelHaptic, this)

        viewModelHaptic.setPrefToChange(PrefsUtil.HAPTIC_PIN)
        viewModelHaptic.setSwitchState(PrefsUtil.getInstance(requireContext()).getValue(PrefsUtil.HAPTIC_PIN, true))
        cbPref11.setOnPreferenceClickListener {
            val currentValue = viewModelHaptic.isSwitchOn.value ?: true
            viewModelHaptic.setSwitchState(!currentValue)
            PrefsUtil.getInstance(requireContext()).setValue(PrefsUtil.HAPTIC_PIN, !currentValue)
            PayloadUtil.getInstance(context).saveWalletToJSON(CharSequenceX(AccessFactory.getInstance(context).guid + AccessFactory.getInstance(context).pin))
            true
        }



        val changePinPref = findPreference("change_pin") as Preference?
        changePinPref!!.onPreferenceClickListener = Preference.OnPreferenceClickListener {
            val pinEntryDialog = PinEntryDialog.create()
            pinEntryDialog.setOnSuccessCallback {
                requireActivity().runOnUiThread {
                    pinEntryDialog.dismiss()
                    val pinChangeDialog = PinChangeDialog.create()
                    pinChangeDialog.setOnSuccessCallback { newPin ->
                        requireActivity().runOnUiThread {
                            pinChangeDialog.dismiss()
                            changeWalletPin(newPin)
                        }
                    }
                    pinChangeDialog.show(requireActivity().supportFragmentManager, pinChangeDialog.tag)
                }
            }
            pinEntryDialog.show(requireActivity().supportFragmentManager, pinEntryDialog.tag)
            true
        }
    }

    private fun pubkeySettings() {
        val depositPubsPref = findPreference("showDepositPubs") as Preference?
        depositPubsPref!!.onPreferenceClickListener = Preference.OnPreferenceClickListener {
            val dialog = PubkeyViewerFragment(
                arrayListOf(getXPUBString(44, 0), getXPUBString(49, 0), getXPUBString(84,0)),
                arrayListOf("Deposit BIP44 xPUB", "Deposit BIP49 yPUB", "Deposit BIP84 zPUB")
            )
            dialog.show(requireFragmentManager(), dialog.tag)
            true
        }

        val whirlpoolPubsPref = findPreference("showWhirlpoolPubs") as Preference?
        whirlpoolPubsPref!!.onPreferenceClickListener = Preference.OnPreferenceClickListener {
            val dialog = PubkeyViewerFragment(
                arrayListOf(
                    getXPUBString(84, WhirlpoolMeta.getInstance(requireContext()).whirlpoolPremixAccount),
                    getXPUBString(84, WhirlpoolMeta.getInstance(requireContext()).whirlpoolPostmix),
                    getXPUBString(44, WhirlpoolMeta.getInstance(requireContext()).whirlpoolPostmix),
                    getXPUBString(49, WhirlpoolMeta.getInstance(requireContext()).whirlpoolPostmix),
                ),
                arrayListOf("Premix BIP84 zPUB", "Postmix BIP84 zPUB", "Postmix-change xPUB", "Postmix-change yPUB")
            )
            dialog.show(requireFragmentManager(), dialog.tag)
            true
        }

        val badbankPubsPref = findPreference("showBadBankPubs") as Preference?
        badbankPubsPref!!.onPreferenceClickListener = Preference.OnPreferenceClickListener {
            val dialog = PubkeyViewerFragment(
                arrayListOf(
                    getXPUBString(84, WhirlpoolMeta.getInstance(requireContext()).whirlpoolBadBank)
                ),
                arrayListOf("Bad Bank BIP84 zPUB")
            )
            dialog.show(requireFragmentManager(), dialog.tag)
            true
        }

        val swapsPubsPref = findPreference("showSwapsPubs") as Preference?
        swapsPubsPref!!.onPreferenceClickListener = Preference.OnPreferenceClickListener {
            val dialog = PubkeyViewerFragment(
                arrayListOf(
                    getXPUBString(84, SwapsMeta.getInstance(requireContext()).swapsMainAccount),
                    getXPUBString(84, SwapsMeta.getInstance(requireContext()).swapsRefundAccount),
                    getXPUBString(84, SwapsMeta.getInstance(requireContext()).swapsAsbMainAccount),
                ),
                arrayListOf("Swaps Deposit BIP84 zPUB", "Swaps Refund BIP84 zPUB", "Swaps ASB BIP84 zPUB")
            )
            dialog.show(requireFragmentManager(), dialog.tag)
            true
        }

        val ricochetPubPref = findPreference("showRicochetPub") as Preference?
        ricochetPubPref!!.onPreferenceClickListener = Preference.OnPreferenceClickListener {
            val dialog = PubkeyViewerFragment(
                arrayListOf(
                    getXPUBString(84, RicochetMeta.getInstance(requireContext()).ricochetAccount)
                ),
                arrayListOf("Ricochet BIP84 zPUB")
            )
            dialog.show(requireFragmentManager(), dialog.tag)
            true
        }


        val techInfoPref = findPreference("showTechInfo") as Preference?
        techInfoPref!!.onPreferenceClickListener = Preference.OnPreferenceClickListener {
            startActivity(Intent(this.activity,WalletTechInfo::class.java))
            true
        }
    }

    private fun walletSettings(rootKey: String?) {

        val showMnemonicPref = findPreference("showMnemonic") as Preference?
        showMnemonicPref!!.onPreferenceClickListener = Preference.OnPreferenceClickListener {
            val dialog = ShowMnemonicBottomSheet()
            dialog.show(requireFragmentManager(), dialog.tag)
            true
        }

        val shareWalletInfoPref = findPreference("shareWalletInfo") as Preference?
        shareWalletInfoPref!!.onPreferenceClickListener = Preference.OnPreferenceClickListener {
            val dialog = ShareBackupBottomsheet(
                isTroubleshooting = true,
            )
            dialog.show(requireFragmentManager(), dialog.tag)
            true
        }

        val showLogsPref = findPreference("showLogs") as Preference?
        showLogsPref!!.onPreferenceClickListener = Preference.OnPreferenceClickListener {
            showLogs()
            true
        }

        val checkPassphrasePref = findPreference("checkBip39") as Preference?
        checkPassphrasePref!!.onPreferenceClickListener = Preference.OnPreferenceClickListener {
            val dialog = CheckPassphraseFragment()
            dialog.show(requireFragmentManager(), dialog.tag)
            true
        }

        val showPubsPref = findPreference("viewExtendedPubkeys") as Preference?
        showPubsPref!!.onPreferenceClickListener = Preference.OnPreferenceClickListener {
            setPreferencesFromResource(R.xml.settings_pubkeys, rootKey)
            (activity as SettingsActivity).activePreferences = "VIEW_PUBKEYS"
            activity?.title = "Extended Public Keys"
            pubkeySettings()
            true
        }
    }

    private fun changeWalletPin(newPin: String?) {
        val accessHash = PrefsUtil.getInstance(requireContext()).getValue(PrefsUtil.ACCESS_HASH, "")
        val accessHash2 =
            PrefsUtil.getInstance(requireContext()).getValue(PrefsUtil.ACCESS_HASH2, "")
        val hash = AccessFactory.getInstance(requireContext()).getHash(
            AccessFactory.getInstance(requireContext()).guid,
            CharSequenceX(newPin),
            AESUtil.DefaultPBKDF2Iterations
        )
        PrefsUtil.getInstance(requireContext()).setValue(PrefsUtil.ACCESS_HASH, hash)
        if (accessHash == accessHash2) {
            PrefsUtil.getInstance(requireContext()).setValue(PrefsUtil.ACCESS_HASH2, hash)
        }
        AccessFactory.getInstance(requireContext()).pin = newPin
        try {
            PayloadUtil.getInstance(requireContext())
                .saveWalletToJSON(CharSequenceX(AccessFactory.getInstance(requireContext()).guid + newPin))
        } catch (e: Exception) {
            e.printStackTrace();
        } finally {
            Toast.makeText(
                requireContext().getApplicationContext(),
                R.string.success_change_pin,
                Toast.LENGTH_SHORT
            ).show()
        }
    }

    private fun transactionsSettings() {
        val broadcastPref: CustomPreference? = findPreference("broadcastTx") as? CustomPreference
        val viewModelBroadcast = ViewModelProvider(this, CustomPrefViewModelFactory()).get("viewModelBroadcast", CustomPreferenceViewModel::class.java)
        broadcastPref!!.bindViewModel(viewModelBroadcast, this)

        viewModelBroadcast.setPrefToChange(PrefsUtil.BROADCAST_TX)
        viewModelBroadcast.setSwitchState(PrefsUtil.getInstance(activity).getValue(PrefsUtil.BROADCAST_TX, true))
        broadcastPref.setOnPreferenceClickListener {
            val currentValue = viewModelBroadcast.isSwitchOn.value ?: true
            viewModelBroadcast.setSwitchState(!currentValue)
            PrefsUtil.getInstance(activity).setValue(PrefsUtil.BROADCAST_TX, !currentValue)
            PayloadUtil.getInstance(requireContext()).saveWalletToJSON(CharSequenceX(AccessFactory.getInstance(requireContext()).guid + AccessFactory.getInstance(requireContext()).pin))
            true
        }

        val likeTypePref: CustomPreference? = findPreference("likeTypedChange") as? CustomPreference
        val viewModelLikeType = ViewModelProvider(this, CustomPrefViewModelFactory()).get("viewModelLikeType", CustomPreferenceViewModel::class.java)
        likeTypePref!!.bindViewModel(viewModelLikeType, this)

        viewModelLikeType.setPrefToChange(PrefsUtil.USE_LIKE_TYPED_CHANGE)
        viewModelLikeType.setSwitchState(PrefsUtil.getInstance(activity).getValue(PrefsUtil.USE_LIKE_TYPED_CHANGE, true))
        likeTypePref.setOnPreferenceClickListener {
            val currentValue = viewModelLikeType.isSwitchOn.value ?: true
            viewModelLikeType.setSwitchState(!currentValue)
            PrefsUtil.getInstance(activity).setValue(PrefsUtil.USE_LIKE_TYPED_CHANGE, !currentValue)
            PayloadUtil.getInstance(requireContext()).saveWalletToJSON(CharSequenceX(AccessFactory.getInstance(requireContext()).guid + AccessFactory.getInstance(requireContext()).pin))
            true
        }

        val strictPref: CustomPreference? = findPreference("strictOutputs") as? CustomPreference
        val viewModelStrict = ViewModelProvider(this, CustomPrefViewModelFactory()).get("viewModelStric", CustomPreferenceViewModel::class.java)
        strictPref!!.bindViewModel(viewModelStrict, this)

        viewModelStrict.setPrefToChange(PrefsUtil.STRICT_OUTPUTS)
        viewModelStrict.setSwitchState(PrefsUtil.getInstance(activity).getValue(PrefsUtil.STRICT_OUTPUTS, true))
        strictPref.setOnPreferenceClickListener {
            val currentValue = viewModelStrict.isSwitchOn.value ?: true
            viewModelStrict.setSwitchState(!currentValue)
            PrefsUtil.getInstance(activity).setValue(PrefsUtil.STRICT_OUTPUTS, !currentValue)
            PayloadUtil.getInstance(requireContext()).saveWalletToJSON(CharSequenceX(AccessFactory.getInstance(requireContext()).guid + AccessFactory.getInstance(requireContext()).pin))
            true
        }

        val rbfPref: CustomPreference? = findPreference("rbf") as? CustomPreference
        val viewModelRBF = ViewModelProvider(this, CustomPrefViewModelFactory()).get("viewModelRBF", CustomPreferenceViewModel::class.java)
        rbfPref!!.bindViewModel(viewModelRBF, this)

        viewModelRBF.setPrefToChange(PrefsUtil.RBF_OPT_IN)
        viewModelRBF.setSwitchState(PrefsUtil.getInstance(activity).getValue(PrefsUtil.RBF_OPT_IN, true))
        rbfPref.setOnPreferenceClickListener {
            val currentValue = viewModelRBF.isSwitchOn.value ?: true
            viewModelRBF.setSwitchState(!currentValue)
            PrefsUtil.getInstance(activity).setValue(PrefsUtil.RBF_OPT_IN, !currentValue)
            PayloadUtil.getInstance(requireContext()).saveWalletToJSON(CharSequenceX(AccessFactory.getInstance(requireContext()).guid + AccessFactory.getInstance(requireContext()).pin))
            true
        }

    }

    private fun troubleShootSettings() {
        val autosavePref: CustomPreference? = findPreference("autosaveFile") as? CustomPreference
        val viewModelAutosave = ViewModelProvider(this, CustomPrefViewModelFactory()).get("viewModelAutosave", CustomPreferenceViewModel::class.java)
        autosavePref!!.bindViewModel(viewModelAutosave, this)

        if (!SamouraiWallet.getInstance().hasPassphrase(requireContext())) {
            viewModelAutosave.setSwitchState(false)
            viewModelAutosave.setPrefToChange(PrefsUtil.AUTO_BACKUP)
            autosavePref.isEnabled = false
        } else {
            viewModelAutosave.setSwitchState(PrefsUtil.getInstance(requireContext()).getValue(PrefsUtil.AUTO_BACKUP, false))
            autosavePref.setOnPreferenceClickListener {
                val currentValue = viewModelAutosave.isSwitchOn.value ?: true
                viewModelAutosave.setSwitchState(!currentValue)
                PrefsUtil.getInstance(activity).setValue(PrefsUtil.AUTO_BACKUP, !currentValue)
                true
            }
        }

        val exportFilePref: CustomPreference? = findPreference("exportFile") as? CustomPreference
        exportFilePref!!.setOnPreferenceClickListener {
            doShareEncryptedFile()
            true
        }

        val pruneFilePref: CustomPreference? = findPreference("prune") as? CustomPreference
        pruneFilePref!!.setOnPreferenceClickListener {
            val dialog = PruneBackupBottomsheet()
            dialog.show(requireFragmentManager(), dialog.tag)
            true
        }

        val testFilePref: CustomPreference? = findPreference("testFile") as? CustomPreference
        testFilePref!!.setOnPreferenceClickListener {
            val dialog = TestBackupBottomsheet()
            dialog.show(requireFragmentManager(), dialog.tag)
            true
        }

    }

    private fun doShareEncryptedFile() {
        if (SamouraiWallet.getInstance().hasPassphrase(context)) {
            if (HD_WalletFactory.getInstance(context).get() != null && SamouraiWallet.getInstance().hasPassphrase(context)) {
                val dialog = ShareBackupBottomsheet(isTroubleshooting = false, HD_WalletFactory.getInstance(context).get().passphrase)
                dialog.show(requireFragmentManager(), dialog.tag)
            }
        } else {
            val builder = MaterialAlertDialogBuilder(requireContext())
            builder.setTitle(R.string.enter_backup_password)
            val view = layoutInflater.inflate(R.layout.password_input_dialog_layout, null)
            val password = view.findViewById<EditText>(R.id.restore_dialog_password_edittext)
            val message = view.findViewById<TextView>(R.id.dialogMessage)
            message.setText(R.string.backup_password)
            builder.setPositiveButton(R.string.confirm) { dialog: DialogInterface, which: Int ->
                val pw = password.text.toString()
                if (pw.length >= AppUtil.MIN_BACKUP_PW_LENGTH && pw.length <= AppUtil.MAX_BACKUP_PW_LENGTH) {
                    val dialog2 = ShareBackupBottomsheet(isTroubleshooting = false, pw)
                    dialog2.show(requireFragmentManager(), dialog2.tag)
                } else {
                    Toast.makeText(context, R.string.password_error, Toast.LENGTH_SHORT).show()
                }
                dialog.dismiss()
            }
            builder.setNegativeButton(R.string.cancel) { dialog: DialogInterface, which: Int -> dialog.dismiss() }
            builder.setView(view)
            builder.show()
        }
    }

    private fun getXPUBString(purpose: Int, account: Int): String {
        var xpub = ""
        if((purpose == 44 || purpose == 49) && account == WhirlpoolMeta.getInstance(context).whirlpoolPostmix) {

            val vpub = BIP84Util.getInstance(context).wallet.getAccount(WhirlpoolMeta.getInstance(context).whirlpoolPostmix).zpubstr()

            if(purpose == 49) {
                xpub = FormatsUtil.xlatXPUB(vpub, true);
            }
            else {
                xpub = FormatsUtil.xlatXPUB(vpub, false);
            }

        }
        else {
            when (purpose) {
                49 -> xpub = BIP49Util.getInstance(context).wallet.getAccount(account).ypubstr()
                84 -> xpub = BIP84Util.getInstance(context).wallet.getAccount(account).zpubstr()
                else -> try {
                    xpub = HD_WalletFactory.getInstance(context).get().getAccount(account).xpubstr()
                } catch (ioe: IOException) {
                    ioe.printStackTrace()

                    Toast.makeText(context, "HD wallet error", Toast.LENGTH_SHORT).show()
                } catch (mle: MnemonicLengthException) {
                    mle.printStackTrace()
                    Toast.makeText(context, "HD wallet error", Toast.LENGTH_SHORT).show()
                }
            }
        }

        return xpub
    }

    private fun showLogs() {
        startActivity(Intent(requireContext(),LogViewActivity::class.java))
    }

    override fun onDestroy() {
        if (scope.isActive) {
            scope.cancel(CancellationException())
        }
        super.onDestroy()
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        ExternalBackupManager.onActivityResult(requestCode, resultCode, data, requireActivity().application)
        super.onActivityResult(requestCode, resultCode, data)

    }
}