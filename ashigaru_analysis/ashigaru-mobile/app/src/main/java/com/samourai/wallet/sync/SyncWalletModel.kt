package com.samourai.wallet.sync

import android.app.Application
import android.content.Context
import android.util.Log
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.google.common.base.Joiner
import com.google.common.collect.ListMultimap
import com.google.common.collect.Lists
import com.google.common.collect.Maps
import com.google.common.collect.MultimapBuilder
import com.google.common.collect.Sets
import com.google.gson.Gson
import com.samourai.wallet.SamouraiWallet
import com.samourai.wallet.api.APIFactory
import com.samourai.wallet.api.backend.beans.TxDetail
import com.samourai.wallet.api.txs.PaginatedRawTxs
import com.samourai.wallet.api.txs.TxsClient
import com.samourai.wallet.api.wallet.WalletClient
import com.samourai.wallet.api.xpub.XPubClient
import com.samourai.wallet.bip47.BIP47Meta
import com.samourai.wallet.bip47.BIP47Util
import com.samourai.wallet.bip47.SendNotifTxFactory
import com.samourai.wallet.bip47.rpc.PaymentCode
import com.samourai.wallet.constants.SamouraiAccountIndex
import com.samourai.wallet.hd.HD_WalletFactory
import com.samourai.wallet.paynym.api.PayNymApiService
import com.samourai.wallet.paynym.models.NymResponse
import com.samourai.wallet.ricochet.RicochetMeta
import com.samourai.wallet.segwit.BIP49Util
import com.samourai.wallet.segwit.BIP84Util
import com.samourai.wallet.util.PrefsUtil
import com.samourai.wallet.util.func.EnumAddressType
import com.samourai.wallet.util.func.WalletUtil
import com.samourai.wallet.util.func.claim
import com.samourai.wallet.util.func.executeFeaturePayNymUpdate
import com.samourai.wallet.util.func.getNymInfo
import com.samourai.wallet.util.func.isClaimedAndFeaturedPayNym
import com.samourai.wallet.util.func.reinitBIP47Meta
import com.samourai.wallet.util.func.synPayNym
import com.samourai.wallet.util.network.AshigaruNetworkException
import com.samourai.wallet.util.network.BackendApiAndroid
import com.samourai.wallet.util.network.ConnectivityStatus
import com.samourai.wallet.util.network.checkDojoConnection
import com.samourai.wallet.util.network.executeNetworkTaskWithAttempts
import com.samourai.wallet.util.tech.AshigaruException
import com.samourai.wallet.util.tech.HapticHelper.Companion.hapticDaDuration
import com.samourai.wallet.util.tech.HapticHelper.Companion.hapticTadaPattern
import com.samourai.wallet.util.tech.HapticHelper.Companion.vibratePhone
import com.samourai.wallet.util.tech.SimpleCallback
import com.samourai.wallet.util.tech.SimpleTaskRunner
import com.samourai.wallet.util.tech.ThreadHelper
import com.samourai.wallet.whirlpool.WhirlpoolMeta
import io.reactivex.disposables.CompositeDisposable
import kotlinx.coroutines.Deferred
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import kotlinx.coroutines.withContext
import org.apache.commons.collections4.CollectionUtils
import org.apache.commons.lang3.ArrayUtils
import org.apache.commons.lang3.StringUtils
import org.apache.commons.lang3.StringUtils.equalsIgnoreCase
import java.util.Objects.isNull
import java.util.Objects.nonNull
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger

class SyncWalletModel(application: Application) : AndroidViewModel(application) {

    private var taskStatuses_ =
        MutableLiveData<List<Triple<EnumSyncTask, EnumSyncTaskStatus, String>>>(Lists.newArrayList())
    val taskStatuses: LiveData<List<Triple<EnumSyncTask, EnumSyncTaskStatus, String>>>
        get() = taskStatuses_

    private val syncCompleted_ = MutableLiveData(false)
    val syncCompleted: LiveData<Boolean>
        get() = syncCompleted_

    private val retrySyncShouldBeDone_ = MutableLiveData(false)
    val retrySyncShouldBeDone: LiveData<Boolean>
        get() = retrySyncShouldBeDone_

    private var allTasksSuccess_ = false

    private var saveWalletProfitable_ = false

    private val payNymName_ = MutableLiveData("")
    val payNymName: LiveData<String>
        get() = payNymName_

    private val shouldClaimedPayNym_ = MutableLiveData(true)
    val shouldClaimedPayNym: LiveData<Boolean>
        get() = shouldClaimedPayNym_

    private val payNymContactsSyncProgressMessage_ = MutableLiveData("")
    val payNymContactsSyncProgressMessage: LiveData<String>
        get() = payNymContactsSyncProgressMessage_

    private val compositeDisposable_ = CompositeDisposable()

    constructor(application: Application, test: Boolean) : this(application) {
        if (test) {
            taskStatuses_ = MutableLiveData(simulateWalletSyncCore())
        }
    }

    private fun setTaskStatuses(taskStatusList: List<Triple<EnumSyncTask, EnumSyncTaskStatus, String>>) {
        this.taskStatuses_.postValue(taskStatusList)
    }

    private fun currentStateOfTaskStatuses(): MutableList<Triple<EnumSyncTask, EnumSyncTaskStatus, String>> {
        return Lists.newArrayList(CollectionUtils.emptyIfNull(taskStatuses_.value))
    }

    fun startWalletSync() {
        taskStatuses_.value = Lists.newArrayList()

        val backupPcodeLabels = BIP47Meta.getInstance().copyOfPcodeLabels

        SimpleTaskRunner.create().executeAsync<String?>(true, {
            syncCompleted_.postValue(false)
            retrySyncShouldBeDone_.postValue(false)
            allTasksSuccess_ = false
            saveWalletProfitable_ = false
            walletSyncCore()
            null
        }, object : SimpleCallback<String?> {
            override fun onComplete(result: String?) {
                keepUnfollowedPcodesFromBackup(backupPcodeLabels)
                saveWalletIfProfitable()
                syncCompleted_.postValue(true)
                vibrateForTermination()
                clearSubTaskInformation()
            }

            override fun onException(t: Throwable) {
                Log.e(TAG, "exception on startWalletSync", t)
                keepUnfollowedPcodesFromBackup(backupPcodeLabels)
                saveWalletIfProfitable()
                syncCompleted_.postValue(true)
                vibrateForTermination()
                clearSubTaskInformation()
            }
        })
    }

