package com.samourai.wallet.settings

import android.content.Context
import android.content.Intent
import android.graphics.drawable.Drawable
import android.util.AttributeSet
import android.view.View
import android.widget.ImageView
import android.widget.Switch
import android.widget.TextView
import androidx.core.content.ContextCompat.getColor
import androidx.core.content.ContextCompat.startActivity
import androidx.lifecycle.LifecycleOwner
import androidx.lifecycle.Observer
import androidx.preference.Preference
import androidx.preference.PreferenceViewHolder
import com.google.android.material.switchmaterial.SwitchMaterial
import com.samourai.wallet.R
import com.samourai.wallet.access.AccessFactory
import com.samourai.wallet.payload.ExternalBackupManager
import com.samourai.wallet.payload.PayloadUtil
import com.samourai.wallet.stealth.StealthModeController
import com.samourai.wallet.stealth.StealthModeSettings
import com.samourai.wallet.util.CharSequenceX
import com.samourai.wallet.util.PrefsUtil

class CustomPreference @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : Preference(context, attrs, defStyleAttr) {

    private var isSwitchVisible: Boolean = false
    private var viewModel: CustomPreferenceViewModel? = null
    private var switchView: SwitchMaterial? = null
    private var isSwitchViewInitialized = false
    private var isViewModelInitialized = false
    private var pendingSwitchState: Boolean? = null
    private var isAutosavePref: Boolean = false


    init {
        layoutResource = R.xml.my_preference_layout
        attrs?.let {
            val typedArray = context.obtainStyledAttributes(it, R.styleable.CustomPreference, 0, 0)
            isSwitchVisible = typedArray.getBoolean(R.styleable.CustomPreference_isSwitch, false)
            isAutosavePref = typedArray.getBoolean(R.styleable.CustomPreference_isAutosave, false)
            typedArray.recycle()
        }
    }

    fun bindViewModel(viewModel: CustomPreferenceViewModel, lifecycleOwner: LifecycleOwner) {
        this.viewModel = viewModel
        isViewModelInitialized = true

        viewModel.isSwitchOn.observe(lifecycleOwner) { isOn ->
            if (isSwitchViewInitialized) {
                switchView?.isChecked = isOn
            } else {
                pendingSwitchState = isOn
            }
        }
    }

    override fun onBindViewHolder(holder: PreferenceViewHolder) {
        super.onBindViewHolder(holder)

        holder.itemView.findViewById<SwitchMaterial>(R.id.switch2).setOnClickListener {
                PrefsUtil.getInstance(context).setValue(
                    viewModel!!.prefToChange.value,
                    holder.itemView.findViewById<SwitchMaterial>(R.id.switch2).isChecked
                )
                PayloadUtil.getInstance(context).saveWalletToJSON(
                    CharSequenceX(
                        AccessFactory.getInstance(context).guid + AccessFactory.getInstance(context).pin
                    )
                )
        }

        switchView = holder.itemView.findViewById(R.id.switch2)
        isSwitchViewInitialized = true

        pendingSwitchState?.let {
            switchView?.isChecked = it
            pendingSwitchState = null
        } ?: run {
            if (isViewModelInitialized) {
                switchView?.isChecked = viewModel!!.isSwitchOn.value ?: false
            }
        }

        val titleView = holder.findViewById(R.id.title) as TextView
        titleView.text = title

        val summaryView = holder.findViewById(R.id.summary) as TextView
        val summary = summary
        if (!summary.isNullOrEmpty()) {
            summaryView.text = summary
            summaryView.visibility = View.VISIBLE
        } else {
            summaryView.visibility = View.GONE
        }

        val iconView = holder.findViewById(R.id.icon) as ImageView
        val icon: Drawable? = icon
        if (icon != null) {
            iconView.setImageDrawable(icon)
            iconView.visibility = View.VISIBLE
        } else {
            iconView.visibility = View.GONE
        }

        if (isSwitchVisible)
            switchView?.visibility = View.VISIBLE

        if (isAutosavePref) {
            val fileLocText = holder.findViewById(R.id.textviewFileLoc) as TextView
            val actualFileLoc = holder.findViewById(R.id.file_location_text) as TextView

            fileLocText.visibility = View.VISIBLE
            actualFileLoc.visibility = View.VISIBLE

            fileLocText.text = "File location:"
            val fileLocation = ExternalBackupManager.getBackUpURI()!!.uri.path
            actualFileLoc.text = fileLocation
        }
    }
}

