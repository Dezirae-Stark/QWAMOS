package com.samourai.wallet.network.dojo

import android.app.AlertDialog
import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.graphics.Bitmap
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.WindowManager
import android.widget.ImageView
import android.widget.TextView
import android.widget.Toast
import com.google.android.material.bottomsheet.BottomSheetDialogFragment
import com.google.android.material.imageview.ShapeableImageView
import com.google.zxing.BarcodeFormat
import com.google.zxing.WriterException
import com.google.zxing.client.android.Contents
import com.google.zxing.client.android.encode.QRCodeEncoder
import com.samourai.wallet.R

class DojoQRBottomsheet(val qrData: String, val title: String? = "", val clipboardLabel: String? = "") : BottomSheetDialogFragment() {


    //secure flag to dialogs window
    private var secure: Boolean = false;

    override fun onCreateView(
            inflater: LayoutInflater,
            container: ViewGroup?,
            savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_dojo_bottomsheet, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val qrDialogTitle = view.findViewById<TextView>(R.id.qrDialogTitle);
        val qRImage = view.findViewById<ShapeableImageView>(R.id.imgQrCode);
        val copyBtn = view.findViewById<ImageView>(R.id.qrCopyIcon)

        title?.let {
            qrDialogTitle.text = title
        }
        var bitmap: Bitmap? = null
        val qrCodeEncoder = QRCodeEncoder(qrData, null, Contents.Type.TEXT, BarcodeFormat.QR_CODE.toString(), 500)
        try {
            bitmap = qrCodeEncoder.encodeAsBitmap()
        } catch (e: WriterException) {
            e.printStackTrace()
        }

        val radius = resources.getDimension(R.dimen.qr_image_corner_radius)

        qRImage.shapeAppearanceModel = qRImage.shapeAppearanceModel
                .toBuilder()
                .setAllCornerSizes(radius)
                .build()
        view.findViewById<ImageView>(R.id.imgQrCode).setImageBitmap(bitmap)

        copyBtn.setOnClickListener {
            AlertDialog.Builder(requireContext())
                .setTitle(R.string.app_name)
                .setMessage(R.string.receive_dojo_pairing_to_clipboard)
                .setCancelable(false)
                .setPositiveButton(
                    R.string.yes
                ) { dialog, whichButton ->
                    val clipboard =
                        requireContext().getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                    var clip: ClipData? = null
                    clip = ClipData.newPlainText("Dojo Payload", qrData)
                    clipboard.setPrimaryClip(clip)
                    Toast.makeText(
                        requireContext(),
                        R.string.copied_to_clipboard,
                        Toast.LENGTH_SHORT
                    ).show()
                }.setNegativeButton(
                    R.string.no
                ) { dialog, whichButton -> }.show()


        }

        if(secure){
            this.dialog?.window?.setFlags(WindowManager.LayoutParams.FLAG_SECURE, WindowManager.LayoutParams.FLAG_SECURE)
        }

    }

    fun setSecure(secure: Boolean){
        this.secure =secure
    }
}