    private fun keepUnfollowedPcodesFromBackup(backupPcodeLabels: Map<String, String>) {
        val bip47Meta = BIP47Meta.getInstance()
        val pcodeLabels = bip47Meta.copyOfPcodeLabels
        backupPcodeLabels.forEach {pcode, label ->
            if (!pcodeLabels.containsKey(pcode)) {
                bip47Meta.putNotFoundPcodes(pcode, label)
            }
        }
    }

    private fun saveWalletIfProfitable() {
        if (saveWalletProfitable_) {
            viewModelScope.launch(Dispatchers.IO) { WalletUtil.saveWallet(getApplication()) }
        }
    }

    private fun clearSubTaskInformation() {
        if (allTasksSuccess_) {
            payNymContactsSyncProgressMessage_.postValue("")
        }
    }

    private fun vibrateForTermination() {
        if (allTasksSuccess_) {
            vibratePhone(hapticDaDuration, getApplication())
        } else {
            vibratePhone(hapticTadaPattern, getApplication())
        }
    }

    private fun walletSyncCore() {
        val currentState =
            currentStateOfTaskStatuses()
        val engineTerminatedJobAsMap: MutableMap<EnumSyncTask, EnumSyncTaskStatus> =
            Maps.newHashMap()

        for (syncTask in EnumSyncTask.entries) {
            if (engineTerminatedJobAsMap.containsKey(syncTask)) continue

            SimpleTaskRunner.create()
                .executeAsync<Boolean?>(true, { ThreadHelper.pauseMillisWithStatus(30000L) },
                    object : SimpleCallback<Boolean?> {
                        override fun onComplete(result: Boolean?) {
                            synchronized(SyncWalletModel::class.java) {
                                if (!engineTerminatedJobAsMap.containsKey(syncTask)) {
                                    currentState.removeAt(currentState.size - 1)
                                    currentState.add(
                                        Triple(
                                            syncTask,
                                            EnumSyncTaskStatus.IN_PROGRESS_LONG,
                                            "Task still in progress. Please continue to wait..."
                                        )
                                    )
                                    setTaskStatuses(Lists.newArrayList(currentState))
                                }
                            }
                        }
                    })

            ThreadHelper.pauseMillis(500L)
            currentState.add(Triple(syncTask, EnumSyncTaskStatus.IN_PROGRESS, ""))
            setTaskStatuses(Lists.newArrayList(currentState))
            ThreadHelper.pauseMillis(1000L)

            var status: EnumSyncTaskStatus
            var message = ""
            when (syncTask) {
                EnumSyncTask.DOJO_CONNECTED -> {
                    status = ensureDojoConnection()
                    if (status == EnumSyncTaskStatus.FAILED) {
                        message =
                            "Investigate. Unable to sync extended public keys and reusable payment codes.\nWallet resync will be required"
                    }
                }

                EnumSyncTask.SYNC_PUB_KEYS -> {
                    status = syncPubKeys()
                    if (status == EnumSyncTaskStatus.FAILED) {
                        message =
                            "Wallet balance may be inaccurate.\nWallet resync will be required."
                    }
                }

                EnumSyncTask.SYNC_PCODES -> {
                    status = syncPaymentCodes()
                    if (status == EnumSyncTaskStatus.FAILED) {
                        message =
                            "Wallet balance may be inaccurate.\nWallet resync will be required."
                    }
                }

                EnumSyncTask.PAYNYM -> {
                    status = loadPayNym()
                    if (status == EnumSyncTaskStatus.SKIPPED) {
                        message = "Not claimed"
                    }
                }

                EnumSyncTask.PAYNYM_CONTACT -> status = loadAndSyncPayNymContact()
            }
            synchronized(SyncWalletModel::class.java) {
                engineTerminatedJobAsMap[syncTask] = status
                currentState.removeAt(currentState.size - 1)
                currentState.add(
                    Triple(
                        syncTask,
                        status,
                        message
                    )
                )
            }

            if (syncTask == EnumSyncTask.DOJO_CONNECTED && status != EnumSyncTaskStatus.SUCCEEDED) {
                engineTerminatedJobAsMap[EnumSyncTask.SYNC_PUB_KEYS] = EnumSyncTaskStatus.SKIPPED
                engineTerminatedJobAsMap[EnumSyncTask.SYNC_PCODES] = EnumSyncTaskStatus.SKIPPED
                currentState.add(
                    Triple(
                        EnumSyncTask.SYNC_PUB_KEYS,
                        EnumSyncTaskStatus.SKIPPED,
                        "Skipped. Dojo is not reachable"
                    )
                )
                currentState.add(
                    Triple(
                        EnumSyncTask.SYNC_PCODES,
                        EnumSyncTaskStatus.SKIPPED,
                        "Skipped. Dojo is not reachable"
                    )
                )
            }

            if (syncTask == EnumSyncTask.PAYNYM) {
                if (status == EnumSyncTaskStatus.SKIPPED) {
                    engineTerminatedJobAsMap[EnumSyncTask.PAYNYM_CONTACT] =
                        EnumSyncTaskStatus.SKIPPED
                    currentState.add(
                        Triple(
                            EnumSyncTask.PAYNYM_CONTACT,
                            EnumSyncTaskStatus.SKIPPED,
                            "PayNym not claimed"
                        )
                    )
                } else {
                    shouldClaimedPayNym_.postValue(false)
                }
            }

            setTaskStatuses(Lists.newArrayList(currentState))
        }

        val taskStatusList: List<EnumSyncTaskStatus> =
            Lists.newArrayList(Sets.newHashSet(engineTerminatedJobAsMap.values))
        allTasksSuccess_ =
            taskStatusList.size == 1 && taskStatusList[0] == EnumSyncTaskStatus.SUCCEEDED && engineTerminatedJobAsMap.size == EnumSyncTask.entries.size

        if (engineTerminatedJobAsMap[EnumSyncTask.SYNC_PUB_KEYS] == EnumSyncTaskStatus.SUCCEEDED &&
            engineTerminatedJobAsMap[EnumSyncTask.SYNC_PCODES] == EnumSyncTaskStatus.SUCCEEDED
        ) {
            PrefsUtil.getInstance(getApplication()).setValue(PrefsUtil.WALLET_SCAN_COMPLETE, true)
            saveWalletProfitable_ = true
        } else {
            PrefsUtil.getInstance(getApplication()).setValue(PrefsUtil.WALLET_SCAN_COMPLETE, false)
            saveWalletProfitable_ = false
        }

        retrySyncShouldBeDone_.postValue(
            engineTerminatedJobAsMap[EnumSyncTask.SYNC_PUB_KEYS] != EnumSyncTaskStatus.SUCCEEDED ||
                    engineTerminatedJobAsMap[EnumSyncTask.SYNC_PCODES] != EnumSyncTaskStatus.SUCCEEDED ||
                    engineTerminatedJobAsMap[EnumSyncTask.PAYNYM] == EnumSyncTaskStatus.FAILED ||
                    engineTerminatedJobAsMap[EnumSyncTask.PAYNYM_CONTACT] == EnumSyncTaskStatus.FAILED)

    }

