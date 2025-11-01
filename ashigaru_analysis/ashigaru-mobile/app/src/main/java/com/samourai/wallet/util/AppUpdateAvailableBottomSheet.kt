package com.samourai.wallet.util

import android.app.Dialog
import android.os.Bundle
import android.util.TypedValue
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.ViewTreeObserver
import android.widget.FrameLayout
import android.widget.ImageButton
import android.widget.LinearLayout
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.core.content.res.ResourcesCompat
import com.google.android.material.bottomsheet.BottomSheetBehavior
import com.google.android.material.bottomsheet.BottomSheetDialog
import com.google.android.material.bottomsheet.BottomSheetDialogFragment
import com.google.android.material.button.MaterialButton
import com.samourai.wallet.BuildConfig
import com.samourai.wallet.R
import com.samourai.wallet.SamouraiWallet
import com.samourai.wallet.util.AppUpdateAvailableBottomSheet.Companion.TAG_BOTTOM_SHEET_APP_UPDATE
import org.json.JSONArray


class AppUpdateAvailableBottomSheet(val latestVersion: String = "latestVersion") : BottomSheetDialogFragment() {

    companion object {
        const val TAG_BOTTOM_SHEET_APP_UPDATE = "BottomSheetAppUpdate"
        const val TAG_BOTTOM_SHEET_APP_RELEASE_NOTES = "BottomSheetAppReleaseNotes"
    }

    private var fragmentHeight: Int = 0

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

        val view = inflater.inflate(R.layout.update_available_content, container, false)

        val notesBtn = view.findViewById<MaterialButton>(R.id.notesBtn)
        view.findViewById<TextView>(R.id.tvLatestVersion).text = latestVersion
        view.findViewById<TextView>(R.id.tvCurrentVersion).text = "v${BuildConfig.VERSION_NAME}"

        notesBtn.text = "Show $latestVersion release notes"
        notesBtn.setOnClickListener {
            dismiss()
            val releaseNotesFragment = ReleaseNotesBottomSheet(fragmentHeight)
            releaseNotesFragment.show(parentFragmentManager, TAG_BOTTOM_SHEET_APP_RELEASE_NOTES)
        }

        view.viewTreeObserver.addOnGlobalLayoutListener(object : ViewTreeObserver.OnGlobalLayoutListener {
            override fun onGlobalLayout() {
                fragmentHeight = view.height
                view.viewTreeObserver.removeOnGlobalLayoutListener(this)
            }
        })

        return view
    }
}

