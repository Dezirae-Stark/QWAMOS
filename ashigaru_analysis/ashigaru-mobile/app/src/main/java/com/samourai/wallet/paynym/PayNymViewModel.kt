package com.samourai.wallet.paynym

import android.app.Application
import android.util.Log
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.google.gson.Gson
import com.samourai.wallet.access.AccessFactory
import com.samourai.wallet.bip47.BIP47Meta
import com.samourai.wallet.bip47.BIP47Util
import com.samourai.wallet.payload.PayloadUtil
import com.samourai.wallet.paynym.api.PayNymApiService
import com.samourai.wallet.paynym.models.NymResponse
import com.samourai.wallet.util.CharSequenceX
import com.samourai.wallet.util.PrefsUtil
import com.samourai.wallet.util.func.isClaimedPayNym
import com.samourai.wallet.util.tech.LogUtil
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import kotlinx.coroutines.withContext
import org.bitcoinj.core.AddressFormatException
import org.json.JSONException
import org.json.JSONObject
import java.util.concurrent.atomic.AtomicInteger

class PayNymViewModel(application: Application) : AndroidViewModel(application) {

    private var paymentCode = MutableLiveData<String>()
    private var errors = MutableLiveData<String>()
    private var loader = MutableLiveData(false)
    private var refreshTaskProgress = MutableLiveData(Pair(0, 0))
    private var followersList = MutableLiveData<ArrayList<String>>()
    private var followingList = MutableLiveData<ArrayList<String>>()
    private var refreshJob: Job = Job()
    private val TAG = "PayNymHomeViewModel"

    val followers: LiveData<ArrayList<String>>
        get() = followersList

    val errorsLiveData: LiveData<String>
        get() = errors

    val pcode: LiveData<String>
        get() = paymentCode

    val following: LiveData<ArrayList<String>>
        get() = followingList

    val loaderLiveData: LiveData<Boolean>
        get() = loader


    val refreshTaskProgressLiveData: LiveData<Pair<Int, Int>>
        get() = refreshTaskProgress


    private suspend fun setPaynymPayload(jsonObject: JSONObject) = withContext(Dispatchers.IO) {
        if (jsonObject.has("empty") || !jsonObject.has("codes")) {
            val backupFilePaynyms = PayloadUtil.getInstance(getApplication<Application>().applicationContext).paynymsFromBackupFile
            BIP47Meta.getInstance().setFollowings(backupFilePaynyms as java.util.ArrayList<String>?)
            sortByLabel(backupFilePaynyms);
            viewModelScope.launch(Dispatchers.Main) {
                followingList.postValue(backupFilePaynyms)
            }
            return@withContext
        }
        try {
            val pcode = BIP47Util.getInstance(getApplication()).paymentCode.toString()
            if (isClaimedPayNym(pcode, jsonObject)) {
                val strNymName = jsonObject.getString("nymName")
                viewModelScope.launch(Dispatchers.Main) {
                    paymentCode.postValue(strNymName)
                }
            }

            val backupFilePaynyms = PayloadUtil.getInstance(getApplication<Application>().applicationContext).paynymsFromBackupFile

            val nym = Gson().fromJson(jsonObject.toString(), NymResponse::class.java)
            nym.following?.let { codes ->
                codes.forEach { paynym ->
                    BIP47Meta.getInstance().setSegwit(paynym.code, paynym.segwit)
                    BIP47Meta.getInstance().setName(paynym.code, paynym.nymName)
                    if (BIP47Meta.getInstance().getDisplayLabel(paynym.code).contains(paynym.code.substring(0, 4))) {
                        BIP47Meta.getInstance().setLabel(paynym.code, paynym.nymName)
                    }
                }
                val followings = ArrayList(codes.distinctBy { it.code }.map { it.code })
                backupFilePaynyms.forEach { pcode ->
                    if (!followings.contains(pcode) && pcode != "")
                        followings.add(pcode)
                }
                BIP47Meta.getInstance().setFollowings(followings)
                sortByLabel(followings);
                viewModelScope.launch(Dispatchers.Main) {
                    followingList.postValue(followings)
                }
            }
            nym.followers?.let { codes ->
                codes.forEach { paynym ->
                    BIP47Meta.getInstance().setSegwit(paynym.code, paynym.segwit)
                    BIP47Meta.getInstance().setName(paynym.code, paynym.nymName)
                    if (BIP47Meta.getInstance().getDisplayLabel(paynym.code).contains(paynym.code.substring(0, 4))) {
                        BIP47Meta.getInstance().setLabel(paynym.code, paynym.nymName)
                    }
                }
                val followers = ArrayList(codes.distinctBy { it.code }.map { it.code })
                sortByLabel(followers);
                viewModelScope.launch(Dispatchers.Main) {
                    followersList.postValue(followers)
                }
            }
            PayloadUtil.getInstance(getApplication()).serializePayNyms(jsonObject);
        } catch (e: JSONException) {
            e.printStackTrace()
        }
    }

