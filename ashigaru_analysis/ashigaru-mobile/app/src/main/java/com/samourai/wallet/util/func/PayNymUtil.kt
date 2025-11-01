package com.samourai.wallet.util.func

import android.content.Context
import android.util.Log
import com.google.gson.Gson
import com.samourai.wallet.api.APIFactory
import com.samourai.wallet.bip47.BIP47Meta
import com.samourai.wallet.bip47.BIP47Util
import com.samourai.wallet.bip47.paynym.WebUtil
import com.samourai.wallet.bip47.rpc.PaymentCode
import com.samourai.wallet.payload.PayloadUtil
import com.samourai.wallet.paynym.api.PayNymApiService
import com.samourai.wallet.paynym.models.NymResponse
import com.samourai.wallet.util.PrefsUtil
import kotlinx.coroutines.CancellationException
import org.apache.commons.lang3.StringUtils
import org.apache.commons.lang3.StringUtils.defaultIfBlank
import org.json.JSONException
import org.json.JSONObject


const val TAG = "PayNymUtil"

fun synPayNym(pcode : String?, context : Context) {
    synPayNym(pcode, true, context)
}

fun synPayNym(pcode : String?, saveWallet : Boolean, context : Context) {
    val payment_code = PaymentCode(pcode)
    var idx = 0
    var loop = true
    val addrs = ArrayList<String>()
    while (loop) {
        addrs.clear()
        for (i in idx until (idx + 20)) {
            //                            Log.i("PayNymDetailsActivity", "sync receive from " + i + ":" + BIP47Util.getInstance(PayNymDetailsActivity.this).getReceivePubKey(payment_code, i));
            val addr = BIP47Util.getInstance(context).getReceivePubKey(payment_code, i)
            BIP47Meta.getInstance().idx4AddrLookup[addr] = i
            BIP47Meta.getInstance().pCode4AddrLookup[addr] = payment_code.toString()
            addrs.add(addr)
            //                            Log.i("PayNymDetailsActivity", "p2pkh " + i + ":" + BIP47Util.getInstance(PayNymDetailsActivity.this).getReceiveAddress(payment_code, i).getReceiveECKey().toAddress(SamouraiWallet.getInstance().getCurrentNetworkParams()).toString());
        }
        val s = addrs.toTypedArray()
        val nb = APIFactory.getInstance(context).syncBIP47Incoming(s)
        //                        Log.i("PayNymDetailsActivity", "sync receive idx:" + idx + ", nb == " + nb);
        if (nb == 0) {
            loop = false
        }
        idx += 20
    }
    idx = 0
    loop = true
    BIP47Meta.getInstance().setOutgoingIdx(pcode, 0)
    while (loop) {
        addrs.clear()
        for (i in idx until (idx + 20)) {
            val sendPubKey = BIP47Util.getInstance(context).getSendPubKey(payment_code, i)
            BIP47Meta.getInstance().idx4AddrLookup[sendPubKey] = i
            BIP47Meta.getInstance().pCode4AddrLookup[sendPubKey] = payment_code.toString()
            addrs.add(sendPubKey)
        }
        val s = addrs.toTypedArray()
        val nb = APIFactory.getInstance(context).syncBIP47Outgoing(s)
        //                        Log.i("PayNymDetailsActivity", "sync send idx:" + idx + ", nb == " + nb);
        if (nb == 0) {
            loop = false
        }
        idx += 20
    }

    BIP47Meta.getInstance().pruneIncoming()

    if (saveWallet) {
        WalletUtil.saveWallet(context)
    }
}

suspend fun executeFeaturePayNymUpdate(context : Context) {
    var obj = JSONObject()
    obj.put("code", BIP47Util.getInstance(context).paymentCode.toString())
    var res = WebUtil.getInstance(context).postURL("application/json", null, PayNymApiService.PAYNYM_API + "api/v1/token", obj.toString())
    var responseObj = JSONObject(res)
    if (responseObj.has("token")) {
        val token = responseObj.getString("token")
        val sig = MessageSignUtil.getInstance(context).signMessage(BIP47Util.getInstance(context).notificationAddress.ecKey, token)
        obj = JSONObject()
        obj.put("nym", BIP47Util.getInstance(context).paymentCode.toString())
        obj.put("code", BIP47Util.getInstance(context).featurePaymentCode.toString())
        obj.put("signature", sig)

        res = WebUtil.getInstance(context).postURL("application/json", token, PayNymApiService.PAYNYM_API + "api/v1/nym/add", obj.toString())
        responseObj = JSONObject(res)
        if (responseObj.has("segwit") && responseObj.has("token")) {
            PrefsUtil.getInstance(context).setValue(PrefsUtil.PAYNYM_FEATURED_SEGWIT, true)
        } else if (responseObj.has("claimed") && responseObj.getBoolean("claimed") == true) {
            PrefsUtil.getInstance(context).setValue(PrefsUtil.PAYNYM_FEATURED_SEGWIT, true)
        }
    }
}

