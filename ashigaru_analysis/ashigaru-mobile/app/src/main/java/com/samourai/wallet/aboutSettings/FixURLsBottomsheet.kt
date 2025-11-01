package com.samourai.wallet.aboutSettings

import android.app.Dialog
import android.content.DialogInterface
import android.graphics.PorterDuff
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.FrameLayout
import androidx.core.content.ContextCompat
import androidx.core.graphics.drawable.toDrawable
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.viewpager2.adapter.FragmentStateAdapter
import com.google.android.material.bottomsheet.BottomSheetDialog
import com.google.android.material.bottomsheet.BottomSheetDialogFragment
import com.samourai.wallet.R
import com.samourai.wallet.databinding.FragmentBottomsheetViewPagerBinding
import com.samourai.wallet.databinding.FragmentInfoUrlsBinding
import com.samourai.wallet.databinding.FragmentLoadingFixUrlsBinding
import com.samourai.wallet.databinding.LayoutErrorBottomBinding
import com.samourai.wallet.databinding.LayoutLoadingBottomBinding
import com.samourai.wallet.util.URLUpdater.HandlerURLs
import com.samourai.wallet.util.URLUpdater.HandlerURLs.ASHIGARU_PUB_KEY2
import com.samourai.wallet.util.URLUpdater.URLFileUtil
import com.samourai.wallet.util.tech.AppUtil
import com.samourai.wallet.util.tech.VerifyPGPSignedClearMessageUtil
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.plus
import org.apache.commons.lang3.StringUtils
import org.apache.commons.lang3.StringUtils.defaultString


class FixURLsBottomsheet(val pgpMessage: String, val callback: Runnable) : BottomSheetDialogFragment() {

    private var _binding: FragmentBottomsheetViewPagerBinding? = null
    private val binding get() = _binding!!
    private val scope = CoroutineScope(Dispatchers.IO) + SupervisorJob()
    private val loadingFragment = LoadingFragment()
    private val successFragment = SuccessFragment()
    private val errorFragment = ErrorFragment()
    private val infoFragment = InfoFragment()

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
        _binding = FragmentBottomsheetViewPagerBinding.inflate(inflater, container, false)
        val view = binding.root
        return view
    }

    override fun onDismiss(dialog: DialogInterface) {
        super.onDismiss(dialog)
        callback.run()
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        setUpViewPager()
        binding.pager.currentItem = 1
        loadingFragment.setSuccessCheck {
            scope.launch {
                try {
                    val returnCode = checkForAppUpdates(pgpMessage);
                    if (returnCode == 0) { // Success
                        delay(4500)
                        binding.pager.currentItem = 2
                    }
                    else if (returnCode == 1) {
                        delay(4500)
                        infoFragment.setMessageText(getString(R.string.app_same_version))
                        binding.pager.currentItem = 0
                    } else if (returnCode == 2) {
                        delay(4500)
                        infoFragment.setMessageText(getString(R.string.app_higher_version))
                        binding.pager.currentItem = 0
                    } else { //Error
                        delay(2500)
                        binding.pager.currentItem = 3
                    }
                } catch (ex: Exception) {
                    delay(2500)
                    binding.pager.currentItem = 3
                }
            }
        }

        errorFragment.setOnTryAgainBtn {
            this.dismiss()
            val dialog = URLFixInfo()
            dialog.show(requireFragmentManager(), dialog.tag)
        }
    }

    private fun setUpViewPager() {

        val item = arrayListOf<Fragment>()
        item.add(infoFragment)
        item.add(loadingFragment)
        item.add(successFragment)
        item.add(errorFragment)

        binding.pager.adapter = object : FragmentStateAdapter(this) {
            override fun getItemCount(): Int {
                return item.size
            }

            override fun createFragment(position: Int): Fragment {
                return item[position]
            }

        }
        binding.pager.isUserInputEnabled = false
    }

    private fun checkForAppUpdates(pgpMessage: String): Int {
        try {
                if (!VerifyPGPSignedClearMessageUtil.verifySignedMessage(defaultString(pgpMessage).trim(), ASHIGARU_PUB_KEY2))
                    return -1 //not signed pgp message

                val handlerURLs = HandlerURLs.getInstance(requireContext())
                handlerURLs.setPgpMessage(pgpMessage)
                val highestPgpVersion = Integer.parseInt(StringUtils.substringBetween(
                    pgpMessage,
                    "pgp_signed_message_version=",
                    "\n"
                ).trim());
                val currentPgpVersion = (URLFileUtil.getInstance(requireContext())
                    .getValue("pgp_signed_message_version") as String).toInt()

                if (currentPgpVersion == highestPgpVersion) return 1 // Your app version is the same as pgp message
                if (currentPgpVersion > highestPgpVersion) return 2 // Your app version is higher than pgp message

                //If current PGP version is lower than the version retrieved from the signed pgp messages:
                // Overwrite PGP_MESSAGE_URLs and ZIP_CODE_URLs --> updatePgpAndCodeURLs()
                handlerURLs.updatePgpAndCodeURLs()
                // Check for new version of the app itself
                val showUpdate = handlerURLs.isAppUpdateAvailable
                // Check versions for paynym, soroban and ashigaru URLs
                handlerURLs.updatePaynymURL()
                handlerURLs.updateSorobanURL()
                handlerURLs.updateAshigaruSiteURL()
                URLFileUtil.getInstance(requireContext()).setPaynymAndSorobanUrls()

                // If there is no update available, then update pgp message version
                if (!showUpdate) {
                    handlerURLs.updatePgpSignedMessageVersion(highestPgpVersion.toString())
                }

                AppUtil.getInstance(requireContext()).setHasUpdateBeenShown(!showUpdate)
            } catch (e: java.lang.Exception) {
                e.printStackTrace()
                return -1
            }
        return 0
    }
}

