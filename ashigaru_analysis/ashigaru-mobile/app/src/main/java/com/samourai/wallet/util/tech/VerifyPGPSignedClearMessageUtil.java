package com.samourai.wallet.util.tech;


import static org.apache.commons.lang3.StringUtils.strip;

import android.util.Log;

import org.bouncycastle.bcpg.ArmoredInputStream;
import org.bouncycastle.jce.provider.BouncyCastleProvider;
import org.bouncycastle.openpgp.PGPObjectFactory;
import org.bouncycastle.openpgp.PGPPublicKey;
import org.bouncycastle.openpgp.PGPPublicKeyRingCollection;
import org.bouncycastle.openpgp.PGPSignature;
import org.bouncycastle.openpgp.PGPSignatureList;
import org.bouncycastle.openpgp.PGPUtil;
import org.bouncycastle.openpgp.jcajce.JcaPGPPublicKeyRingCollection;
import org.bouncycastle.openpgp.operator.jcajce.JcaKeyFingerprintCalculator;
import org.bouncycastle.openpgp.operator.jcajce.JcaPGPContentVerifierBuilderProvider;

import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.security.Provider;
import java.security.Security;

public class VerifyPGPSignedClearMessageUtil {

    private static final String TAG = "VerifyPGPSignedClear";

    private VerifyPGPSignedClearMessageUtil() {}

    public static boolean verifySignedMessage(String signedMessageAscii, String pubKeyAscii) {

        try (final ArmoredInputStream isMessage =
                     new ArmoredInputStream(
                             new ByteArrayInputStream(signedMessageAscii.getBytes()));
             final ByteArrayOutputStream temp = new ByteArrayOutputStream(isMessage.available())) {

            while (true) {
                int c = isMessage.read();
                if (c == -1)
                    throw new IOException("Unexpected end of file");
                if (!isMessage.isClearText())
                    break;
                temp.write(c);
            }
            final byte clearText[] = temp.toByteArray();

            final PGPObjectFactory pgpFact = new PGPObjectFactory(isMessage, new JcaKeyFingerprintCalculator());
            final PGPSignatureList p3 = (PGPSignatureList) pgpFact.nextObject();
            final PGPSignature sig = p3.get(0);

            final PGPPublicKeyRingCollection pubKeyRing = new JcaPGPPublicKeyRingCollection(PGPUtil.getDecoderStream(new ByteArrayInputStream(pubKeyAscii.getBytes())));
            final PGPPublicKey publicKey = pubKeyRing.getPublicKey(sig.getKeyID());

            final Provider bcProvider = new BouncyCastleProvider();
            Security.removeProvider(bcProvider.getName());
            Security.addProvider(bcProvider);

            sig.init(new JcaPGPContentVerifierBuilderProvider().setProvider("BC"), publicKey);
            // RFC 4880, section 7: http://tools.ietf.org/html/rfc4880#section-7
            // The signature must be validated using clear text:
            // - without trailing white spaces on every line
            // - using CR LF line endings, no matter what the original line ending is
            // - without the latest line ending
            BufferedReader textIn = new BufferedReader(new InputStreamReader(new ByteArrayInputStream(clearText)));
            while (true) {
                // remove trailing whitespace and line endings
                final String aRawLine = textIn.readLine();
                final String strippedLine = strip(aRawLine, " \t\n\r\f");
                sig.update(strippedLine.getBytes());
                if (!textIn.ready()) // skip latest line ending
                    break;
                // always use CR LF
                sig.update((byte) '\r');
                sig.update((byte) '\n');
            }

            return sig.verify();
        } catch (Exception e) {
            Log.e(TAG, e.getMessage());
            return false;
        }
    }

}