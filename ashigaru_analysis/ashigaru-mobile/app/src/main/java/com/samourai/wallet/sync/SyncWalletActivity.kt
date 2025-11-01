package com.samourai.wallet.sync

import android.content.Intent
import android.os.Bundle
import android.view.WindowManager
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.AnimationVector1D
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.ScrollState
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.livedata.observeAsState
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.tooling.preview.PreviewParameter
import androidx.compose.ui.tooling.preview.PreviewParameterProvider
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.samourai.wallet.R
import com.samourai.wallet.SamouraiActivity
import com.samourai.wallet.bip47.BIP47Util
import com.samourai.wallet.home.BalanceActivity
import com.samourai.wallet.home.TestApplication
import com.samourai.wallet.sync.EnumSyncTaskStatus.FAILED
import com.samourai.wallet.sync.EnumSyncTaskStatus.IN_PROGRESS
import com.samourai.wallet.sync.EnumSyncTaskStatus.IN_PROGRESS_LONG
import com.samourai.wallet.sync.EnumSyncTaskStatus.LOCAL_IN_PROGRESS
import com.samourai.wallet.sync.EnumSyncTaskStatus.LOCAL_IN_PROGRESS_LONG
import com.samourai.wallet.sync.EnumSyncTaskStatus.SKIPPED
import com.samourai.wallet.sync.EnumSyncTaskStatus.SUCCEEDED
import com.samourai.wallet.theme.samouraiBoxCheckGreen
import com.samourai.wallet.theme.samouraiBoxGray
import com.samourai.wallet.theme.samouraiBoxGreenBlueLight
import com.samourai.wallet.theme.samouraiBoxHeaderBackgroundBlack
import com.samourai.wallet.theme.samouraiBoxHeaderBackgroundGrey
import com.samourai.wallet.theme.samouraiBoxTextLightGrey
import com.samourai.wallet.theme.samouraiBoxTextOrangeDark
import com.samourai.wallet.theme.samouraiBoxTextRed
import com.samourai.wallet.theme.samouraiBoxYellow
import com.samourai.wallet.util.func.WalletUtil
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.apache.commons.lang3.StringUtils
import java.util.Objects.nonNull

class SyncWalletActivity : SamouraiActivity() {

    companion object {
        const val TAG = "SyncWalletActivity"
    }

    private val syncWalletModel: SyncWalletModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        syncWalletModel.startWalletSync()
        setContent {
            SyncWalletActivityContent(model = syncWalletModel, activity = this)
        }
    }
}

@Composable
fun SyncWalletActivityContent(model: SyncWalletModel, activity: SyncWalletActivity?) {

    val footerHeight = computeFooterHeight(model)
    val headerHeight = 100.dp

    Box (
        modifier = Modifier
            .background(samouraiBoxHeaderBackgroundBlack)
    ) {

        Column(
            modifier = Modifier
                .fillMaxSize()
                .background(samouraiBoxHeaderBackgroundBlack)
        ) {
            SyncWalletHeaderContent(model=model, headerHeight=headerHeight)
            SyncWalletCoreContent(
                model=model,
                activity=activity,
                headerHeight=headerHeight,
                footerHeight=footerHeight
            )
            SyncWalletFooterContent(model=model, activity=activity, footerHeight=footerHeight)
        }

    }
}

@Composable
private fun computeFooterHeight(model: SyncWalletModel): Dp {
    val isSyncCompleted by model.syncCompleted.observeAsState(false)
    val isRetrySyncShouldBeDone by model.retrySyncShouldBeDone.observeAsState(false)
    val shouldClaimedPayNym by model.shouldClaimedPayNym.observeAsState(false)

    return if (isSyncCompleted &&
        !(shouldClaimedPayNym && !isRetrySyncShouldBeDone)
        && isRetrySyncShouldBeDone
    ) 170.dp
    else 110.dp
}

