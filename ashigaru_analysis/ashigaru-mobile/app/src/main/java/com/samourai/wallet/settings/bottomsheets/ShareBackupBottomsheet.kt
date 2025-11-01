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
import com.samourai.wallet.aboutSettings.URLFixInfo
import com.samourai.wallet.crypto.AESUtil
import com.samourai.wallet.payload.PayloadUtil
import com.samourai.wallet.util.CharSequenceX
import com.samourai.wallet.util.URLUpdater.URLFileUtil
import com.samourai.wallet.util.tech.SimpleCallback
import com.samourai.wallet.util.tech.SimpleTaskRunner
import org.json.JSONObject
import java.net.URL

class ShareBackupBottomsheet(private val isTroubleshooting: Boolean = false, val passphrase: String = "") : BottomSheetDialogFragment() {

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
        return inflater.inflate(R.layout.fragment_share_backup_bottomsheet, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        if (isTroubleshooting) {
            view.findViewById<TextView>(R.id.titleBottomsheet).text =
                getString(R.string.wallet_info_for_troubleshooting)
            view.findViewById<TextView>(R.id.noteText).visibility = View.VISIBLE
        }

        val copyBtn = view.findViewById<MaterialButton>(R.id.copy_btn)
        val shareBtn = view.findViewById<MaterialButton>(R.id.share_button)

        val payloadJson = doSendBackup(isTroubleshooting)

        copyBtn.setOnClickListener{
            AlertDialog.Builder(requireContext())
                .setTitle(R.string.app_name)
                .setMessage(R.string.copy_warning_generic)
                .setCancelable(false)
                .setPositiveButton(
                    R.string.yes
                ) { dialog, whichButton ->
                    SimpleTaskRunner.create().executeAsync<Void>(
                        true,
                        {
                            val clipboard =
                                requireContext().getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                            var clip: ClipData? = null
                            clip = ClipData.newPlainText("Backup file", payloadJson.toString())
                            clipboard.setPrimaryClip(clip)
                            null
                        },
                        object : SimpleCallback<Void?> {
                        }
                    )
                }.setNegativeButton(
                    R.string.no
                ) { dialog, whichButton -> }.show()
        }

        shareBtn.setOnClickListener{
            val sendIntent: Intent = Intent().apply {
                action = Intent.ACTION_SEND
                putExtra(Intent.EXTRA_TEXT, payloadJson.toString())
                type = "text/plain"
            }
            val shareIntent = Intent.createChooser(sendIntent, null)
            startActivity(shareIntent)
        }
    }

    private fun doSendBackup(isTroubleshooting: Boolean): JSONObject? {
        try {

            val jsonObject = PayloadUtil.getInstance(requireContext()).payload

            if (!isTroubleshooting) {
                var encrypted: String? = null

                try {
                    encrypted = AESUtil.encryptSHA256(PayloadUtil.getInstance(requireContext()).payload.toString(), CharSequenceX(
                        this.passphrase
                    ))
                } catch (e: Exception) {
                    Toast.makeText(requireContext(), e.message, Toast.LENGTH_SHORT).show()
                }

                val obj = PayloadUtil.getInstance(requireContext()).putPayload(encrypted, true)

                return obj
            }

            jsonObject.getJSONObject("wallet").remove("seed")
            jsonObject.getJSONObject("wallet").remove("passphrase")

            if (jsonObject.has("meta")) {

                if (jsonObject.getJSONObject("meta").has("pin")) {
                    jsonObject.getJSONObject("meta").remove("pin")
                }
                if (jsonObject.getJSONObject("meta").has("pin2")) {
                    jsonObject.getJSONObject("meta").remove("pin2")
                }

                if (jsonObject.getJSONObject("meta").has("trusted_node")) {
                    if (jsonObject.getJSONObject("meta").getJSONObject("trusted_node").has("password")) {
                        jsonObject.getJSONObject("meta").getJSONObject("trusted_node").remove("password")
                    }
                    if (jsonObject.getJSONObject("meta").getJSONObject("trusted_node").has("node")) {
                        jsonObject.getJSONObject("meta").getJSONObject("trusted_node").remove("node")
                    }
                    if (jsonObject.getJSONObject("meta").getJSONObject("trusted_node").has("port")) {
                        jsonObject.getJSONObject("meta").getJSONObject("trusted_node").remove("port")
                    }
                    if (jsonObject.getJSONObject("meta").getJSONObject("trusted_node").has("user")) {
                        jsonObject.getJSONObject("meta").getJSONObject("trusted_node").remove("user")
                    }
                }
            }

            val seedURLs = URLFileUtil.getInstance(requireContext()).readFromFile();
            jsonObject.put("URLs", seedURLs);

            return jsonObject

        } catch (e: Exception) {
            e.printStackTrace()
            Toast.makeText(requireContext(), R.string.error_reading_payload, Toast.LENGTH_SHORT).show()
        }
        return JSONObject()
    }

}