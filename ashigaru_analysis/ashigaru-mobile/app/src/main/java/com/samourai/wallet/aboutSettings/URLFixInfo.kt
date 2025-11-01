package com.samourai.wallet.aboutSettings

import android.app.Dialog
import android.content.ClipboardManager
import android.content.Context
import android.os.Bundle
import android.util.TypedValue
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.FrameLayout
import androidx.core.content.ContextCompat
import com.google.android.material.bottomsheet.BottomSheetBehavior
import com.google.android.material.bottomsheet.BottomSheetDialog
import com.google.android.material.bottomsheet.BottomSheetDialogFragment
import com.samourai.wallet.R
import com.samourai.wallet.databinding.BottomsheetFixUrlsBinding

class URLFixInfo() : BottomSheetDialogFragment() {

    private var _binding: BottomsheetFixUrlsBinding? = null
    private val binding get() = _binding!!
    private var callback: Runnable? = null

    constructor(callback: Runnable) : this() {
        this.callback = callback
    }

    override fun getTheme(): Int {
        return R.style.NoDimBottomSheetTheme
    }

    override fun onStart() {
        super.onStart()
        if (getDialog() != null && getDialog()!!.getWindow() != null) {
            getDialog()!!.getWindow()!!.setNavigationBarColor(ContextCompat.getColor(requireContext(), R.color.networking));
        }
    }

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
    ): View {
        _binding = BottomsheetFixUrlsBinding.inflate(inflater, container, false)
        val view = binding.root

        return view
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        view.post {
            val parent = view.parent as View
            val bottomSheetBehavior =
                BottomSheetBehavior.from(parent)

            val fixHeight = TypedValue.applyDimension(
                TypedValue.COMPLEX_UNIT_DIP, 610f + 68f, resources.displayMetrics
            ).toInt()
            parent.layoutParams.height = fixHeight
            parent.requestLayout()
            bottomSheetBehavior.setState(BottomSheetBehavior.STATE_EXPANDED)
        }

        binding.pasteIcon.setOnClickListener {
            val clipboard = requireContext().getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
            val pgpMessage = if (clipboard.hasPrimaryClip()) {
                val item = clipboard.primaryClip?.getItemAt(0)
                item?.text.toString()
            } else {
                ""
            }
            binding.pgpMessageText.text = pgpMessage
            binding.pgpMessageText.setTextColor(ContextCompat.getColor(requireContext(), R.color.white))
            binding.fixUrlsButton.setBackgroundColor(ContextCompat.getColor(requireContext(), R.color.warning_yellow))
            binding.fixUrlsButton.isEnabled = true
        }

        binding.fixUrlsButton.setOnClickListener {
            this.dismiss()
            val dialog = FixURLsBottomsheet(binding.pgpMessageText.text.toString()) {
                if (callback != null) callback!!.run()
            }
            dialog.show(parentFragmentManager, "FixURLsBottomsheet")

        }
    }

}