package com.samourai.wallet.util.func;

import static org.apache.commons.lang3.StringUtils.startsWith;

import com.samourai.wallet.send.UTXO;

import org.apache.commons.collections4.CollectionUtils;

import java.util.Collection;

public class UTXOHelper {

    private UTXOHelper() {}

    public static boolean hasPath(final Collection<UTXO> utxos, final String path) {
        for (final UTXO utxo : CollectionUtils.emptyIfNull(utxos)) {
            if (startsWith(utxo.getPath(), path)) {
                return true;
            }
        }
        return false;
    }
}
