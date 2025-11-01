package com.samourai.wallet.settings

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel

class CustomPreferenceViewModel : ViewModel() {
    private val _isSwitchOn = MutableLiveData<Boolean>().apply { value = false }
    val isSwitchOn: LiveData<Boolean> get() = _isSwitchOn

    private val _prefToChange = MutableLiveData<String>().apply { value = "" }
    val prefToChange: LiveData<String> get() = _prefToChange

    fun setSwitchState(isOn: Boolean) {
        _isSwitchOn.value = isOn
    }

    fun setPrefToChange (pref: String) {
        _prefToChange.value = pref
    }
}

