package com.samourai.wallet.onboard

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import com.samourai.wallet.CreateWalletActivity
import com.samourai.wallet.R
import com.samourai.wallet.databinding.CreateOrRestoreBinding


class CreateOrRestoreActivity : AppCompatActivity() {

    private lateinit var binding: CreateOrRestoreBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = CreateOrRestoreBinding.inflate(layoutInflater)
        setContentView(binding.root)
        window.statusBarColor = ContextCompat.getColor(this, R.color.networking);
        binding.createNew.setOnClickListener {
            startActivity(Intent(this, CreateWalletActivity::class.java))
        }

        binding.restoreWallet.setOnClickListener {
            startActivity(Intent(this, RestoreOptionActivity::class.java))
        }
    }

}