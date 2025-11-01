package com.samourai.wallet.settings.bottomsheets

import android.app.AlertDialog
import android.app.Dialog
import android.content.ClipData
import android.content.ClipboardManager
import android.graphics.Bitmap
import android.os.Bundle
import android.util.TypedValue
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.FrameLayout
import android.widget.Toast
import androidx.compose.runtime.currentCompositeKeyHash
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.fragment.app.FragmentActivity
import androidx.viewpager2.adapter.FragmentStateAdapter
import com.google.android.material.bottomsheet.BottomSheetBehavior
import com.google.android.material.bottomsheet.BottomSheetDialog
import com.google.android.material.bottomsheet.BottomSheetDialogFragment
import com.google.zxing.BarcodeFormat
import com.google.zxing.WriterException
import com.google.zxing.client.android.Contents
import com.google.zxing.client.android.encode.QRCodeEncoder
import com.samourai.wallet.R
import com.samourai.wallet.SamouraiActivity.CLIPBOARD_SERVICE
import com.samourai.wallet.databinding.BottomsheetPubkeySlidesBinding
import com.samourai.wallet.databinding.ItemPubkeySlideBinding
import com.samourai.wallet.util.func.FormatsUtil
import com.samourai.wallet.util.tech.SimpleCallback
import com.samourai.wallet.util.tech.SimpleTaskRunner

class PubkeyViewerFragment(val pubkeys: ArrayList<String>, val qrTitles: ArrayList<String>) : BottomSheetDialogFragment() {

    private var _binding: BottomsheetPubkeySlidesBinding? = null
    private val binding get() = _binding!!

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
        _binding = BottomsheetPubkeySlidesBinding.inflate(inflater, container, false)
        val view = binding.root

        return view
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        binding.pubkeysViewPager.adapter = ScreenSlidePagerAdapter(requireActivity(), pubkeys, qrTitles)
        binding.sliderPubkeys.setViewPager2(binding.pubkeysViewPager)

