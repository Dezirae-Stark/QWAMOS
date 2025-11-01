package com.samourai.wallet.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider

class CustomPrefViewModelFactory : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(CustomPreferenceViewModel::class.java)) {
            return CustomPreferenceViewModel() as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}