@Composable
fun SyncWalletHeaderContent(
    model: SyncWalletModel,
    headerHeight: Dp
) {

    val robotoBoldFont = FontFamily(Font(R.font.roboto_bold, FontWeight.Bold))
    val robotoMediumFont = FontFamily(Font(R.font.roboto_medium, FontWeight.Normal))
    val isSyncCompleted by model.syncCompleted.observeAsState(false)

    Column(
        modifier = Modifier
            .background(samouraiBoxHeaderBackgroundGrey)
            .height(headerHeight)
            .padding(20.dp),
        verticalArrangement = Arrangement.Center
    ) {


        if(isSyncCompleted) {

            Row (
                modifier =  Modifier.fillMaxSize(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "Completed",
                        color = Color.White,
                        fontSize = 18.sp,
                        fontFamily = robotoBoldFont
                    )
                }
                Spacer(modifier = Modifier.weight(1f))
                Column {
                    Icon(
                        painter = painterResource(id = R.drawable.ic_check),
                        contentDescription = null,
                        tint = samouraiBoxTextLightGrey,
                        modifier = Modifier.size(52.dp)
                    )
                }
            }
        } else {

            Row (
                modifier =  Modifier.fillMaxSize(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "Syncing wallet",
                        color = Color.White,
                        fontSize = 18.sp,
                        fontFamily = robotoBoldFont
                    )
                    Text(
                        text = "Please wait...",
                        color = samouraiBoxTextLightGrey,
                        fontSize = 12.sp,
                        fontFamily = robotoMediumFont
                    )
                }
                Spacer(modifier = Modifier.weight(1f))
                Column {
                    Box {
                        RotatingArcs()
                    }
                }
            }
        }
    }
}

@Composable
fun SyncWalletFooterContent(
    model: SyncWalletModel,
    activity: SyncWalletActivity?,
    footerHeight: Dp) {

    val isSyncCompleted by model.syncCompleted.observeAsState(false)
    val isRetrySyncShouldBeDone by model.retrySyncShouldBeDone.observeAsState(false)
    val shouldClaimedPayNym by model.shouldClaimedPayNym.observeAsState(false)
    val coroutineScope = rememberCoroutineScope()
    val robotoMediumFont = FontFamily(Font(R.font.roboto_medium, FontWeight.Normal))


    Box(modifier = Modifier.height(footerHeight)) {
        Column (
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(start = 20.dp, end = 20.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        )
        {

            if (isSyncCompleted) {

                if (shouldClaimedPayNym && !isRetrySyncShouldBeDone) {

                    Column (
                        modifier = Modifier
                            .fillMaxWidth(1f)
                            .height(44.dp)
                            .background(samouraiBoxGreenBlueLight, RoundedCornerShape(12.dp))
                            .clickable {
                                model.claimPayNymSync()
                            },
                        verticalArrangement = Arrangement.Center,
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = "Claim PayNym",
                            color = samouraiBoxHeaderBackgroundBlack,
                            fontSize = 14.sp,
                            fontFamily = robotoMediumFont
                        )
                    }

                    Column (
                        modifier = Modifier
                            .fillMaxWidth(1f)
                            .height(44.dp)
                            .background(Color.Transparent, RoundedCornerShape(12.dp))
                            .clickable {
                                continueToBalanceActivity(coroutineScope, activity)
                            },
                        verticalArrangement = Arrangement.Center,
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = "Continue without claiming PayNym",
                            color = samouraiBoxGreenBlueLight,
                            fontSize = 14.sp,
                            fontFamily = robotoMediumFont
                        )
                    }
                } else {

                    if (isRetrySyncShouldBeDone) {
                        Column (
                            modifier = Modifier
                                .fillMaxWidth(1f)
                                .height(44.dp)
                                .background(samouraiBoxYellow, RoundedCornerShape(12.dp))
                                .clickable {
                                    coroutineScope.launch(Dispatchers.Main) {
                                        model.startWalletSync()
                                    }
                                },
                            verticalArrangement = Arrangement.Center,
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Text(
                                text = "Try syncing wallet again",
                                color = samouraiBoxHeaderBackgroundBlack,
                                fontSize = 14.sp,
                                fontFamily = robotoMediumFont
                            )
                        }
                    }

                    Column (
                        modifier = Modifier
                            .fillMaxWidth(1f)
                            .height(44.dp)
                            .background(samouraiBoxGreenBlueLight, RoundedCornerShape(12.dp))
                            .clickable {
                                continueToBalanceActivity(coroutineScope, activity)
                            },
                        verticalArrangement = Arrangement.Center,
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = "Continue",
                            color = samouraiBoxHeaderBackgroundBlack,
                            fontSize = 14.sp,
                            fontFamily = robotoMediumFont
                        )
                    }

                    Column (
                        modifier = Modifier
                            .fillMaxWidth(1f)
                            .height(44.dp)
                            .background(Color.Transparent, RoundedCornerShape(12.dp))
                            .clickable {
                                WalletUtil.stop(activity)
                            },
                        verticalArrangement = Arrangement.Center,
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = "Exit wallet",
                            color = samouraiBoxGreenBlueLight,
                            fontSize = 14.sp,
                            fontFamily = robotoMediumFont
                        )
                    }
                }

            } else {

                Column (
                    modifier = Modifier
                        .fillMaxWidth(1f)
                        .height(44.dp)
                        .background(samouraiBoxGray, RoundedCornerShape(12.dp)),
                    verticalArrangement = Arrangement.Center,
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "Continue",
                        color = samouraiBoxHeaderBackgroundBlack,
                        fontSize = 14.sp,
                        fontFamily = robotoMediumFont
                    )
                }

                Column (
                    modifier = Modifier
                        .fillMaxWidth(1f)
                        .height(44.dp)
                        .background(Color.Transparent, RoundedCornerShape(12.dp)),
                    verticalArrangement = Arrangement.Center,
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "Exit wallet",
                        color = samouraiBoxGray,
                        fontSize = 14.sp,
                        fontFamily = robotoMediumFont
                    )
                }
            }
        }
    }
}