class LoadingFragment : Fragment() {

    private var _binding: FragmentLoadingFixUrlsBinding? = null
    private val binding get() = _binding!!
    private var onSelect: () -> Unit = {}


    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentLoadingFixUrlsBinding.inflate(inflater, container, false)
        val view = binding.root
        return view
    }


    fun setSuccessCheck(callback: () -> Unit = {}) {
        this.onSelect = callback
    }

    override fun onActivityCreated(savedInstanceState: Bundle?) {
        super.onActivityCreated(savedInstanceState)
        binding.broadcastProgress.visibility = View.VISIBLE
        binding.loadingImage.visibility = View.VISIBLE
        binding.successfulVerificatin.visibility = View.GONE
        binding.loadingImage.background = ContextCompat.getColor(requireContext(), R.color.white_flojo).toDrawable()

        val drawable = ContextCompat.getDrawable(requireContext(), R.drawable.circle_background)
        drawable?.mutate()?.setTint(ContextCompat.getColor(requireContext(), R.color.white_flojo))
        binding.circleImage.background = drawable

        lifecycleScope.launch(Dispatchers.Main) {
            try {
                onSelect()
            } catch (e: Exception) {
                println("Error: ${e.message}")
            }
        }
    }
}

class SuccessFragment : Fragment() {

    private var _binding: LayoutLoadingBottomBinding? = null
    private val binding get() = _binding!!
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = LayoutLoadingBottomBinding.inflate(inflater, container, false)
        binding.titleBottomsheet.text = getString(R.string.fix_orphaned_urls)
        val view = binding.root
        return view
    }

    override fun onActivityCreated(savedInstanceState: Bundle?) {
        super.onActivityCreated(savedInstanceState)
        binding.successCheck.visibility = View.VISIBLE
        binding.broadcastProgress.visibility = View.GONE
        binding.successfulVerificatin.text = "URLs and versions successfully updated"
        binding.successCheck.setColorFilter(getResources().getColor(R.color.networking), PorterDuff.Mode.SRC_IN);
    }
}

class ErrorFragment : Fragment() {

    private var onSelect2: (View) -> Unit = {}
    private var _binding: LayoutErrorBottomBinding? = null
    private val binding get() = _binding!!
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = LayoutErrorBottomBinding.inflate(inflater, container, false)
        binding.titleBottomsheet.text = getString(R.string.fix_orphaned_urls)
        binding.unsuccessfulVerificatin.text = getString(R.string.pgp_message_verification_failed)
        val view = binding.root
        return view
    }

    fun setOnTryAgainBtn(callback: (View) -> Unit) {
        this.onSelect2 = callback
    }

    override fun onActivityCreated(savedInstanceState: Bundle?) {
        super.onActivityCreated(savedInstanceState)
        binding.successCheck.visibility = View.VISIBLE
            binding.errorMessage.text = getString(R.string.the_text_provided_does_not_contain)
        binding.checkPassIndepen.visibility = View.GONE

        binding.tryAgainBtn.setOnClickListener(onSelect2)

    }
}

class InfoFragment : Fragment() {

    private var _binding: FragmentInfoUrlsBinding? = null
    private val binding get() = _binding!!
    private var onSelect: () -> Unit = {}


    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentInfoUrlsBinding.inflate(inflater, container, false)
        val view = binding.root
        return view
    }

    override fun onActivityCreated(savedInstanceState: Bundle?) {
        super.onActivityCreated(savedInstanceState)

        lifecycleScope.launch(Dispatchers.Main) {
            try {
                onSelect()
            } catch (e: Exception) {
                println("Error: ${e.message}")
            }
        }
    }

    fun setMessageText(string: String) {
        binding.infoMessage.text = string
    }
}