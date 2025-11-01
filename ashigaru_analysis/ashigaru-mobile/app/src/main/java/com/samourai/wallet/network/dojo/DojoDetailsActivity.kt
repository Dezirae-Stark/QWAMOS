package com.samourai.wallet.network.dojo

import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.View
import android.view.ViewGroup
import android.view.inputmethod.InputMethodManager
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.transition.TransitionManager
import com.samourai.wallet.R
import com.samourai.wallet.api.APIFactory
import com.samourai.wallet.databinding.ActivityDojoDetailsBinding
import com.samourai.wallet.util.PrefsUtil
import com.samourai.wallet.util.network.ConnectivityStatus
import com.samourai.wallet.util.tech.AppUtil


class DojoDetailsActivity : AppCompatActivity() {

    private lateinit var binding: ActivityDojoDetailsBinding
    var activeColor: Int = 0
    var disabledColor:Int = 0
    var waiting:Int = 0


    enum class CONNECTION_STATUS {
        ENABLED, DISABLED, CONFIGURE, WAITING
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityDojoDetailsBinding.inflate(layoutInflater)
        setContentView(binding.root)
        binding.toolbar.setNavigationIcon(R.drawable.ic_baseline_arrow_back_24)
        binding.toolbar.setNavigationOnClickListener {
            super.onBackPressed()
        }
        window.statusBarColor = ContextCompat.getColor(this, R.color.toolbar);
        window.navigationBarColor = ContextCompat.getColor(this, R.color.networking)


        activeColor = ContextCompat.getColor(this, R.color.green_ui_2)
        disabledColor = ContextCompat.getColor(this, R.color.disabledRed)
        waiting = ContextCompat.getColor(this, R.color.warning_yellow)

        setDataState()

        AppUtil.getInstance(applicationContext).offlineStateLive().observe(
            this
        ) { aBoolean: Boolean? -> setDataState() }

        val dojoName =
            if (!PrefsUtil.getInstance(getApplicationContext()).getValue(PrefsUtil.DOJO_NAME, "").isEmpty())
                PrefsUtil.getInstance(getApplicationContext()).getValue(PrefsUtil.DOJO_NAME, "")
            else
                "My Dojo"

        binding.dojoName.text = Editable.Factory.getInstance().newEditable(dojoName.toString())


        binding.showPairingCreds.setOnClickListener {
            val dialog = DojoQRBottomsheet(
                DojoUtil.getInstance(applicationContext).toJSON().toString(),
                "${dojoName} pairing credentials",
                "dojo_credentials"
            )
            dialog.setSecure(true)
            dialog.show(supportFragmentManager, dialog.tag)
        }

        binding.dojoName.addTextChangedListener(object : TextWatcher {
            override fun afterTextChanged(s: Editable?) {
                // Called after the text has been changed
            }

            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {
                // Called before the text is about to be changed
            }

            override fun onTextChanged(newName: CharSequence?, start: Int, before: Int, count: Int) {
                val originalName = PrefsUtil.getInstance(applicationContext).getValue(PrefsUtil.DOJO_NAME, "")
                if (originalName.equals(newName) || newName.isNullOrEmpty())
                    binding.saveDojoName.visibility = View.INVISIBLE
                else
                    binding.saveDojoName.visibility = View.VISIBLE

            }
        })

        binding.saveDojoName.setOnClickListener {
            if (binding.saveDojoName.visibility == View.VISIBLE) {
                hidekeyboard()
                binding.dojoName.clearFocus()
                PrefsUtil.getInstance(applicationContext).setValue(PrefsUtil.DOJO_NAME, binding.dojoName.text.toString())
                binding.saveDojoName.visibility = View.INVISIBLE
                Toast.makeText(this, "Dojo name changed", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun setDataState() {
        if (ConnectivityStatus.hasConnectivity(applicationContext)) {
            setDataConnectionState(CONNECTION_STATUS.ENABLED)
        } else {
            setDataConnectionState(CONNECTION_STATUS.DISABLED)
        }
    }

    fun hidekeyboard() {
        val view = this.currentFocus
        if (view != null) {
            val imm = getSystemService(INPUT_METHOD_SERVICE) as InputMethodManager
            imm.hideSoftInputFromWindow(view.windowToken, 0)
        }
    }

    private fun setDataConnectionState(enabled: CONNECTION_STATUS) {
        this@DojoDetailsActivity.runOnUiThread(Runnable {
            if (enabled == CONNECTION_STATUS.ENABLED) {
                showOfflineMessage(false)
                binding.dojoStatusIcon.setColorFilter(activeColor)
                binding.blockHeightText.text =
                    APIFactory.getInstance(applicationContext).latestBlockHeight.toString();
                binding.dojoConnectionText.text = "Connected"

            } else {
                showOfflineMessage(true)
                binding.dojoStatusIcon.setColorFilter(disabledColor)
                binding.blockHeightText.text = "unknown"
                binding.dojoConnectionText.text = "Not reachable"
            }
        })
    }

    private fun showOfflineMessage(show: Boolean) {
        TransitionManager.beginDelayedTransition((binding.dojoNotReachableMessage.getRootView() as ViewGroup))
        binding.dojoNotReachableMessage.setVisibility(if (show) View.VISIBLE else View.GONE)
    }
}