    private fun loadAndSyncPayNymContact(): EnumSyncTaskStatus {
        try {
            runBlocking {

                if (!loadWallet(getApplication())) {
                    throw AshigaruException("loadWallet() failed")
                }

                val friendPcodes = Sets.newHashSet(BIP47Meta.getInstance().pcodes)
                try {
                    if (friendPcodes.contains(BIP47Util.getInstance(getApplication()).paymentCode.toString())) {
                        friendPcodes.remove(BIP47Util.getInstance(getApplication()).paymentCode.toString())
                        BIP47Meta.getInstance()
                            .remove(BIP47Util.getInstance(getApplication()).paymentCode.toString())
                    }
                } catch (t: Throwable) {
                    Log.e(TAG, t.message, t)
                }

                async(Dispatchers.IO) {
                    addPaynymsToFollow(
                        friendPcodes,
                        getApplication()
                    )

                    if (!reinitBIP47Meta(getApplication())) {
                        throw AshigaruException("registerPayNymContact() failed")
                    }

                }.await()

                async(Dispatchers.IO) {
                    if (!syncPayNymContacts(BIP47Meta.getInstance().pcodes)) {
                        throw AshigaruException("not syncPayNymContacts")
                    }
                }.await()

                withContext(Dispatchers.Main) {
                    payNymContactsSyncProgressMessage_.postValue("Retrieving outgoing BIP47 connections...")
                }

                async(Dispatchers.IO) {
                    if (!retrievePayNymConnections(getApplication())) {
                        withContext(Dispatchers.Main) {
                            payNymContactsSyncProgressMessage_.postValue("Retrieving outgoing BIP47 connections was failed at least partially")
                        }
                        throw AshigaruException("issue on retrievePayNymConnections")
                    }
                }.await()
            }

            return EnumSyncTaskStatus.SUCCEEDED
        } catch (e: Throwable) {
            Log.e(TAG, "exception on loadAndSyncPayNymContact", e)
            return EnumSyncTaskStatus.FAILED
        }
    }

    suspend fun addPaynymsToFollow(pcodesToAdd: Collection<String>, context: Context): MutableSet<String> {

        val addedPcodes : MutableSet<String> = Sets.newHashSet()

        val pcode = BIP47Util.getInstance(context).paymentCode.toString()
        val jsonObject = getNymInfo(pcode, context)
        if (jsonObject.has("empty") || !jsonObject.has("codes")) {
            return addedPcodes
        }

        val nym = Gson().fromJson(jsonObject.toString(), NymResponse::class.java);

        val followingPcodes: MutableSet<String> = Sets.newHashSet()
        nym.following?.let { codes ->
            codes.forEach { paynym ->
                followingPcodes.add(paynym.code)
            }
        }

        val pcodeList : MutableList<String> = Lists.newArrayList()
        for (pcodeCandidate in CollectionUtils.emptyIfNull(pcodesToAdd)) {
            if (BIP47Meta.getInstance().getArchived(pcodeCandidate)) continue
            if (! followingPcodes.contains(pcodeCandidate)) {
                pcodeList.add(pcodeCandidate)
            }
        }

        val apiPayNymApiService = PayNymApiService(pcode, context)
        val totalToAdd = pcodeList.size
        val totalAdded = AtomicInteger(0)
        val totalNotFound = AtomicInteger(0)
        val totalFailed = AtomicInteger(0)
        runBlocking {
            val semaphore = Semaphore(4)
            val tasks = pcodeList.map { friendPcode ->
                withContext(Dispatchers.IO) {
                    async {
                        semaphore.withPermit {
                            try {

                                withContext(Dispatchers.Main) {
                                    payNymContactsSyncProgressMessage_.postValue(
                                        String.format(
                                            "Adding followers %s/%s (including %s not found, %s failed)",
                                            totalAdded.get(),
                                            totalToAdd,
                                            totalNotFound.get(),
                                            totalFailed.get()
                                        )
                                    )
                                }

                                executeNetworkTaskWithAttempts(3, 5_000L) {
                                    val response = apiPayNymApiService.follow(friendPcode)
                                    if (equalsIgnoreCase(response.message, "Not Found")) {
                                        totalNotFound.incrementAndGet();
                                    } else {
                                        addedPcodes.add(friendPcode)
                                    }
                                    totalAdded.incrementAndGet()
                                    withContext(Dispatchers.Main) {
                                        payNymContactsSyncProgressMessage_.postValue(
                                            String.format(
                                                "Adding followers %s/%s (including %s not found, %s failed)",
                                                totalAdded.get(),
                                                totalToAdd,
                                                totalNotFound.get(),
                                                totalFailed.get()
                                            )
                                        )
                                    }
                                }
                            } catch (e : Throwable) {
                                Log.e(TAG, "issue on adding as follow $friendPcode", e)
                                totalAdded.incrementAndGet()
                                totalFailed.incrementAndGet()
                                withContext(Dispatchers.Main) {
                                    payNymContactsSyncProgressMessage_.postValue(
                                        String.format(
                                            "Adding followers %s/%s (including %s not found, %s failed)",
                                            totalAdded.get(),
                                            totalToAdd,
                                            totalNotFound.get(),
                                            totalFailed.get()
                                        )
                                    )
                                }
                            }
                        }
                    }
                }
            }
            tasks.awaitAll()
        }
        withContext(Dispatchers.Main) {
            payNymContactsSyncProgressMessage_.postValue(
                String.format(
                    "Adding followers %s/%s (including %s not found, %s failed)",
                    totalAdded.get(),
                    totalToAdd,
                    totalNotFound.get(),
                    totalFailed.get()
                )
            )
        }
        val failed = totalFailed.get()
        if (failed > 0) {
            throw AshigaruException("issue on adding PayNym as following ($failed failed)")
        }
        return addedPcodes
    }

