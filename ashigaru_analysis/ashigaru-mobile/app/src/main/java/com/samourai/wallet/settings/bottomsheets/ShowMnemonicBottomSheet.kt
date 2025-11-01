package com.samourai.wallet.settings.bottomsheets

import android.app.AlertDialog
import android.app.Dialog
import android.content.ClipData
import android.content.ClipboardManager
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.WindowManager
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.core.content.ContextCompat
import com.google.android.material.bottomsheet.BottomSheetDialog
import com.google.android.material.bottomsheet.BottomSheetDialogFragment
import com.samourai.wallet.R
import com.samourai.wallet.SamouraiActivity.CLIPBOARD_SERVICE
import com.samourai.wallet.hd.HD_WalletFactory
import com.samourai.wallet.util.tech.SimpleCallback
import com.samourai.wallet.util.tech.SimpleTaskRunner

class ShowMnemonicBottomSheet() : BottomSheetDialogFragment() {

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
        return inflater.inflate(R.layout.show_seed_bottomsheet, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        this.dialog?.window?.setFlags(WindowManager.LayoutParams.FLAG_SECURE, WindowManager.LayoutParams.FLAG_SECURE)

        var seed: String? = null
        try {
            seed = HD_WalletFactory.getInstance(requireContext()).get().mnemonic
        } catch (_: Exception) {}

        view.findViewById<ImageView>(R.id.copy_seed).setOnClickListener {

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
                            val clipboard = requireContext().getSystemService(CLIPBOARD_SERVICE) as ClipboardManager
                            val clip: ClipData = ClipData.newPlainText("seed", seed)
                            clipboard.setPrimaryClip(clip)
                            Toast.makeText(requireContext(), R.string.copied_to_clipboard, Toast.LENGTH_SHORT).show()
                            null
                        },
                        object : SimpleCallback<Void?> {
                            override fun onComplete(result: Void?) {
                                Toast.makeText(
                                    requireContext(),
                                    R.string.copied_to_clipboard,
                                    Toast.LENGTH_SHORT
                                ).show()
                            }
                        }
                    )
                }.setNegativeButton(
                    R.string.no
                ) { dialog, whichButton -> }.show()
        }

        // Set the seed words to their respective text fields:
        if (seed!!.split(" ").size == 12) {
            view.findViewById<LinearLayout>(R.id.row7).visibility = View.GONE
            view.findViewById<LinearLayout>(R.id.row8).visibility = View.GONE
            view.findViewById<LinearLayout>(R.id.row9).visibility = View.GONE
            view.findViewById<LinearLayout>(R.id.row10).visibility = View.GONE
            view.findViewById<LinearLayout>(R.id.row11).visibility = View.GONE
            view.findViewById<LinearLayout>(R.id.row12).visibility = View.GONE
        }
        else if (seed.split(" ").size == 15) {
            view.findViewById<TextView>(R.id.text16).visibility = View.INVISIBLE
            view.findViewById<TextView>(R.id.seed_word_16).visibility = View.INVISIBLE

            view.findViewById<LinearLayout>(R.id.row9).visibility = View.GONE
            view.findViewById<LinearLayout>(R.id.row10).visibility = View.GONE
            view.findViewById<LinearLayout>(R.id.row11).visibility = View.GONE
            view.findViewById<LinearLayout>(R.id.row12).visibility = View.GONE
        }
        else if (seed.split(" ").size == 18) {
            view.findViewById<LinearLayout>(R.id.row10).visibility = View.GONE
            view.findViewById<LinearLayout>(R.id.row11).visibility = View.GONE
            view.findViewById<LinearLayout>(R.id.row12).visibility = View.GONE
        }

        for (i in 0 until seed.split(" ").size) {
            val fieldName = "seed_word_${i+1}"

            val resourceId = resources.getIdentifier(fieldName, "id", requireContext().packageName)

            view.findViewById<TextView>(resourceId).text = seed.split(" ")[i]
        }
    }
}