package com.samourai.wallet.settings.bottomsheets

import android.app.AlertDialog
import android.app.Dialog
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.FrameLayout
import android.widget.Toast
import androidx.core.content.ContextCompat
import com.google.android.material.bottomsheet.BottomSheetDialog
import com.google.android.material.bottomsheet.BottomSheetDialogFragment
import com.google.android.material.button.MaterialButton
import com.samourai.wallet.BuildConfig
import com.samourai.wallet.R
import com.samourai.wallet.util.URLUpdater.URLFileUtil
import com.samourai.wallet.util.tech.AppUtil
import com.samourai.wallet.util.tech.SimpleCallback
import com.samourai.wallet.util.tech.SimpleTaskRunner
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch
import kotlinx.coroutines.plus
import org.apache.commons.io.FileUtils

class WipeWalletBottomSheet() : BottomSheetDialogFragment() {

    private val scope = CoroutineScope(Dispatchers.IO) + SupervisorJob();

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
        return inflater.inflate(R.layout.fragment_wipe_wallet_bottomsheet, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        val eraseBtn = view.findViewById<MaterialButton>(R.id.erase_button)
        val cancelBtn = view.findViewById<MaterialButton>(R.id.cancel_button)

        eraseBtn.setOnClickListener {
            AlertDialog.Builder(requireContext())
                .setTitle(R.string.erase_wallet_data)
                .setMessage(R.string.certain_erase_data)
                .setCancelable(false)
                .setPositiveButton(
                    R.string.yes
                ) { dialog, whichButton ->
                    scope.launch {
                        URLFileUtil.getInstance(requireContext()).deleteFile()
                        AppUtil.getInstance(requireContext()).wipeApp()

                        val walletDir = requireContext().getDir("wallet", Context.MODE_PRIVATE)
                        val filesDir = requireContext().filesDir
                        val cacheDir = requireContext().cacheDir

                        if (walletDir.exists()) {
                            FileUtils.deleteDirectory(walletDir);
                        }
                        if (filesDir.exists()) {
                            FileUtils.deleteDirectory(filesDir);
                        }
                        if (cacheDir.exists()) {
                            FileUtils.deleteDirectory(cacheDir);

                        }
                    }.invokeOnCompletion {
                        scope.launch(Dispatchers.Main) {
                            if (it == null) {
                                Toast.makeText(requireContext(), R.string.wallet_erased, Toast.LENGTH_SHORT).show()
                                AppUtil.getInstance(requireContext()).restartApp()
                            } else {
                                Toast.makeText(requireContext(), "Error ${it.message}", Toast.LENGTH_SHORT).show()
                                if (BuildConfig.DEBUG) {
                                    it.printStackTrace();
                                }
                            }
                        }
                    }
                }.setNegativeButton(
                    R.string.cancel
                ) { dialog, whichButton -> }.show()
        }

        cancelBtn.setOnClickListener{
            this.dismiss()
        }
    }

}