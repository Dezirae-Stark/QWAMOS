package org.bitcoinj.core;

import org.bitcoinj.crypto.TransactionSignature;

import java.io.ByteArrayOutputStream;

public class TransactionWitness {
    static TransactionWitness empty = new TransactionWitness(0);

    public static TransactionWitness getEmpty() {
        return empty;
    }

    byte[][] pushes;

    public TransactionWitness(int pushCount) {
        pushes = new byte[pushCount][];
    }

    public byte[] getPush(int i) {
        return pushes[i];
    }

    public int getPushCount() {
        return pushes.length;
    }

    public void setPush(int i, byte[] value) {
        pushes[i] = value;
    }

    /**
     * Create a witness that can redeem a pay-to-witness-pubkey-hash output.
     */
    public static TransactionWitness createWitness(final TransactionSignature signature, final ECKey pubKey) {
        final byte[] sigBytes = signature != null ? signature.encodeToBitcoin() : new byte[]{};
        final byte[] pubKeyBytes = pubKey.getPubKey();
        final TransactionWitness witness = new TransactionWitness(2);
        witness.setPush(0, sigBytes);
        witness.setPush(1, pubKeyBytes);
        return witness;
    }

    public static TransactionWitness createTaprootWitness(byte[] schnorrSig, Transaction.SigHash mode, boolean anyoneCanPay) {
        TransactionWitness witness = new TransactionWitness(1);
        if(mode == Transaction.SigHash.UNSET) {
            witness.setPush(0, schnorrSig);
        } else {
            witness.setPush(0, witness.encodeSchnorrToBitcoin(schnorrSig, mode, anyoneCanPay)); // signature
        }

        return witness;
    }

    private byte[] encodeSchnorrToBitcoin(byte[] schnorrSig, Transaction.SigHash mode, boolean anyoneCanPay) {
        ByteArrayOutputStream bos = new ByteArrayOutputStream(schnorrSig.length);
        bos.write(schnorrSig, 0, schnorrSig.length);
        bos.write(TransactionSignature.calcSigHashValue(mode, anyoneCanPay));
        return bos.toByteArray();
    }
}