private fun continueToBalanceActivity(
    coroutineScope: CoroutineScope,
    activity: SyncWalletActivity?
) {
    coroutineScope.launch(Dispatchers.Main) {
        val intent = Intent(activity, BalanceActivity::class.java)
        val bundle: Bundle? = activity!!
            .getIntent()
            .getExtras()
        if (nonNull(bundle)) {
            intent.putExtras(bundle!!)
        }
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_NEW_TASK)
        activity.startActivity(intent)
        activity.finish()
    }
}

@Composable
fun SyncWalletCoreContent(
    model: SyncWalletModel,
    activity: SyncWalletActivity?,
    headerHeight: Dp,
    footerHeight: Dp
) {

    val screenHeight = LocalConfiguration.current.screenHeightDp.dp

    val maxSecondComponentHeight =
        screenHeight - getStatusBarHeightDp() - footerHeight - headerHeight

    val taskStatuses by model.taskStatuses.observeAsState()

    val rotation = remember { Animatable(0f) }
    LaunchedEffect(Unit) {
        launch {
            rotation.animateTo(
                targetValue = 360f,
                animationSpec = infiniteRepeatable(
                    animation = tween(durationMillis = 2000, easing = LinearEasing),
                    repeatMode = RepeatMode.Restart
                )
            )
        }
    }

    val scrollState = rememberScrollState()
    LaunchedEffect(scrollState.maxValue) {
        launch(Dispatchers.Main) {
            scrollToPositionGradually(scrollState, scrollState.maxValue)
        }
    }

    Box {
        Column(
            modifier = Modifier
                .align(Alignment.TopCenter)
                .height(maxSecondComponentHeight)
                .verticalScroll(
                    state = scrollState,
                    enabled = true
                )
                .background(samouraiBoxHeaderBackgroundBlack)
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            for (taskStatus in taskStatuses!!) {
                SyncWalletItemContent(
                    model=model,
                    activity=activity,
                    status=taskStatus,
                    rotation=rotation)
            }
        }
    }
}

@Composable
private fun SyncWalletItemContent(
    model: SyncWalletModel,
    activity: SyncWalletActivity?,
    status: Triple<EnumSyncTask, EnumSyncTaskStatus, String>,
    rotation: Animatable<Float, AnimationVector1D>
) {

    val robotoMediumFont = FontFamily(Font(R.font.roboto_medium, FontWeight.Normal))
    val robotoLightFont = FontFamily(Font(R.font.roboto_light, FontWeight.Normal))

    val payNymName by model.payNymName.observeAsState("")
    val payNymContactsSyncMsg by model.payNymContactsSyncProgressMessage.observeAsState("")
    val payNymLogo by BIP47Util.getInstance(activity).payNymLogoLive.observeAsState(null)

    Column {
        Row (
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row (
                horizontalArrangement = Arrangement.spacedBy(14.dp)
            ) {
                Text(
                    text = status.first.caption,
                    color = samouraiBoxTextLightGrey,
                    fontSize = 14.sp,
                    fontFamily = robotoMediumFont
                )
                if (status.first == EnumSyncTask.PAYNYM) {
                    Row (
                        horizontalArrangement = Arrangement.spacedBy(4.dp)
                    )  {
                        if (nonNull(payNymLogo)) {
                            Image(
                                bitmap = payNymLogo!!.asImageBitmap(),
                                contentDescription = "PayNym logo",
                                modifier = Modifier
                                    .size(24.dp)
                                    .clip(CircleShape)
                            )
                        }
                        Text(
                            text = payNymName,
                            color = samouraiBoxTextLightGrey,
                            fontSize = 14.sp,
                            fontFamily = robotoLightFont
                        )
                    }
                }
            }
            Spacer(modifier = Modifier.weight(1f))
            Column {
                when(status.second) {
                    IN_PROGRESS, IN_PROGRESS_LONG -> {
                        Icon(
                            painter = painterResource(id = R.drawable.ic_checkbox_blank_outline),
                            contentDescription = null,
                            tint = samouraiBoxTextLightGrey
                        )
                    }
                    LOCAL_IN_PROGRESS, LOCAL_IN_PROGRESS_LONG -> {
                        Icon(
                            painter = painterResource(id = R.drawable.ic_sync_in_progress),
                            contentDescription = null,
                            tint = samouraiBoxTextLightGrey,
                            modifier = Modifier
                                .size(24.dp)
                                .graphicsLayer(rotationZ = rotation.value)
                        )
                    }
                    SUCCEEDED -> {
                        Icon(
                            painter = painterResource(id = R.drawable.ic_checkbox_marked),
                            contentDescription = null,
                            tint = samouraiBoxCheckGreen
                        )
                    }
                    FAILED -> {
                        Icon(
                            painter = painterResource(id = R.drawable.ic_alert_box),
                            contentDescription = null,
                            tint = samouraiBoxTextRed
                        )
                    }
                    SKIPPED -> {
                        Icon(
                            painter = painterResource(id = R.drawable.ic_close_box),
                            contentDescription = null,
                            tint = samouraiBoxTextRed
                        )
                    }
                }
            }
            // to align with the sync icon in header zone
            Spacer(modifier = Modifier.width(15.dp))
        }

        Column (
            modifier = Modifier.height(52.dp)
        ) {

            var message = status.third
            if (status.first == EnumSyncTask.PAYNYM_CONTACT) {
               message = StringUtils.trim(message + "\n" + payNymContactsSyncMsg)
            }
            Text(
                text = message,
                color = if(status.second == FAILED || status.second == SKIPPED) samouraiBoxTextRed else samouraiBoxTextOrangeDark,
                fontSize = 14.sp,
                fontFamily = robotoLightFont,
                maxLines = 3
            )
        }
    }
}