    suspend private fun syncPayNymContacts(friendPcodes : MutableSet<String>): Boolean {

        if (CollectionUtils.isEmpty(friendPcodes)) {
            return true
        }

        try {
            val friendCount = friendPcodes.size
            val friendSyncCount = AtomicInteger(0)
            val friendSyncFailCount = AtomicInteger(0)
            runBlocking {
                val semaphore = Semaphore(6)
                val tasks = friendPcodes.map {friendPcode ->
                    withContext(Dispatchers.IO) {
                        async {
                            semaphore.withPermit {
                                try {

                                    withContext(Dispatchers.Main) {
                                        payNymContactsSyncProgressMessage_.postValue(
                                            String.format(
                                                "Syncing BIP47 address indexes %s/%s (including %s failed)",
                                                friendSyncCount.get(),
                                                friendCount,
                                                friendSyncFailCount.get()
                                            )
                                        )
                                    }

                                    executeNetworkTaskWithAttempts(5, 10_000L) {
                                        synPayNym(friendPcode, false, getApplication())
                                        friendSyncCount.incrementAndGet()
                                        withContext(Dispatchers.Main) {
                                            payNymContactsSyncProgressMessage_.postValue(
                                                String.format(
                                                    "Syncing BIP47 address indexes %s/%s (including %s failed)",
                                                    friendSyncCount.get(),
                                                    friendCount,
                                                    friendSyncFailCount.get()
                                                )
                                            )

                                            Log.i(
                                                TAG,
                                                String.format(
                                                    "sync %s is done with success (%s/%s) and %s failed",
                                                    friendPcode,
                                                    friendSyncCount.get(),
                                                    friendCount,
                                                    friendSyncFailCount.get()
                                                )
                                            )
                                        }
                                    }

                                } catch (te : Throwable) {
                                    Log.e(TAG, "issue on synPayNym $friendPcode", te)
                                    friendSyncCount.incrementAndGet()
                                    friendSyncFailCount.incrementAndGet()
                                    withContext(Dispatchers.Main) {
                                        payNymContactsSyncProgressMessage_.postValue(
                                            String.format(
                                                "Syncing BIP47 address indexes %s/%s (including %s failed)",
                                                friendSyncCount.get(),
                                                friendCount,
                                                friendSyncFailCount.get()
                                            )
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
                tasks.awaitAll()
            }
            return friendSyncFailCount.get() <= 0
        } catch (e: Throwable) {
            Log.e(TAG, "issue on synPayNym set", e)
            return false
        }
    }

    private fun loadPayNym(): EnumSyncTaskStatus {
        val loadPayNymStatus: EnumSyncTaskStatus
        try {
            loadPayNymStatus = runBlocking {
                withContext(Dispatchers.IO) {
                    async {
                        val claimedAndFeaturedPayNym = isClaimedAndFeaturedPayNym(getApplication())
                        if (!claimedAndFeaturedPayNym.first) {
                            return@async EnumSyncTaskStatus.SKIPPED
                        }
                        if (!claimedAndFeaturedPayNym.second) {
                            executeFeaturePayNymUpdate(getApplication())
                        }
                        payNymName_.postValue(claimedAndFeaturedPayNym.third)

                        PrefsUtil.getInstance(getApplication()).setValue(PrefsUtil.PAYNYM_CLAIMED, true)
                        PrefsUtil.getInstance(getApplication())
                            .setValue(PrefsUtil.PAYNYM_BOT_NAME, claimedAndFeaturedPayNym.third)

                        EnumSyncTaskStatus.SUCCEEDED
                    }.await()
                }
            }
        } catch (e: Throwable) {
            Log.e(TAG, "exception on claimPayNym", e)
            return EnumSyncTaskStatus.FAILED
        }

        fetchPayNymBotImage()

        return loadPayNymStatus
    }

    private fun fetchPayNymBotImage() {
        try {
            val completable = BIP47Util.getInstance(getApplication()).fetchBotImage()
            compositeDisposable_.add(completable.subscribe())
            if (!completable.blockingAwait(10000L, TimeUnit.MILLISECONDS)) {
                Log.i(TAG, "PayNym bot image still downloading after more than 10 seconds")
            }
        } catch (e: Throwable) {
            Log.e(TAG, "issue on fetching PayNym bot image", e)
        }
    }

    private fun syncPaymentCodes(): EnumSyncTaskStatus {
        try {
            runBlocking {
                withContext(Dispatchers.IO) {
                    async {
                        if (!syncIncomingConnection()) {
                            throw AshigaruException("syncIncomingConnection failed")
                        }
                        true
                    }.await()
                }
            }
            return EnumSyncTaskStatus.SUCCEEDED
        } catch (e: Throwable) {
            Log.e(TAG, "exception on syncPaymentCodes", e)
            return EnumSyncTaskStatus.FAILED
        }
    }

    private fun syncPubKeys(): EnumSyncTaskStatus {
        try {
            if (!lockPubKeys()) {
                return EnumSyncTaskStatus.FAILED
            }
            return EnumSyncTaskStatus.SUCCEEDED
        } catch (e: Throwable) {
            Log.e(TAG, "exception on syncPubKeys", e)
            return EnumSyncTaskStatus.FAILED
        }
    }

    suspend private fun syncIncomingConnection(): Boolean {
        try {
            val networkParams = SamouraiWallet.getInstance().currentNetworkParams
            val pcode = BIP47Util.getInstance(getApplication()).paymentCode
            val myNotifAddr = pcode.notificationAddress(networkParams).addressString

            val txsClient = TxsClient.createTxsClient(getApplication())
            val pageSize = 50
            var pageIndex = 0
            var txsContent: PaginatedRawTxs?
            do {
                txsContent = paginatedRawTxs(txsClient, myNotifAddr, pageIndex++, pageSize)
                if (txsContent != null) {
                    for (tx in CollectionUtils.emptyIfNull(txsContent.txs)) {
                        if (nonNull(tx.hash)) {
                            executeNetworkTaskWithAttempts(3, 10_000L) {
                                val txContent = APIFactory.getInstance(getApplication())
                                    .getNotifTx(tx.hash, myNotifAddr)
                                if (isNull(txContent)) {
                                    throw AshigaruNetworkException("exception getNotifTx()")
                                }
                            }
                        }
                    }
                }
            } while (txsContent != null && !txsContent.shouldBeLastPage())
        } catch (e: Throwable) {
            Log.e(TAG, "issue on syncIncomingConnection", e)
            return false
        }

        return true
    }

    private fun lockPubKeys(): Boolean {
        try {
            runBlocking {
                ensureTrackPubAddresses(getApplication())
            }
            return true
        } catch (e : Throwable) {
            return false
        }
    }

    private fun ensureDojoConnection(): EnumSyncTaskStatus {
        try {
            if (! ConnectivityStatus.hasConnectivity(getApplication())) {
                return EnumSyncTaskStatus.FAILED
            }

            if (! isDojoRespond()) {
                return EnumSyncTaskStatus.FAILED
            }
            return EnumSyncTaskStatus.SUCCEEDED

        } catch (e: Throwable) {
            Log.e(TAG, "exception on ensureDojoConnection", e)
            return EnumSyncTaskStatus.FAILED
        }
    }

    private fun isDojoRespond(): Boolean {
        try {
            runBlocking {
                withContext(Dispatchers.IO) {
                    async {
                        checkDojoConnection(getApplication())
                    }.await()
                }
            }
            return true
        } catch (e : Throwable) {
            return false
        }
    }

    fun claimPayNymSync() {
        SimpleTaskRunner.create().executeAsync<String?>(true, {
            syncCompleted_.postValue(false)
            retrySyncShouldBeDone_.postValue(false)
            shouldClaimedPayNym_.postValue(false)
            allTasksSuccess_ = false
            saveWalletProfitable_ = false
            claimPayNymCore()
            null
        }, object : SimpleCallback<String?> {
            override fun onComplete(result: String?) {
                saveWalletIfProfitable()
                syncCompleted_.postValue(true)
                vibrateForTermination()
                clearSubTaskInformation()
                super.onComplete(result)
            }

            override fun onException(t: Throwable) {
                Log.e(TAG, "exception on claimPayNymSync", t)
                saveWalletIfProfitable()
                syncCompleted_.postValue(true)
                vibrateForTermination()
                clearSubTaskInformation()
                super.onException(t)
            }
        })
    }

    private fun claimPayNymCore() {
        val currentState: List<Triple<EnumSyncTask, EnumSyncTaskStatus, String>> =
            currentStateOfTaskStatuses()

        val newState: MutableList<Triple<EnumSyncTask, EnumSyncTaskStatus, String>> =
            Lists.newArrayList()

        for (aState in currentState) {
            if (aState.first.isAboutPayNym) {
                newState.add(Triple(aState.first, EnumSyncTaskStatus.LOCAL_IN_PROGRESS, ""))
            } else {
                newState.add(aState)
            }
        }

        ThreadHelper.pauseMillis(500L)
        setTaskStatuses(Lists.newArrayList(newState))
        ThreadHelper.pauseMillis(1000L)

        val engineTerminatedJobAsMap: MutableMap<EnumSyncTask, EnumSyncTaskStatus> =
            Maps.newHashMap()

        for (i in newState.indices) {
            val aState = newState[i]
            if (aState.first.isAboutPayNym) {
                val syncTask = aState.first

                if (engineTerminatedJobAsMap[EnumSyncTask.PAYNYM] == EnumSyncTaskStatus.FAILED) {
                    synchronized(SyncWalletModel::class.java) {
                        engineTerminatedJobAsMap[syncTask] = EnumSyncTaskStatus.SKIPPED
                        newState[i] = Triple(
                            syncTask,
                            EnumSyncTaskStatus.SKIPPED,
                            "Unable to claim PayNym.\nContinue, then try again later."
                        )
                        setTaskStatuses(Lists.newArrayList(newState))
                    }
                    continue
                }

                SimpleTaskRunner.create()
                    .executeAsync<Boolean?>(true, { ThreadHelper.pauseMillisWithStatus(30000L) },
                        object : SimpleCallback<Boolean?> {
                            override fun onComplete(result: Boolean?) {
                                synchronized(SyncWalletModel::class.java) {
                                    if (!engineTerminatedJobAsMap.containsKey(syncTask)) {
                                        for (k in newState.indices) {
                                            val statekk = newState[k]
                                            if (statekk.first == syncTask) {
                                                newState[k] = Triple(
                                                    statekk.first,
                                                    EnumSyncTaskStatus.LOCAL_IN_PROGRESS_LONG,
                                                    "Task still in progress. Please continue to wait..."
                                                )
                                            }
                                            setTaskStatuses(Lists.newArrayList(newState))
                                        }
                                    }
                                }
                            }
                        })

                var status: EnumSyncTaskStatus
                var message = ""
                when (syncTask) {
                    EnumSyncTask.PAYNYM -> {
                        status = claimPayNym()
                        if (status == EnumSyncTaskStatus.FAILED) {
                            message = "Unable to claim PayNym.\nContinue, then try again later."
                        }
                    }

                    EnumSyncTask.PAYNYM_CONTACT -> status = loadAndSyncPayNymContact()
                    else -> {
                        status = EnumSyncTaskStatus.SKIPPED
                        Log.w(TAG, String.format("unknown EnumSyncTask %s", syncTask))
                    }
                }
                if (status == EnumSyncTaskStatus.SUCCEEDED) {
                    saveWalletProfitable_ = true
                }

                synchronized(SyncWalletModel::class.java) {
                    engineTerminatedJobAsMap[syncTask] = status
                    newState[i] = Triple(syncTask, status, message)
                    setTaskStatuses(Lists.newArrayList(newState))
                }
            }
        }

        val taskStatusSet: MutableSet<EnumSyncTaskStatus> = Sets.newHashSet()
        val statusesByTask : MutableMap<EnumSyncTask, EnumSyncTaskStatus> = Maps.newHashMap()
        for ((task, statuses) in newState) {
            statusesByTask.put(task, statuses)
            taskStatusSet.add(statuses)
        }
        val taskStatusList: List<EnumSyncTaskStatus> = Lists.newArrayList(taskStatusSet)
        allTasksSuccess_ =
            taskStatusList.size == 1 && taskStatusList[0] == EnumSyncTaskStatus.SUCCEEDED && newState.size == EnumSyncTask.entries.size

        retrySyncShouldBeDone_.postValue(
            statusesByTask[EnumSyncTask.SYNC_PUB_KEYS] != EnumSyncTaskStatus.SUCCEEDED ||
                    statusesByTask[EnumSyncTask.SYNC_PCODES] != EnumSyncTaskStatus.SUCCEEDED ||
                    statusesByTask[EnumSyncTask.PAYNYM] != EnumSyncTaskStatus.SUCCEEDED ||
                    statusesByTask[EnumSyncTask.PAYNYM_CONTACT] != EnumSyncTaskStatus.SUCCEEDED)
    }

    private fun claimPayNym(): EnumSyncTaskStatus {
        try {

            val resultOfClaim = runBlocking {
                async(Dispatchers.IO) {
                    claim(getApplication())
                }.await()
            }

            if (!resultOfClaim.first) {
                return EnumSyncTaskStatus.FAILED
            }
            PrefsUtil.getInstance(getApplication()).setValue(PrefsUtil.PAYNYM_CLAIMED, true)
            val nymName = resultOfClaim.second
            PrefsUtil.getInstance(getApplication()).setValue(PrefsUtil.PAYNYM_BOT_NAME, nymName)
            payNymName_.postValue(nymName)
            fetchPayNymBotImage()

            return EnumSyncTaskStatus.SUCCEEDED
        } catch (e: Throwable) {
            Log.e(TAG, "exception on claimPayNym", e)
            return EnumSyncTaskStatus.FAILED
        }
    }

    override fun onCleared() {
        if (!compositeDisposable_.isDisposed) {
            compositeDisposable_.dispose()
        }
        super.onCleared()
    }
    companion object {
        private const val TAG = "SyncWalletModel"

        private fun simulateWalletSyncCore(): List<Triple<EnumSyncTask, EnumSyncTaskStatus, String>> {
            val currentState: MutableList<Triple<EnumSyncTask, EnumSyncTaskStatus, String>> =
                Lists.newArrayList()
            for (syncTask in EnumSyncTask.entries) {
                currentState.add(
                    Triple(
                        syncTask,
                        EnumSyncTaskStatus.provideRandomlyOneStatus(),
                        "123 soleil"
                    )
                )
            }
            return currentState
        }

        suspend fun retrievePayNymConnections(context: Context): Boolean {
            val addressSet = getAllDepositAddresses(context)
            addressSet.addAll(getAllPostMixAddresses(context))

            val pCodeByNotifAddr = trackAndGetNotifAddrToConnect(context)

            try {
                executeNetworkTaskWithAttempts(5, 10_000L) {
                    if (!retrievePayNymConnections(addressSet, pCodeByNotifAddr, context)) {
                        throw AshigaruException("Issue on retrievePayNymConnections. Cannot retrieve all PayNym connections")
                    }
                }
                return true
            } catch (e: Throwable) {
                Log.e(TAG, "issue on retrievePayNymConnections", e)
                return false
            }
        }

        private fun trackAndGetNotifAddrToConnect(context: Context): Map<String, String> {
            val pCodeByNotifAddr: MutableMap<String, String> = Maps.newConcurrentMap()

            runBlocking {
                withContext(Dispatchers.IO) {
                    val networkParams = SamouraiWallet.getInstance().currentNetworkParams
                    val semaphore = Semaphore(6)
                    val taskList: MutableList<Deferred<Any>> = arrayListOf()
                    for (aFriend in BIP47Meta.getInstance().followings) {
                        taskList.add(
                            async {
                                semaphore.withPermit {
                                    try {
                                        val paymentCode = PaymentCode(aFriend)
                                        val notifAddr =
                                            paymentCode.notificationAddress(networkParams).addressString
                                        executeNetworkTaskWithAttempts(5, 5_000L) {
                                            if (ensureTrackAddrOrXPub(
                                                addrOrXPub = notifAddr,
                                                addrType = EnumAddressType.BIP44_LEGACY,
                                                isAddr = true,
                                                context = context
                                            )) {
                                                pCodeByNotifAddr[notifAddr] = aFriend
                                            } else {
                                                Log.e(TAG, "cannot track notif addr of PayNym $paymentCode")
                                            }
                                        }
                                    } catch (e: Throwable) {
                                        Log.e(TAG, "issue on PayNym to try to connect", e)
                                    }
                                }
                            }
                        )
                    }
                    taskList.awaitAll()
                }
            }
            return pCodeByNotifAddr
        }

        private fun getAllPostMixAddresses(context: Context): Collection<String> {
            val addressSet: MutableSet<String> = Sets.newLinkedHashSet()
            addressSet.add(
                BIP84Util.getInstance(context).wallet.getAccount(SamouraiAccountIndex.POSTMIX)
                    .xpubstr()
            )
            return addressSet
        }

        private fun getAllDepositAddresses(context: Context): MutableSet<String> {
            val addressSet: MutableSet<String> = Sets.newLinkedHashSet()
            addressSet.add(
                BIP84Util.getInstance(context).wallet.getAccount(SamouraiAccountIndex.DEPOSIT)
                    .xpubstr()
            )
            addressSet.add(
                BIP49Util.getInstance(context).wallet.getAccount(SamouraiAccountIndex.DEPOSIT)
                    .xpubstr()
            )
            addressSet.add(
                HD_WalletFactory.getInstance(context).get().getAccount(SamouraiAccountIndex.DEPOSIT)
                    .xpubstr()
            )
            try {
                addressSet.addAll(BIP47Util.getBip47Addresses(context))
            } catch (e: Throwable) {
                Log.e(TAG, "issue on getBip47Addresses", e)
            }
            return addressSet
        }

        private fun retrievePayNymConnections(
            addressSet: Set<String>,
            pCodeByNotifAddr: Map<String, String>,
            context: Context
        ): Boolean {
            try {
                val bip47Meta = BIP47Meta.getInstance()

                val allCandidateTxHash =
                    getSpentTxHashes(addressSet, context)

                val notifTxHash =
                    getConnectionTxHashesByNotifAddr(pCodeByNotifAddr.keys, context)

                for (notifAddr in notifTxHash.keySet()) {
                    val txHashes = notifTxHash[notifAddr]
                    var validBlock: Long? = null
                    for ((txHash, second) in txHashes) {
                        val txInputs = allCandidateTxHash[txHash]
                        if (CollectionUtils.isNotEmpty(txInputs)) {
                            try {
                                val fetchTx = requestTxDetail(context, txHash)
                                if (ArrayUtils.isEmpty(fetchTx.outputs)) continue
                                if (fetchTx.outputs.size < 2) continue

                                for (out in fetchTx.outputs) {
                                    if (out.value == 0L && isNull(out.address) && nonNull(
                                            out.scriptpubkey
                                        )
                                    ) {
                                        validBlock = second
                                        break
                                    }
                                }

                                if (validBlock != null) {
                                    val pcode = pCodeByNotifAddr[notifAddr]
                                    val latestBlockHeight =
                                        APIFactory.getInstance(context).latestBlockHeight
                                    val status = if ((latestBlockHeight > validBlock)
                                    ) BIP47Meta.STATUS_SENT_CFM
                                    else BIP47Meta.STATUS_SENT_NO_CFM
                                    bip47Meta.setOutgoingStatus(pcode, txHash, status)
                                    break
                                }
                            } catch (e: Throwable) {
                                Log.e(
                                    TAG,
                                    "issue while checking details of tx to retrieves PayNyms connection",
                                    e
                                )
                            }
                        }
                    }
                }
            } catch (e: Throwable) {
                Log.e(TAG, "issue while retrieving PayNyms connection", e)
                return false
            }
            return true
        }

        private fun requestTxDetail(context: Context, txHash: String): TxDetail {
            val result = ArrayList<TxDetail>()
            runBlocking {
                withContext(Dispatchers.IO) {
                    async {
                        executeNetworkTaskWithAttempts(3, 10_000L) {
                            result.add(BackendApiAndroid.getInstance(context).fetchTx(txHash, true))
                        }
                    }.await()
                }
            }
            return result.get(0)
        }

        private fun getConnectionTxHashesByNotifAddr(
            notifAddressSet: Set<String>,
            context: Context
        ): ListMultimap<String, Pair<String, Long>> {
            val spentTxHashes =
                MultimapBuilder.hashKeys().arrayListValues().build<String, Pair<String, Long>>()

            if (notifAddressSet.isEmpty()) {
                return spentTxHashes
            }

            val notifTxValue = SendNotifTxFactory._bNotifTxValue.toLong()

            val addresses = Joiner.on('|').join(notifAddressSet)

            val txsClient = TxsClient.createTxsClient(context)
            val pageSize = 200
            var pageIndex = 0
            var txsContent: PaginatedRawTxs?
            do {
                txsContent = paginatedRawTxs(txsClient, addresses, pageIndex++, pageSize)
                if (txsContent != null) {
                    for (tx in CollectionUtils.emptyIfNull(txsContent.txs)) {
                        if (StringUtils.isBlank(tx.hash)) continue
                        if (CollectionUtils.isNotEmpty(tx.inputs)) continue
                        if (CollectionUtils.isEmpty(tx.out)) continue
                        if (tx.out.size != 1) continue
                        for (txInfoOut in tx.out) {
                            if (!notifAddressSet.contains(txInfoOut.addr)) continue
                            if (nonNull(txInfoOut.value) && txInfoOut.value == notifTxValue) {
                                spentTxHashes.put(txInfoOut.addr, Pair(tx.hash, tx.blockHeight))
                            }
                        }
                    }
                }
            } while (txsContent != null && !txsContent.shouldBeLastPage())

            return spentTxHashes
        }

        private fun getSpentTxHashes(
            addressSet: Set<String>,
            context: Context
        ): ListMultimap<String, Pair<String, Long>?> {
            val spentTxHashes =
                MultimapBuilder.hashKeys().arrayListValues().build<String, Pair<String, Long>?>()

            val addresses = Joiner.on('|').join(addressSet)

            val txsClient = TxsClient.createTxsClient(context)
            val pageSize = 200
            var pageIndex = 0
            var txsContent: PaginatedRawTxs?
            do {
                txsContent = paginatedRawTxs(txsClient, addresses, pageIndex++, pageSize)
                if (txsContent != null) {
                    for (tx in CollectionUtils.emptyIfNull(txsContent.txs)) {
                        if (isNull(tx.hash)) continue
                        if (CollectionUtils.isEmpty(tx.inputs)) continue
                        for (txInfoInput in tx.inputs) {
                            if (nonNull(txInfoInput.prevOut.value)) {
                                spentTxHashes.put(
                                    tx.hash,
                                    Pair(txInfoInput.prevOut.addr, tx.blockHeight)
                                )
                            }
                        }
                    }
                }
            } while (txsContent != null && !txsContent.shouldBeLastPage())

            return spentTxHashes
        }

        @Throws(Exception::class)
        suspend fun ensureTrackPubAddresses(context: Context) {

            withContext(Dispatchers.IO) {
                val tasks = listOf(

                    async {
                        executeNetworkTaskWithAttempts(3, 10_000L) {

                            val bip44Deposit = HD_WalletFactory.getInstance(context).get()
                                .getAccount(0).xpubstr()
                            ensureTrackAddrOrXPub(
                                addrOrXPub = bip44Deposit,
                                addrType = EnumAddressType.BIP44_LEGACY,
                                tag = PrefsUtil.XPUBPREREG,
                                context = context
                            )
                        }
                    },

                    async {
                        executeNetworkTaskWithAttempts(3, 10_000L) {

                            val bip49Deposit = BIP49Util.getInstance(context).wallet
                                .getAccount(0).xpubstr()
                            ensureTrackAddrOrXPub(
                                addrOrXPub = bip49Deposit,
                                addrType = EnumAddressType.BIP49_SEGWIT_COMPAT,
                                tag = PrefsUtil.XPUBPREREG,
                                context = context
                            )
                        }
                    },
                    async {
                        executeNetworkTaskWithAttempts(3, 10_000L) {

                            val bip84Deposit = BIP84Util.getInstance(context).wallet
                                .getAccount(0).xpubstr()
                            ensureTrackAddrOrXPub(
                                addrOrXPub = bip84Deposit,
                                addrType = EnumAddressType.BIP84_SEGWIT_NATIVE,
                                tag = PrefsUtil.XPUBPREREG,
                                context = context
                            )
                        }
                    },
                    async {
                        executeNetworkTaskWithAttempts(3, 10_000L) {

                            val acc = WhirlpoolMeta.getInstance(context).whirlpoolPremixAccount
                            val bip84Pre = BIP84Util.getInstance(context).wallet
                                .getAccount(acc).xpubstr()
                            ensureTrackAddrOrXPub(
                                addrOrXPub = bip84Pre,
                                addrType = EnumAddressType.BIP84_SEGWIT_NATIVE,
                                tag = PrefsUtil.XPUBPREREG,
                                context = context)
                        }
                    },
                    async {
                        executeNetworkTaskWithAttempts(3, 10_000L) {

                            val acc = WhirlpoolMeta.getInstance(context).whirlpoolPostmix
                            val bip84Post = BIP84Util.getInstance(context).wallet
                                .getAccount(acc).xpubstr()
                            ensureTrackAddrOrXPub(
                                addrOrXPub = bip84Post,
                                addrType = EnumAddressType.BIP84_SEGWIT_NATIVE,
                                tag = PrefsUtil.XPUBPOSTREG,
                                context = context)
                        }
                    },
                    async {
                        executeNetworkTaskWithAttempts(3, 10_000L) {

                            val acc = WhirlpoolMeta.getInstance(context).whirlpoolBadBank
                            val bip84BadBank =
                                BIP84Util.getInstance(context).wallet
                                    .getAccount(acc).xpubstr()
                            ensureTrackAddrOrXPub(
                                addrOrXPub = bip84BadBank,
                                addrType = EnumAddressType.BIP84_SEGWIT_NATIVE,
                                tag = PrefsUtil.XPUBBADBANKLOCK,
                                context = context)
                        }
                    },
                    async {
                        executeNetworkTaskWithAttempts(3, 10_000L) {

                            val acc = RicochetMeta.getInstance(context).ricochetAccount
                            val bip84Ric =
                                BIP84Util.getInstance(context).wallet
                                    .getAccount(acc).xpubstr()
                            ensureTrackAddrOrXPub(
                                addrOrXPub = bip84Ric,
                                addrType = EnumAddressType.BIP84_SEGWIT_NATIVE,
                                tag = PrefsUtil.XPUBRICOCHETREG,
                                context = context)
                        }
                    },
                    async {
                        executeNetworkTaskWithAttempts(3, 10_000L) {

                            val bip84SwapDep = BIP84Util.getInstance(context).wallet
                                    .getAccount(SamouraiAccountIndex.SWAPS_DEPOSIT).xpubstr()
                            ensureTrackAddrOrXPub(
                                addrOrXPub = bip84SwapDep,
                                addrType = EnumAddressType.BIP84_SEGWIT_NATIVE,
                                tag = PrefsUtil.XPUBSWAPDEPOLOCK,
                                context = context)
                        }
                    },
                    async {
                        executeNetworkTaskWithAttempts(3, 10_000L) {

                            val bip84SwapRefunds = BIP84Util.getInstance(context).wallet
                                .getAccount(SamouraiAccountIndex.SWAPS_REFUNDS).xpubstr()
                            ensureTrackAddrOrXPub(
                                addrOrXPub = bip84SwapRefunds,
                                addrType = EnumAddressType.BIP84_SEGWIT_NATIVE,
                                tag = PrefsUtil.XPUBSWAPREFUNDSLOCK,
                                context = context)
                        }
                    },
                    async {
                        executeNetworkTaskWithAttempts(3, 10_000L) {

                            val bip84SwapAsb = BIP84Util.getInstance(context).wallet
                                .getAccount(SamouraiAccountIndex.SWAPS_ASB).xpubstr()
                            ensureTrackAddrOrXPub(
                                addrOrXPub = bip84SwapAsb,
                                addrType = EnumAddressType.BIP84_SEGWIT_NATIVE,
                                tag = PrefsUtil.XPUBSWAPASBLOCK,
                                context = context)
                        }
                    }
                )
                tasks.awaitAll()
            }
        }

        suspend private fun loadWallet(context: Context): Boolean {
            try {
                runBlocking {
                    async(Dispatchers.IO) {
                        executeNetworkTaskWithAttempts(3, 10_000L) {
                            val walletContent = APIFactory.getInstance(context)
                                .getXPUB(getAllDepositAddresses(context), true)

                            if (nonNull(walletContent)) {
                                APIFactory.parseUnspentOutputs(walletContent.toString())
                                APIFactory.parseDynamicFees_bitcoind(walletContent)
                                APIFactory.parse1DollarFeesEstimator(walletContent)
                            } else {
                                throw AshigaruException("exception on loadWallet");
                            }
                        }
                    }.await()
                }
            } catch (e: Throwable) {
                Log.e(TAG, e.message, e)
                return false
            }
            return true
        }

        fun ensureTrackAddrOrXPub(
            addrOrXPub: String,
            addrType: EnumAddressType,
            tag: String? = null,
            isAddr: Boolean = false,
            context: Context
        ): Boolean {
            if (isAddr) {
                val rawWallet = WalletClient.createWalletClient(context).getRawWallet(addrOrXPub)
                if (rawWallet == null || CollectionUtils.isEmpty(rawWallet.txs)) {
                    return false
                }
            } else {
                val xPubClient = XPubClient.createXPubClient(context)
                if (!xPubClient.isTracked(addrType, addrOrXPub)) {
                    if (!xPubClient.track(
                            addrType,
                            addrOrXPub,
                            tag)
                    ) {
                        throw AshigaruException("failed to track $addrType")
                    }
                }
            }
            return true
        }

        fun paginatedRawTxs(
            txsClient: TxsClient,
            addresses: String?,
            pageIndex: Int,
            pageSize: Int
        ): PaginatedRawTxs? {

            val result = ArrayList<PaginatedRawTxs>()
            runBlocking {
                withContext(Dispatchers.IO) {
                    async {
                        executeNetworkTaskWithAttempts(3, 10_000L) {
                            result.add(txsClient.getPage(addresses, pageIndex, pageSize))
                        }
                    }.await()
                }
            }
            return if (result.isEmpty()) null else result.get(0)
        }
    }

}
