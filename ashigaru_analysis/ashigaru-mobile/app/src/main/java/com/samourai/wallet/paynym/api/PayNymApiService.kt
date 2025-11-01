package com.samourai.wallet.paynym.api

import android.content.Context
import android.util.Log
import com.samourai.wallet.api.AbstractApiService
import com.samourai.wallet.bip47.BIP47Util
import com.samourai.wallet.sync.SyncWalletModel
import com.samourai.wallet.util.func.MessageSignUtil
import com.samourai.wallet.util.func.synPayNym
import com.samourai.wallet.util.network.WebUtil
import okhttp3.HttpUrl
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.Response
import org.json.JSONObject
import java.io.IOException


/**
 * samourai-wallet-android
 *
 */
class PayNymApiService(private val paynymCode: String, private val context: Context) : AbstractApiService() {

    private val TAG = PayNymApiService::class.java.simpleName


    private var payNymToken: String? = null

    override fun buildClient(url: HttpUrl): OkHttpClient {
        val builder = WebUtil.getInstance(context).getTorHttpClientBuilder(url.toString());

        builder.addInterceptor { chain ->
            val original = chain.request()

            val newBuilder = original.newBuilder()
            if (!payNymToken.isNullOrEmpty()) {
                newBuilder
                    .header("auth-token", payNymToken!!)
                    .header("client", "samourai-wallet")
            }
            newBuilder.method(original.method, original.body)
            chain.proceed(newBuilder.build())
        }
        return builder.build()
    }

    private suspend fun getToken() {
        val builder = Request.Builder();
        builder.url("$PAYNYM_API/api/v1/token")
        val payload = JSONObject().apply {
            put("code", paynymCode)
        }
        val body: RequestBody = RequestBody.create(JSON, payload.toString())
        val response = this.executeRequest(builder.post(body).build())
        if (response.isSuccessful) {
            val status = response.body?.string()
            val tokenResponse = JSONObject(status)
            if (tokenResponse.has("token")) {
                this.payNymToken = tokenResponse.getString("token")
            } else {
                throw Exception("Invalid paynym token response")
            }
        } else {
            throw Exception("Unable to retrieve paynym token")
        }
    }


    suspend fun claim(): Response {
        createPayNym()
        if (payNymToken == null) {
            getToken()
        }
        val payload = JSONObject().apply {
            put("signature", getSig())
        }
        val builder = Request.Builder();
        val body: RequestBody = RequestBody.create(JSON, payload.toString())
        builder.url("$PAYNYM_API/api/v1/claim")
        val response = this.executeRequest(builder.post(body).build())
        if (response.isSuccessful) {
            val jsonStr = response.body?.string();
            val json = JSONObject(jsonStr);
            if (json.has("token")) {
                payNymToken = json.getString("token")
            }
            return addPayNym()
        } else {
            throw IOException("Unable to claim paynym")
        }
    }


    suspend fun addPayNym(): Response {
        if (payNymToken == null) {
            getToken()
        }
        val paynymCode = BIP47Util.getInstance(context).paymentCode.toString()
        val paynymCodeFeat = BIP47Util.getInstance(context).featurePaymentCode
        val payload = JSONObject().apply {
            put("nym", paynymCode)
            put("code", paynymCodeFeat)
            put("signature", getSig())
        }
        val builder = Request.Builder();
        val body: RequestBody = RequestBody.create(JSON, payload.toString())
        builder.url("$PAYNYM_API/api/v1/nym/add")
        return this.executeRequest(builder.post(body).build())
    }


    suspend fun createPayNym(): JSONObject {
        val payload = JSONObject().apply {
            put("code", paynymCode)
        }
        val builder = Request.Builder();
        val body: RequestBody = RequestBody.create(JSON, payload.toString())
        builder.url("$PAYNYM_API/api/v1/create")
        val response = this.executeRequest(builder.post(body).build())
        if (response.isSuccessful) {
            val jsonStr = response.body?.string()
            val jsonObject = JSONObject(jsonStr)
            if (jsonObject.has("token")) {
                this.payNymToken = jsonObject.getString("token")
            }
            return jsonObject
        } else {
            val jsonStr = response.body?.string()
            val jsonObject = JSONObject(jsonStr)
            if (jsonObject.has("message")) {
                throw IOException(jsonObject.getString("message"))
            } else {
                throw IOException("Unable to register paynym")
            }
        }
    }

    suspend fun getNymInfo(): Response {
        if (payNymToken == null) {
            getToken()
        }
        val payload = JSONObject().apply {
            put("nym", paynymCode)
        }
        val builder = Request.Builder();
        val body: RequestBody = RequestBody
            .create(JSON, payload.toString())
        builder.url("$PAYNYM_API/api/v1/nym")
        return executeRequest(builder.post(body).build())
    }


    suspend fun auth47(url: String, payload: JSONObject): Response {
        val builder = Request.Builder();
        val body: RequestBody = payload.toString().toRequestBody(JSON)
        builder.url(url)
        return executeRequest(builder.post(body).build())
    }

    public suspend fun follow(pcode: String): Response {

        if (payNymToken == null) {
            getToken()
        }
        val builder = Request.Builder();
        val obj = JSONObject()

        obj.put("target", pcode)
        obj.put("signature", getSig())

        val body: RequestBody = RequestBody
            .create(JSON, obj.toString())

        builder.url("$PAYNYM_API/api/v1/follow")
        return executeRequest(builder.post(body).build())
    }

    suspend fun unfollow(pcode: String): Response {

        if (payNymToken == null) {
            getToken()
        }
        val builder = Request.Builder();
        val obj = JSONObject()

        obj.put("target", pcode)
        obj.put("signature", getSig())

        val body: RequestBody = RequestBody
            .create(JSON, obj.toString())

        builder.url("$PAYNYM_API/api/v1/unfollow")
        return executeRequest(builder.post(body).build())
    }

    fun syncPcode(pcode: String): Boolean {
        try {
            synPayNym(pcode, context)
            return true
        } catch (ex: Exception) {
            Log.e(TAG, "Exception on synPayNym")
        }
        return false
    }

    suspend fun retrievePayNymConnections(): Boolean {
        try {
            return SyncWalletModel.retrievePayNymConnections(context)
        } catch (ex: Exception) {
            Log.e(TAG, "Exception on synPayNym")
        }
        return false
    }

    private fun getSig(): String? {
        return MessageSignUtil.getInstance(context).signMessage(BIP47Util.getInstance(context).notificationAddress.ecKey, payNymToken)
    }

    //This will be replaced using DI injection in the future
    companion object {
        lateinit var PAYNYM_API: String
        var payNymApiService: PayNymApiService? = null
        fun getInstance(code: String, context: Context): PayNymApiService {
            if (payNymApiService == null) {
                payNymApiService = PayNymApiService(code, context)
            } else {
                if (code != payNymApiService!!.paynymCode) {
                    payNymApiService = PayNymApiService(code, context)
                }
            }
            return payNymApiService!!
        }
    }


}