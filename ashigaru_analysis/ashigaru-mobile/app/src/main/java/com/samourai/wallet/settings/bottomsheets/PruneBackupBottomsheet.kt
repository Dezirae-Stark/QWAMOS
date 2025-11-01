package com.samourai.wallet.settings.bottomsheets

import android.app.AlertDialog
import android.app.Dialog
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.FrameLayout
import android.widget.TextView
import android.widget.Toast
import androidx.core.content.ContextCompat
import com.google.android.material.bottomsheet.BottomSheetDialog
import com.google.android.material.bottomsheet.BottomSheetDialogFragment
import com.google.android.material.button.MaterialButton
import com.samourai.wallet.R
import com.samourai.wallet.access.AccessFactory
import com.samourai.wallet.crypto.DecryptionException
import com.samourai.wallet.payload.ExternalBackupManager
import com.samourai.wallet.payload.ExternalBackupManager.askPermission
import com.samourai.wallet.payload.ExternalBackupManager.hasPermissions
import com.samourai.wallet.payload.PayloadUtil
import com.samourai.wallet.ricochet.RicochetMeta
import com.samourai.wallet.send.RBFUtil
import com.samourai.wallet.util.CharSequenceX
import com.samourai.wallet.util.func.BatchSendUtil
import com.samourai.wallet.util.func.SendAddressUtil
import com.samourai.wallet.util.tech.SimpleCallback
import com.samourai.wallet.util.tech.SimpleTaskRunner
import org.bitcoinj.crypto.MnemonicException.MnemonicLengthException
import org.json.JSONException
import java.io.IOException

class PruneBackupBottomsheet() : BottomSheetDialogFragment() {

    override fun onCreateDialog(savedInstanceState: Bundle?): Dialog {
        val appUpdateAvailableDialog = super.onCreateDialog(savedInstanceState) as BottomSheetDialog
        appUpdateAvailableDialog.setOnShowListener { dialog ->
            val bottomSheet = (dialog as BottomSheetDialog).findViewById<View>(com.google.android.material. R.id.design_bottom_sheet) as FrameLayout?
            bottomSheet?.background = ContextCompat.getDrawable(requireContext(), R.drawable.rounded_rectangle_bottom_sheet)
        }
        return appUpdateAvailableDialog
    }

    override fun onCreateView(
            inflater: LayoutInflater,
            container: ViewGroup?,
            savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_prune_backup_bottomsheet, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        val yesBtn = view.findViewById<MaterialButton>(R.id.yes_button)
        val cancelBtn = view.findViewById<MaterialButton>(R.id.cancel_button)

        val fileLocText = view.findViewById<TextView>(R.id.file_location_text)
        fileLocText.text = ExternalBackupManager.getBackUpURI()!!.uri.path

        yesBtn.setOnClickListener{
            doPrune()
        }

        cancelBtn.setOnClickListener{
            this.dismiss()
        }
    }

    private fun doPrune() {
        if (!hasPermissions()) {
            askPermission(requireActivity())
            ExternalBackupManager.getPermissionStateLiveData().observe(this.viewLifecycleOwner) {
                if (it) {
                    doPrune()
                }
            }
        }
        else {
            try {
//                      BIP47Meta.getInstance().pruneIncoming();
                SendAddressUtil.getInstance().reset()
                RicochetMeta.getInstance(requireContext()).empty()
                BatchSendUtil.getInstance().clear()
                RBFUtil.getInstance().clear()
                PayloadUtil.getInstance(requireContext()).saveWalletToJSON(
                    CharSequenceX(
                        AccessFactory.getInstance(requireContext()).guid + AccessFactory.getInstance(requireContext()).pin)
                )
                this.dismiss()
                Toast.makeText(requireContext(), "Wallet backup file pruned successfully.", Toast.LENGTH_SHORT).show()

            } catch (je: JSONException) {
                je.printStackTrace()
                Toast.makeText(requireContext(), R.string.error_reading_payload, Toast.LENGTH_SHORT).show()
            } catch (_: MnemonicLengthException) {
            } catch (_: IOException) {
            } catch (_: DecryptionException) {
            }
        }
    }

}