    private fun sortByLabel(list: ArrayList<String>) {
        list.sortWith { pcode1: String?, pcode2: String? ->
            var res = java.lang.String.CASE_INSENSITIVE_ORDER.compare(BIP47Meta.getInstance().getDisplayLabel(pcode1), BIP47Meta.getInstance().getDisplayLabel(pcode2))
            if (res == 0) {
                res = BIP47Meta.getInstance().getDisplayLabel(pcode1).compareTo(BIP47Meta.getInstance().getDisplayLabel(pcode2))
            }
            res
        }
    }

    suspend fun getPayNymData() {

        val strPaymentCode = BIP47Util.getInstance(getApplication()).paymentCode.toString()
        val apiService = PayNymApiService.getInstance(strPaymentCode, getApplication())
        try {
            val response = apiService.getNymInfo()
            withContext(Dispatchers.Main) {
                loader.postValue(false)
            }
            if (response.isSuccessful) {
                val responseJson = response.body?.string()
                if (responseJson != null)
                    setPaynymPayload(JSONObject(responseJson))
                else
                    throw Exception("Invalid response ")
            }
        } catch (ex: Exception) {
            initPayNyms()
        }
    }

    private suspend fun initPayNyms() {
        try {
            val res =
                PayloadUtil.getInstance(getApplication()).deserializePayNyms().toString()
            setPaynymPayload(JSONObject(res))
        } catch (ex: Exception) {
            setPaynymPayload(JSONObject().put("empty", true))
            LogUtil.error(TAG, ex)
        }
    }

    fun refreshPayNym() {
        if (refreshJob.isActive) {
            refreshJob.cancel("")
        }

        synchronized(PayNymViewModel::class.java) {
            refreshJob = viewModelScope.launch(Dispatchers.Main) {
                loader.postValue(true)
                withContext(Dispatchers.IO) {
                    try {
                        getPayNymData()
                    } catch (error: Exception) {
                        error.printStackTrace()
                        throw CancellationException(error.message)
                    }
                }
            }
        }

        refreshJob.invokeOnCompletion {
            viewModelScope.launch(Dispatchers.Main) {
                loader.postValue(false)
            }
        }
    }

