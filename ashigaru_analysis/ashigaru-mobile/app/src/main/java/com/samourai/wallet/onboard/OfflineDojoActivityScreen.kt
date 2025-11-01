package com.samourai.wallet.onboard

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import com.samourai.wallet.R
import com.samourai.wallet.databinding.ActivityOfflineModeDojoBinding


class OfflineDojoActivityScreen : AppCompatActivity() {

    private lateinit var binding: ActivityOfflineModeDojoBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityOfflineModeDojoBinding.inflate(layoutInflater)
        setContentView(binding.root)
        window.statusBarColor = ContextCompat.getColor(this, R.color.offline_dojo_background);
        binding.nextBtn.setOnClickListener {
            val newIntent = Intent(this, SetDojoActivity::class.java)
            if (intent.hasExtra("dojoURL")) {
                newIntent.putExtra("dojoURL", intent.getStringExtra("dojoURL"))
                newIntent.putExtra("explorerURL", intent.getStringExtra("explorerURL"))
                newIntent.putExtra("apikey", intent.getStringExtra("apikey"))
            }
            startActivity(newIntent)
        }
    }
}