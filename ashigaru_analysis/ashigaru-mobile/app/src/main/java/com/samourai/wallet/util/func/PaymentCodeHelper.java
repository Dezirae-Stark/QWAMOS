package com.samourai.wallet.util.func;

import org.apache.commons.lang3.tuple.Pair;
import org.bitcoinj.core.AddressFormatException;
import org.bitcoinj.core.Base58;
import org.bitcoinj.crypto.DeterministicKey;
import org.bitcoinj.crypto.HDKeyDerivation;

import java.nio.ByteBuffer;

public class PaymentCodeHelper {
    private static final int PUBLIC_KEY_X_LEN = 32;
    private static final int PUBLIC_KEY_Y_LEN = 1;
    private static final int CHAIN_LEN = 32;

    private PaymentCodeHelper() {}

    public static Pair<byte[], byte[]> parse(final String paymentCodeStr) throws AddressFormatException {
        byte[] pcBytes = Base58.decodeChecked(paymentCodeStr);

        ByteBuffer bb = ByteBuffer.wrap(pcBytes);
        if(bb.get() != 0x47)   {
            throw new AddressFormatException("invalid payment code version");
        }

        byte[] chain = new byte[CHAIN_LEN];
        byte[] pub = new byte[PUBLIC_KEY_X_LEN + PUBLIC_KEY_Y_LEN];

        // type:
        bb.get();
        // features:
        bb.get();

        bb.get(pub);
        if(pub[0] != 0x02 && pub[0] != 0x03)   {
            throw new AddressFormatException("invalid public key");
        }

        bb.get(chain);

        return Pair.of(pub, chain);
    }

    public static DeterministicKey toDeterministicKey(final String paymenyCodeStr) {
        final Pair<byte[], byte[]> pair = parse(paymenyCodeStr);
        return HDKeyDerivation.createMasterPubKeyFromBytes(pair.getLeft(), pair.getRight());
    }
}
