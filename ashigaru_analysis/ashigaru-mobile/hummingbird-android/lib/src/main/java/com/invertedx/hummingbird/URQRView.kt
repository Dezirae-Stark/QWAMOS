package com.invertedx.hummingbird


import android.content.Context
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Rect
import android.util.AttributeSet
import android.view.View
import com.google.zxing.BarcodeFormat
import com.invertedx.hummingbird.encoder.Contents
import com.invertedx.hummingbird.encoder.encode.QRCodeEncoder
import com.sparrowwallet.hummingbird.UR
import com.sparrowwallet.hummingbird.UREncoder
import com.sparrowwallet.hummingbird.registry.RegistryType
import kotlinx.coroutines.*
import java.nio.charset.Charset


//Draws animated QR codes
class URQRView : View {

    private var _minFragmentLength = 10
    private var _maxFragmentLength = 100
    private var _currentFrame = 0
    private var _qrMargin = 1
    private var qrRect = Rect(0, 0, width, height)
    private var _job: Job? = null
    private val bitmapList = arrayListOf<Bitmap?>()
    private var _fps = 12
    private var _ur: UR? = null
    private var _content: String = ""
    private var scope = CoroutineScope(Dispatchers.Unconfined) + SupervisorJob()
    private var urTransmissionListener: (totalFrames: Int, currentFrame: Int) -> Unit = { _, _ -> }

    var fps: Int?
        get() = _fps
        set(value) {
            if (value != null) {
                _fps = value
                restart()
            }
        }


    var maxFragmentLength: Int?
        get() = _maxFragmentLength
        set(value) {
            if (value != null) {
                _maxFragmentLength = value
                makeUR()
            }
        }

    var content: String?
        get() = _content
        set(value) {
            if (value != null) {
                _content = value
                this._ur = UR.fromBytes(_content.toByteArray())
                makeUR()
            }
        }


    var qrMargin: Int?
        get() = _qrMargin
        set(value) {
            if (value != null) {
                _qrMargin = value
                makeUR()
            }
        }

    fun setContent(type: RegistryType, content: String) {
        this._ur = UR.fromBytes(type.type, content.toByteArray())
        this._content = content
        this.makeUR()
    }

    fun getUR(): UR? {
        return this._ur
    }

    fun setContent(ur: UR) {
        this._ur = ur
        this._content = ur.toBytes().decodeToString()
        this.makeUR()
    }

    var minFragmentLength: Int?
        get() = _minFragmentLength
        set(value) {
            if (value != null) {
                _minFragmentLength = value
                makeUR()
            }
        }

    fun setUrTransmissionListener(callback: (totalFrames: Int, currentFrame: Int) -> Unit) {
        this.urTransmissionListener = callback
    }

    constructor(context: Context) : super(context) {
        init(null, 0)
    }

    constructor(context: Context, attrs: AttributeSet) : super(context, attrs) {
        init(attrs, 0)
    }

    constructor(context: Context, attrs: AttributeSet, defStyle: Int) : super(
        context,
        attrs,
        defStyle
    ) {
        init(attrs, defStyle)
    }


    private fun init(attrs: AttributeSet?, defStyle: Int) {
        val a = context.obtainStyledAttributes(
            attrs, R.styleable.URQRView, defStyle, 0
        )
        _qrMargin = a.getInt(R.styleable.URQRView_margin, 1)
        a.getString(R.styleable.URQRView_qrcontent)?.let {
            _content = it
            this._ur = UR.fromBytes(it.toByteArray())
        }
        _fps = a.getInt(R.styleable.URQRView_fps, 12)
        a.recycle()
        makeUR()
    }


    //calculates the QR frames and create QR bitmaps
    private fun makeUR() {
        CoroutineScope(Dispatchers.Unconfined).launch {
            stopLoop()
            bitmapList.clear()
            if (_ur == null) {
                return@launch
            }
            val encoder = UREncoder(_ur, _maxFragmentLength, _minFragmentLength, 0)
            if (encoder.isSinglePart) {
                val qrCodeEncoder = QRCodeEncoder(
                    _ur?.toBytes()?.toString(Charset.defaultCharset()),
                    null,
                    Contents.Type.TEXT,
                    BarcodeFormat.QR_CODE.toString(),
                    width,
                    1
                )
                bitmapList.add(qrCodeEncoder.encodeAsBitmap())
            } else {
                while (!encoder.isComplete) {
                    val qrCodeEncoder = QRCodeEncoder(
                        encoder.nextPart(),
                        null,
                        Contents.Type.TEXT,
                        BarcodeFormat.QR_CODE.toString(),
                        width,
                        _qrMargin
                    )
                    bitmapList.add(qrCodeEncoder.encodeAsBitmap())
                }
            }
            startLoop()
        }
    }

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        qrRect = Rect(0, 0, width, height)
    }

    private fun startLoop() {
        if (bitmapList.size == 1) {
            invalidate()
            return
        }
        _job = scope.launch {
            while (scope.isActive) {
                delay((1000 / _fps).toLong())
                if (bitmapList.size == _currentFrame + 1) {
                    _currentFrame = 0
                } else {
                    _currentFrame += 1
                }
                withContext(Dispatchers.Main) {
                    urTransmissionListener.invoke(bitmapList.size, _currentFrame)
                    invalidate()
                }
            }
        }
    }

    private fun restart() {
        stopLoop()
        startLoop()
    }

    private fun stopLoop() {
        _job?.cancel()
        _currentFrame = 0
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        if (bitmapList.isNotEmpty()) {
            bitmapList[_currentFrame]?.let { canvas.drawBitmap(it, null, qrRect, null) }
        }
    }

    override fun onDetachedFromWindow() {
        _job?.cancel()
        super.onDetachedFromWindow()
    }

    companion object {
        private const val TAG = "URQRView"
    }
}