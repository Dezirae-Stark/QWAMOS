package com.samourai.wallet.util.network


import android.content.Context
import android.util.Log
import com.samourai.wallet.api.ping.PingDojoClient
import com.samourai.wallet.tor.SamouraiTorManager
import kotlinx.coroutines.delay

const val TAG = "DojoNetworkUtils"


suspend fun executeNetworkTaskWithAttempts(
    maxAttempts: Int,
    attemptDelayDuration: Long,
    aTask: suspend () -> Unit
) {

    var attempts = 0

    while (attempts < maxAttempts) {
        try {
            aTask()
            break
        } catch (e: Throwable) {
            attempts++
            if (attempts < maxAttempts) {
                Log.d(TAG, "will attempt to relaunch backgroundIOTask $attempts/$maxAttempts")
                if (attemptDelayDuration > 0L) {
                    delay(attemptDelayDuration)
                }
            } else {
                throw e
            }
        }
    }
}

suspend fun checkDojoConnection(context: Context) {

    val pingDojo = {
        PingDojoClient.createPingDojoClient(context).ping()
    }

    try {
        executeNetworkTaskWithAttempts(2, 5_000L) {
            pingDojo()
        }

    } catch (e: Exception) {

        if (!SamouraiTorManager.isConnected()) {
            SamouraiTorManager.restartSync()
        } else {
            SamouraiTorManager.newIdentitySync()
        }

        delay(8_000L)

        if (SamouraiTorManager.isConnected()) {
            executeNetworkTaskWithAttempts(2, 5_000L) {
                pingDojo()
            }
        } else {
            throw e
        }
    }
}