    fun doSyncAll(silentSync: Boolean = false) {

        val strPaymentCode = BIP47Util.getInstance(getApplication()).paymentCode.toString()
        val apiService = PayNymApiService.getInstance(strPaymentCode, getApplication())

        val _pcodes = BIP47Meta.getInstance().getSortedByLabels(false)
        if (_pcodes.size == 0) {
            return
        }

        try {
            if (_pcodes.contains(BIP47Util.getInstance(getApplication()).paymentCode.toString())) {
                _pcodes.remove(BIP47Util.getInstance(getApplication()).paymentCode.toString())
                BIP47Meta.getInstance().remove(BIP47Util.getInstance(getApplication()).paymentCode.toString())
            }
        } catch (afe: AddressFormatException) {
            afe.printStackTrace()
        }

        refreshJob = viewModelScope.launch(Dispatchers.Main) {

            var progress = AtomicInteger(0)

            if (!silentSync)
                refreshTaskProgress.postValue(Pair(progress.get(), _pcodes.size))

            viewModelScope.launch(Dispatchers.IO) {
                BIP47Util.getInstance(getApplication()).fetchBotImage().subscribe()
            }

            withContext(Dispatchers.IO) {
                val semaphore = Semaphore(6)
                val tasks = _pcodes.map { pcode ->
                    async(Dispatchers.IO) {
                        semaphore.withPermit {
                            try {
                                apiService.syncPcode(pcode)
                                val progress = progress.incrementAndGet()
                                if (!silentSync) {
                                    if(progress < _pcodes.size) {
                                        refreshTaskProgress.postValue(Pair(progress, _pcodes.size))
                                    }
                                }
                                true
                            } catch (te : Throwable) {
                                Log.e(TAG, "issue on syncPcode " + pcode, te)
                            }
                        }
                    }
                }
                tasks.awaitAll()
                async(Dispatchers.IO) {
                    try {
                        apiService.retrievePayNymConnections()
                        val progress = progress.incrementAndGet()
                        if (!silentSync) {
                            refreshTaskProgress.postValue(Pair(progress, _pcodes.size))
                        }
                    } catch (te : Throwable) {
                        Log.e(TAG, "issue on retrievePayNymConnections", te)
                    }
                    true
                }.await()
            }
        }
    }

    fun init() {
        paymentCode.postValue("")
    }

    suspend fun doFollow(pcode: String) {
        val job = viewModelScope.launch {
            withContext(Dispatchers.Main) {
                loader.postValue(true)
            }
            withContext(Dispatchers.IO) {
                try {
                    val strPaymentCode = BIP47Util.getInstance(getApplication()).paymentCode.toString()
                    val apiService = PayNymApiService.getInstance(strPaymentCode, getApplication())
                    apiService.follow(pcode)
                    BIP47Meta.getInstance().isRequiredRefresh = true
                    PayloadUtil.getInstance(getApplication()).saveWalletToJSON(CharSequenceX(AccessFactory.getInstance(getApplication()).guid + AccessFactory.getInstance(getApplication()).pin))
                    //Refresh
                    getPayNymData()
                } catch (ex: Exception) {
                    throw CancellationException(ex.message)
                }
            }
        }
        job.invokeOnCompletion {
            viewModelScope.launch(Dispatchers.Main) {
                loader.postValue(false)
            }
            if (it != null) {
                errors.postValue(it.message)
            }
        }
        job.join()
    }

    fun doUnFollow(pcode: String): Job {
        val job = viewModelScope.launch {
            withContext(Dispatchers.Main) {
                loader.postValue(true)
            }
            withContext(Dispatchers.IO) {
                try {
                    val strPaymentCode = BIP47Util.getInstance(getApplication()).paymentCode.toString()
                    val apiService = PayNymApiService.getInstance(strPaymentCode, getApplication())
                    apiService.unfollow(pcode)
                    BIP47Meta.getInstance().remove(pcode)
                    PayloadUtil.getInstance(getApplication()).saveWalletToJSON(CharSequenceX(AccessFactory.getInstance(getApplication()).guid + AccessFactory.getInstance(getApplication()).pin))
                    BIP47Meta.getInstance().isRequiredRefresh = true
                    //Refresh
                    getPayNymData()
                } catch (ex: Exception) {
                    throw CancellationException(ex.message)
                }
            }
        }
        job.invokeOnCompletion {
            viewModelScope.launch(Dispatchers.Main) {
                loader.postValue(false)
            }
            if (it != null) {
                errors.postValue(it.message)
            }
        }
        return job
    }

    init {
        if (PrefsUtil.getInstance(getApplication()).getValue(PrefsUtil.PAYNYM_CLAIMED, false)) {
            init()
        }
        else {
            viewModelScope.launch {
                setPaynymPayload(JSONObject().put("empty", true))
            }
        }
    }
}