class ReleaseNotesBottomSheet(private val fragmentHeight: Int)
    : BottomSheetDialogFragment() {

    val releaseNotes = SamouraiWallet.getInstance().releaseNotes
    private var containerImportantItems: LinearLayout? = null
    private var containerNewItems: LinearLayout? = null
    private var containerUpdatesItems: LinearLayout? = null
    private var containerFixesItems: LinearLayout? = null
    private var containerOtherItems: LinearLayout? = null
    private var appVersionText: TextView? = null

    override fun onCreateDialog(savedInstanceState: Bundle?): Dialog {
        val releaseNotesDialog = super.onCreateDialog(savedInstanceState) as BottomSheetDialog
        releaseNotesDialog.setOnShowListener { dialog ->
            val bottomSheet = (dialog as BottomSheetDialog).findViewById<View>(com.google.android.material.R.id.design_bottom_sheet) as FrameLayout?
            bottomSheet?.background = ContextCompat.getDrawable(requireContext(), R.drawable.rounded_rectangle_bottom_sheet)
            bottomSheet?.let {
                val behavior = BottomSheetBehavior.from(it)
                behavior.peekHeight = fragmentHeight
                behavior.maxHeight = fragmentHeight
            }
        }
        return releaseNotesDialog
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.release_notes_content, container, false)
        val backButton = view.findViewById<ImageButton>(R.id.notes_button_back)
        containerImportantItems = view.findViewById(R.id.containerImportantItems);
        containerNewItems = view.findViewById(R.id.containerNewItems);
        containerUpdatesItems = view.findViewById(R.id.containerUpdatesItems);
        containerFixesItems = view.findViewById(R.id.containerFixesItems);
        containerOtherItems = view.findViewById(R.id.containerOtherItems);
        appVersionText = view.findViewById(R.id.notes_version)
        backButton.setOnClickListener {
            dismiss()
            val AppUpdateAvailableFragment = AppUpdateAvailableBottomSheet(SamouraiWallet.getInstance().releaseNotes.getString("version"))
            AppUpdateAvailableFragment.show(parentFragmentManager, TAG_BOTTOM_SHEET_APP_UPDATE)
        }
        addReleaseNotes(view)
        return view
    }

    private fun addReleaseNotes(view: View) {
        if (releaseNotes == null)
            return

        appVersionText!!.text = releaseNotes.getString("version")

        val importantArray = if (releaseNotes.getJSONObject("notes").has("important"))
            releaseNotes.getJSONObject("notes").getJSONArray("important")
        else
            JSONArray()

        val newArray = if (releaseNotes.getJSONObject("notes").has("new"))
            releaseNotes.getJSONObject("notes").getJSONArray("new")
        else
            JSONArray()
        val updatesArray = if (releaseNotes.getJSONObject("notes").has("updates"))
            releaseNotes.getJSONObject("notes").getJSONArray("updates")
        else
            JSONArray()
        val fixesArray = if (releaseNotes.getJSONObject("notes").has("fixes"))
            releaseNotes.getJSONObject("notes").getJSONArray("fixes")
        else
            JSONArray()

        val otherArray = if (releaseNotes.getJSONObject("notes").has("other"))
            releaseNotes.getJSONObject("notes").getJSONArray("other")
        else
            JSONArray()

        if (importantArray.length() == 0) {
            view.findViewById<TextView>(R.id.notes_rel_notes_important).visibility = View.GONE
            view.findViewById<LinearLayout>(R.id.containerImportantItems).visibility = View.GONE
        }

        if (newArray.length() == 0) {
            view.findViewById<TextView>(R.id.notes_rel_notes_new).visibility = View.GONE
            view.findViewById<LinearLayout>(R.id.containerNewItems).visibility = View.GONE
        }

        if (updatesArray.length() == 0) {
            view.findViewById<TextView>(R.id.notes_rel_notes_update).visibility = View.GONE
            view.findViewById<LinearLayout>(R.id.containerUpdatesItems).visibility = View.GONE
        }

        if (fixesArray.length() == 0) {
            view.findViewById<TextView>(R.id.notes_rel_notes_fixes).visibility = View.GONE
            view.findViewById<LinearLayout>(R.id.containerFixesItems).visibility = View.GONE
        }

        if (otherArray.length() == 0) {
            view.findViewById<TextView>(R.id.notes_rel_notes_other).visibility = View.GONE
            view.findViewById<LinearLayout>(R.id.containerOtherItems).visibility = View.GONE
        }

        for (i in 0 until importantArray.length()) {
            val important = importantArray.getString(i)
            addTextView(important, containerImportantItems!!)
        }

        for (i in 0 until newArray.length()) {
            val newFeature = newArray.getString(i)
            addTextView(newFeature, containerNewItems!!)
        }

        for (i in 0 until updatesArray.length()) {
            val update = updatesArray.getString(i)
            addTextView(update, containerUpdatesItems!!)
        }

        for (i in 0 until fixesArray.length()) {
            val fix = fixesArray.getString(i)
            addTextView(fix, containerFixesItems!!)
        }

        for (i in 0 until otherArray.length()) {
            val other = otherArray.getString(i)
            addTextView(other, containerOtherItems!!)
        }
    }

    private fun addTextView(newFeature: String,  container: LinearLayout) {
        val textView = TextView(context)

        textView.setTextSize(TypedValue.COMPLEX_UNIT_SP, 14f)
        if (container.equals(containerImportantItems))
            textView.setTextColor(ContextCompat.getColor(requireContext(), R.color.samourai_alert))
        else
            textView.setTextColor(ContextCompat.getColor(requireContext(), R.color.white_too))
        textView.typeface = ResourcesCompat.getFont(requireContext(), R.font.roboto_medium)

        val params = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.WRAP_CONTENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        )
        params.setMargins(0, 5, 0, 0)

        textView.layoutParams = params

        if (newFeature.startsWith("Note:"))
            textView.text = newFeature
        else
            textView.text = "• $newFeature"

        container.addView(textView)
    }
}