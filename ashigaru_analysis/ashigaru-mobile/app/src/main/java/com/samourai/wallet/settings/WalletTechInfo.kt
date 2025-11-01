package com.samourai.wallet.settings

import android.os.Bundle
import android.widget.TextView
import com.samourai.wallet.R
import com.samourai.wallet.SamouraiActivity
import com.samourai.wallet.SamouraiWallet
import com.samourai.wallet.constants.BIP_WALLET
import com.samourai.wallet.constants.WALLET_INDEX
import com.samourai.wallet.util.func.AddressFactory

class WalletTechInfo : SamouraiActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_wallet_info)

        setSupportActionBar(findViewById(R.id.toolbar))
        if (supportActionBar != null) {
            supportActionBar!!.setDisplayHomeAsUpEnabled(true)
        }
        window.statusBarColor = resources.getColor(R.color.toolbar)
        window.navigationBarColor = resources.getColor(R.color.networking)

        if (SamouraiWallet.getInstance().isTestNet) {
            findViewById<TextView>(R.id.POSTMIX_LEGACY_path).text = "m/84'/1'/2147483646'"
            findViewById<TextView>(R.id.POSTMIX_COMPAT_path).text = "m/84'/1'/2147483646'"
            for (bipWallet in BIP_WALLET.entries) {
                val pathName = bipWallet.name + "_path"
                val pathResource = resources.getIdentifier(pathName, "id", packageName)
                val pathText = findViewById<TextView>(pathResource)

                if (pathText!=null) {
                    val pathList = pathText.text.split("/").toMutableList()
                    pathList[2] = "1'"
                    val newPathText = pathList.joinToString("/")
                    pathText.text = newPathText
                }
            }
        }

        for (walletIndex in WALLET_INDEX.entries) {
            val blockchainCount = AddressFactory.getInstance(applicationContext).debugIndex(walletIndex).split(";")[0]
            val internalCount = AddressFactory.getInstance(applicationContext).debugIndex(walletIndex).split(";")[1]

            val blockchainName = walletIndex.name + "_BLOCKCHAIN"
            val blockchainResource = resources.getIdentifier(blockchainName, "id", packageName)
            val internalName = walletIndex.name + "_INTERNAL"
            val internalResource = resources.getIdentifier(internalName, "id", packageName)


            val blockchainCountText = findViewById<TextView>(blockchainResource)
            val internalCountText = findViewById<TextView>(internalResource)
            if (blockchainCountText!=null && internalCountText != null) {
                blockchainCountText.text = blockchainCount
                internalCountText.text = internalCount
            }
        }
    }
}