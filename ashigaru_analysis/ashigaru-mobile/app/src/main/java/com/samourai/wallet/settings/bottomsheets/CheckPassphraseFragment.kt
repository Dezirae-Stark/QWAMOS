package com.samourai.wallet.settings.bottomsheets

import android.app.Dialog
import android.content.res.ColorStateList
import android.graphics.PorterDuff
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.WindowManager
import android.widget.EditText
import android.widget.FrameLayout
import android.widget.TextView
import android.widget.Toast
import androidx.core.content.ContextCompat
import androidx.core.graphics.drawable.toDrawable
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import androidx.viewpager2.adapter.FragmentStateAdapter
import com.google.android.material.bottomsheet.BottomSheetDialog
import com.google.android.material.bottomsheet.BottomSheetDialogFragment
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText
import com.samourai.wallet.R
import com.samourai.wallet.databinding.FragmentBottomsheetViewPagerBinding
import com.samourai.wallet.databinding.LayoutErrorBottomBinding
import com.samourai.wallet.databinding.LayoutLoadingBottomBinding
import com.samourai.wallet.hd.HD_WalletFactory
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.plus


class CheckPassphraseFragment() : BottomSheetDialogFragment() {

    private var _binding: FragmentBottomsheetViewPagerBinding? = null
    private val binding get() = _binding!!
    private val scope = CoroutineScope(Dispatchers.IO) + SupervisorJob()
    private val passwordFragment = EnterPassphrase()
    private val loadingFragment = LoadingFragmentPassphrase()
    private val successFragment = SuccessFragmentPassphras()
    private val errorFragment = ErrorFragmentPassphrase()


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

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        setUpViewPager()
        this.dialog?.window?.setFlags(WindowManager.LayoutParams.FLAG_SECURE, WindowManager.LayoutParams.FLAG_SECURE)

        passwordFragment.setOnClickListener {
            binding.pager.currentItem = 1
        }
        loadingFragment.setSuccessCheck {
            scope.launch {
                delay(3000)
                try {
                    val actualPassphrase = HD_WalletFactory.getInstance(requireContext()).get().passphrase

                    if (passwordFragment.passphraseText.text.toString().equals(actualPassphrase))
                        binding.pager.currentItem = 2
                    else
                        binding.pager.currentItem = 3
                } catch (ex: Exception) {
                    binding.pager.currentItem = 3
                }
            }
        }
        errorFragment.setOnTryAgainListener {
            this.dismiss()
            val dialog = CheckPassphraseFragment()
            dialog.show(requireFragmentManager(), dialog.tag)
        }
    }

    private fun setUpViewPager() {

        val item = arrayListOf<Fragment>()
        item.add(passwordFragment)
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
}

class EnterPassphrase : Fragment() {

    private var onSelect: (View) -> Unit = {}
    lateinit var passphraseText: EditText

    fun setOnClickListener(callback: (View) -> Unit) {
        this.onSelect = callback
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_test_backup_bottomsheet, container)
        return view
    }

    override fun onActivityCreated(savedInstanceState: Bundle?) {
        super.onActivityCreated(savedInstanceState)
        view?.findViewById<TextView>(R.id.titleBottomsheet)!!.text = getString(R.string.check_bip39)
        view?.findViewById<MaterialButton>(R.id.test_button)!!.text = "Check"

        passphraseText = view?.findViewById(R.id.passphrase_text)!!;
        val testBtn = view?.findViewById<MaterialButton>(R.id.test_button)

        testBtn!!.setOnClickListener(onSelect)
    }
}

class LoadingFragmentPassphrase : Fragment() {

    private var _binding: LayoutLoadingBottomBinding? = null
    private val binding get() = _binding!!
    private var onSelect: () -> Unit = {}


    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = LayoutLoadingBottomBinding.inflate(inflater, container, false)
        val view = binding.root
        return view
    }


    fun setSuccessCheck(callback: () -> Unit = {}) {
        this.onSelect = callback
    }

    override fun onActivityCreated(savedInstanceState: Bundle?) {
        super.onActivityCreated(savedInstanceState)
        binding.titleBottomsheet.text = getString(R.string.check_bip39)
        binding.broadcastProgress.visibility = View.VISIBLE
        binding.successfulVerificatin.visibility = View.GONE
        binding.loadingImage.visibility = View.VISIBLE
        binding.loadingImage.background = ContextCompat.getColor(requireContext(), R.color.white_flojo).toDrawable()
        val drawable = ContextCompat.getDrawable(requireContext(), R.drawable.circle_background)
        drawable?.mutate()?.setTint(ContextCompat.getColor(requireContext(), R.color.white_flojo))

        binding.circleImage.background = drawable

        lifecycleScope.launch(Dispatchers.Main) {
            try {
                delay(3000)

                onSelect()
            } catch (e: Exception) {
                println("Error: ${e.message}")
            }
        }
    }
}

class SuccessFragmentPassphras : Fragment() {

    private var _binding: LayoutLoadingBottomBinding? = null
    private val binding get() = _binding!!
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = LayoutLoadingBottomBinding.inflate(inflater, container, false)
        binding.titleBottomsheet.text = getString(R.string.check_bip39)
        val view = binding.root
        return view
    }

    override fun onActivityCreated(savedInstanceState: Bundle?) {
        super.onActivityCreated(savedInstanceState)
        binding.successCheck.visibility = View.VISIBLE
        binding.successCheck.setColorFilter(getResources().getColor(R.color.networking), PorterDuff.Mode.SRC_IN);
        binding.broadcastProgress.visibility = View.GONE
    }
}

class ErrorFragmentPassphrase : Fragment() {

    private lateinit var onSelect: (View) -> Unit
    private var _binding: LayoutErrorBottomBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = LayoutErrorBottomBinding.inflate(inflater, container, false)
        val view = binding.root
        return view
    }

    fun setOnTryAgainListener(callback: (View) -> Unit) {
        this.onSelect = callback
    }

    override fun onActivityCreated(savedInstanceState: Bundle?) {
        super.onActivityCreated(savedInstanceState)
        binding.titleBottomsheet.text = getString(R.string.check_bip39)
        binding.successCheck.visibility = View.VISIBLE
        binding.errorMessage.text = getString(R.string.passphrase_error_message)
        binding.checkPassIndepen.visibility = View.GONE
        binding.tryAgainBtn.setOnClickListener(onSelect)
    }
}