        view.post {
            val parent = view.parent as View
            val bottomSheetBehavior =
                BottomSheetBehavior.from(parent)

            val fixHeight = TypedValue.applyDimension(
                TypedValue.COMPLEX_UNIT_DIP, 552f + 68f, resources.displayMetrics
            ).toInt()
            parent.layoutParams.height = fixHeight
            parent.requestLayout()
            bottomSheetBehavior.setState(BottomSheetBehavior.STATE_EXPANDED)
        }
    }


    class ScreenSlidePagerAdapter(fa: FragmentActivity, val pubkeys: ArrayList<String>, val qrTitles: ArrayList<String>) : FragmentStateAdapter(fa) {
        override fun getItemCount(): Int = pubkeys.size
        override fun createFragment(position: Int) = OnBoardSliderItem.newInstance(position, pubkeys, qrTitles)
    }

    class OnBoardSliderItem(val pubkeys: ArrayList<String>, val qrTitles: ArrayList<String>) : Fragment() {
        private lateinit var binding: ItemPubkeySlideBinding

        private val qrCodes = getQRs(pubkeys)

        private val messages = getPubkeysShort(pubkeys)

        private fun getPubkeysShort(pubkeys: ArrayList<String>): ArrayList<String> {
            val shortedPubkeys = ArrayList<String>()
            for (pubkey in pubkeys) {
                val shortedPubkey = pubkey.substring(0, 13) + "..." + pubkey.substring(pubkey.length-13,pubkey.length)
                shortedPubkeys.add(shortedPubkey)
            }
            return shortedPubkeys
        }

        override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
            binding = ItemPubkeySlideBinding.inflate(inflater,container,false);
            return binding.root
        }

        override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
            super.onViewCreated(view, savedInstanceState)
            var positiion = -1
            if (qrTitles.filter{it.contains("Swaps")}.isNotEmpty())
                binding.titleBottomsheet.text = "Swaps accounts"
            else if (qrTitles.filter{it.contains("Deposit")}.isNotEmpty())
                binding.titleBottomsheet.text = "Deposit accounts"
            else if (qrTitles.filter{it.contains("Postmix")}.isNotEmpty())
                binding.titleBottomsheet.text = "Whirlpool accounts"
            else if (qrTitles.filter{it.contains("Bad Bank")}.isNotEmpty())
                binding.titleBottomsheet.text = "Bad Bank account"

            arguments?.takeIf { it.containsKey(POSITION) }?.apply {
                binding.pubkeyQRCode.setImageBitmap(qrCodes[this.getInt(POSITION)])
                binding.qrText.text = messages[this.getInt(POSITION)]
                binding.qrTitle.text =  qrTitles[this.getInt(POSITION)]
                positiion = this.getInt(POSITION)

                binding.qrDesc.text = getSummaryForPubAndNet(pubkeys[this.getInt(POSITION)], qrTitles[this.getInt(POSITION)])
            }

            binding.copyPubkey.setOnClickListener {
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
                                val clip: ClipData = ClipData.newPlainText("pubkey", pubkeys[positiion])
                                clipboard.setPrimaryClip(clip)
                                Toast.makeText(requireContext(), R.string.copied_to_clipboard, Toast.LENGTH_SHORT).show()
                                null
                            },
                            object : SimpleCallback<Void?> {
                            }
                        )
                    }.setNegativeButton(
                        R.string.no
                    ) { dialog, whichButton -> }.show()

            }
        }

        private fun getSummaryForPubAndNet(xpub: String, name: String): CharSequence {
            //Legacy postmix like-type
            if (name.lowercase().equals("postmix-change xpub")) {
                if (xpub.lowercase().startsWith("t")) {
                    return getString(R.string.deriving_liketype_legacy_testnet)
                }
                if (xpub.lowercase().startsWith("x")) {
                    return getString(R.string.deriving_liketype_legacy_mainnet)
                }
            }
            //Compat postmix like-type
            if (name.lowercase().equals("postmix-change ypub")) {
                if (xpub.lowercase().startsWith("u")) {
                    return getString(R.string.deriving_liketype_compat_testnet)
                }
                if (xpub.lowercase().startsWith("y")) {
                    return getString(R.string.deriving_liketype_compat_mainnet)
                }
            }

            // Segwit legacy texts
            if (xpub.lowercase().startsWith("t")) {
                return getString(R.string.deriving_legacy_testnet)
            }
            if (xpub.lowercase().startsWith("x")) {
                return getString(R.string.deriving_legacy_mainnet)
            }
            // Segwit compatible texts
            if (xpub.lowercase().startsWith("u")) {
                return getString(R.string.deriving_compat_testnet)
            }
            if (xpub.lowercase().startsWith("y")) {
                return getString(R.string.deriving_compat_mainnet)
            }
            // Segwit native texts
            if (xpub.lowercase().startsWith("v")) {
                return getString(R.string.deriving_segwit_testnet)
            }
            if (xpub.lowercase().startsWith("z")) {
                return getString(R.string.deriving_segwit_mainnet)
            }
            return getString(R.string.deriving_segwit_mainnet)
        }

        private fun getQRs(pubkeys: ArrayList<String>): ArrayList<Bitmap> {
            val pubkeysQRs = ArrayList<Bitmap>()
            for (pubkey in pubkeys) {
                val qrCodeEncoder = QRCodeEncoder(pubkey, null, Contents.Type.TEXT, BarcodeFormat.QR_CODE.toString(), 500)
                var bitmap: Bitmap? = null
                try {
                    bitmap = qrCodeEncoder.encodeAsBitmap()
                    pubkeysQRs.add(bitmap)
                } catch (e: WriterException) {
                    e.printStackTrace()
                }
            }
            return pubkeysQRs
        }

        companion object {
            const val POSITION = "POSITION"
            fun newInstance(position: Int, pubkeys: ArrayList<String>, qrTitles: ArrayList<String>): OnBoardSliderItem {
                return OnBoardSliderItem(pubkeys, qrTitles).apply {
                    this.arguments = Bundle().apply {
                        putInt(POSITION, position)
                    }
                }
            }
        }
    }

}