@Composable
fun RotatingArcs() {

    val infiniteTransition = rememberInfiniteTransition(label = "")

    val rotation by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 2000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = ""
    )

    Box(
        contentAlignment = Alignment.Center,
        modifier = Modifier.size(60.dp)
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            drawArcs(rotation)
        }
        Icon(
            painter = painterResource(id = R.drawable.ic_sync),
            contentDescription = null,
            tint = samouraiBoxTextLightGrey,
            modifier = Modifier.size(52.dp)
        )
    }
}

fun DrawScope.drawArcs(rotation: Float) {
    val strokeWidth = 2.dp.toPx()
    val arcSize = Size(size.width - strokeWidth, size.height - strokeWidth)
    val topLeftOffset = Offset(strokeWidth / 2, strokeWidth / 2)

    // Draw first arc
    drawArc(
        color = Color.White,
        startAngle = rotation + 90,
        sweepAngle = 80f,
        useCenter = false,
        topLeft = topLeftOffset,
        size = arcSize,
        style = Stroke(width = strokeWidth)
    )

    // Draw second arc
    drawArc(
        color = Color.White,
        startAngle = rotation - 90,
        sweepAngle = 80f,
        useCenter = false,
        topLeft = topLeftOffset,
        size = arcSize,
        style = Stroke(width = strokeWidth)
    )
}

@Composable
fun getStatusBarHeightDp(): Dp {
    val context = LocalContext.current
    val statusBarHeightResId = context.resources.getIdentifier("status_bar_height", "dimen", "android")
    val statusBarHeightPx = if (statusBarHeightResId > 0) {
        context.resources.getDimensionPixelSize(statusBarHeightResId)
    } else {
        0
    }
    return with(LocalDensity.current) { statusBarHeightPx.toDp() }
}

suspend fun scrollToPositionGradually(scrollState: ScrollState, targetPosition: Int) {
    val currentPosition = scrollState.value
    val step = 5

    if (currentPosition < targetPosition) {
        for (i in currentPosition..targetPosition step step) {
            scrollState.scrollTo(i)
            withContext(Dispatchers.Main) {
                kotlinx.coroutines.delay(10)
            }
        }
        scrollState.scrollTo(targetPosition)
    }
}

@Preview(showBackground = true)
@Composable
fun RotatingArcsPreview() {
    RotatingArcs()
}


@Preview(showBackground = true, heightDp = 780, widthDp = 420)
@Composable
fun DefaultPreview(
    @PreviewParameter(SyncModelPreviewProvider::class) syncWalletModel: SyncWalletModel
) {
    SyncWalletActivityContent(
        model = syncWalletModel,
        activity = null
    )
}

class SyncModelPreviewProvider : PreviewParameterProvider<SyncWalletModel> {
    override val values: Sequence<SyncWalletModel>
        get() = sequenceOf(SyncWalletModel(TestApplication(), true))
}