suspend fun isClaimedAndFeaturedPayNym(context : Context) : Triple<Boolean, Boolean, String> {
    val pcode = BIP47Util.getInstance(context).paymentCode.toString()
    val nymInfo = getNymInfoOffline(pcode, context)
    var strNymName : String = ""
    if (nymInfo.has("nymName")) {
        strNymName = nymInfo.getString("nymName")
        BIP47Meta.getInstance().setName(pcode, strNymName)
        if (FormatsUtil.getInstance().isValidPaymentCode(BIP47Meta.getInstance().getLabel(pcode))) {
            BIP47Meta.getInstance().setLabel(pcode, strNymName)
        }
    }
    var featured : Boolean = false
    if (nymInfo.has("segwit") && nymInfo.getBoolean("segwit")) {
        featured = true
    }

    var claimed = isClaimedPayNym(pcode, nymInfo)

    return Triple(claimed, featured, strNymName)
}

suspend fun isClaimedPayNym(pcode : String, nymInfo: JSONObject): Boolean {

    var claimed : Boolean = false
    if (nymInfo.has("codes")) {
        val codeArray = nymInfo.getJSONArray("codes")

        for (i in 0 until codeArray.length()) {
            val codeInfo: JSONObject = codeArray.getJSONObject(i)
            if (codeInfo.has("code") && StringUtils.equals(codeInfo.getString("code"), pcode)) {
                claimed = codeInfo.has("claimed") && codeInfo.getBoolean("claimed");
                break;
            }
        }
    }

    return claimed
}

suspend fun getNymInfoOffline(pcode: String, context: Context): JSONObject {
    val obj = JSONObject()
    obj.put("nym", pcode)
    val res = WebUtil.getInstance(context)
        .postURL("application/json", null, PayNymApiService.PAYNYM_API + "api/v1/nym", obj.toString())
    return JSONObject(res)
}

suspend fun getNymInfo(pcode: String, context: Context): JSONObject {

    var nymInfo : JSONObject = JSONObject()
    val apiPayNymApiService = PayNymApiService(pcode, context)

    try {
        val nymResponse = apiPayNymApiService.getNymInfo()
        if (nymResponse.isSuccessful) {
            nymInfo = JSONObject(nymResponse.body?.string())
        }
    } catch (ex: Exception) {
        throw CancellationException(ex.message)
    }
    return nymInfo;
}

suspend fun claim(context : Context) : Pair<Boolean, String> {

    val strPaymentCode = BIP47Util.getInstance(context).paymentCode.toString()
    val apiPayNymApiService = PayNymApiService(strPaymentCode, context)

    try {
        val response = apiPayNymApiService.claim()
        if (response.isSuccessful) {
            val nymResponse = apiPayNymApiService.getNymInfo()
            if (nymResponse.isSuccessful) {
                try {
                    val data = JSONObject(nymResponse.body?.string())
                    PayloadUtil.getInstance(context).serializePayNyms(data)
                    val nym = if (data.has("nymName")) data.getString("nymName") else ""
                    return Pair(true, nym)
                } catch (ex: Exception) {
                    throw CancellationException(ex.message)
                }
            }
        }
    } catch (ex: Exception) {
        throw CancellationException(ex.message)
    }
    return Pair(false, "")
}

suspend fun reinitBIP47Meta(context: Context) : Boolean {
    try {

        val pcodeLabelsToRestore = BIP47Meta.getInstance().copyOfPcodeLabels

        val pcode = BIP47Util.getInstance(context).paymentCode.toString()
        var jsonObject = getNymInfo(pcode, context)
        if (jsonObject.has("empty") || !jsonObject.has("codes")) {
            return true
        }
        val nym = Gson().fromJson(jsonObject.toString(), NymResponse::class.java);
        BIP47Meta.getInstance().partialClearOnRestoringWallet()

        nym.following?.let { codes ->
            codes.forEach { paynym ->
                BIP47Meta.getInstance().setSegwit(paynym.code, paynym.segwit)
                BIP47Meta.getInstance().setName(paynym.code, paynym.nymName)
                val pname = defaultIfBlank(pcodeLabelsToRestore.get(paynym.code), paynym.nymName)
                BIP47Meta.getInstance().setLabel(paynym.code, pname)
            }
            val followings = ArrayList(codes.distinctBy { it.code }.map { it.code })
            BIP47Meta.getInstance().setFollowings(followings)
        }
        nym.followers?.let { codes ->
            codes.forEach { paynym ->
                BIP47Meta.getInstance().setSegwit(paynym.code, paynym.segwit)
                BIP47Meta.getInstance().setName(paynym.code, paynym.nymName)
                val pname = defaultIfBlank(pcodeLabelsToRestore.get(paynym.code), paynym.nymName)
                BIP47Meta.getInstance().setLabel(paynym.code, pname)
            }
        }

        PayloadUtil.getInstance(context).serializePayNyms(jsonObject);
    } catch (e: JSONException) {
        Log.e(TAG, "issue on registerPayNymContact", e)
        return false
    }
    return true
}
