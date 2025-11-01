package com.samourai.wallet.api.wallet;

import static java.util.Objects.isNull;

import android.util.Log;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableList;
import com.samourai.wallet.api.txs.TxInfo;

import org.jetbrains.annotations.NotNull;

import java.util.List;
import java.util.Map;

public class RawWallet {

    public static final String TAG = "RawWallet";

    private static final ObjectMapper objectMapper = new ObjectMapper();

    private final Map<String, Object> entity;

    private RawWallet(final Map<String, Object> entity) {
        this.entity = entity;
    }

    public static RawWallet createRawWallet(final Map<String, Object> entity) {
        return new RawWallet(entity);
    }

    public Map<String, Object> getEntity() {
        return entity;
    }

    @NotNull
    public List<TxInfo> getTxs() {
        final Object txsObject = entity.get("txs");
        if (isNull(txsObject)) return ImmutableList.of();
        try {
            final String txsPlainText = objectMapper.writeValueAsString(txsObject);
            return objectMapper.readValue(
                    txsPlainText,
                    new TypeReference<List<TxInfo>>() {});
        } catch (final Exception e) {
            Log.e(TAG, e.getMessage());
        }
        return ImmutableList.of();
    }
}
