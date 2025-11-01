package com.samourai.whirlpool.protocol;

import com.samourai.wallet.util.Util;
import com.samourai.wallet.util.Z85;
import com.samourai.whirlpool.protocol.beans.Utxo;
import java.util.*;

public class WhirlpoolProtocol {
  public static final String PARTNER_ID_SAMOURAI = "SAMOURAI";

  private static final Z85 z85 = Z85.getInstance();

  public WhirlpoolProtocol() {}

  public static long computePremixBalanceMin(
      long denomination, long mustMixBalanceMin, boolean liquidity) {
    return liquidity ? denomination : mustMixBalanceMin;
  }

  public static long computePremixBalanceMax(
      long denomination, long mustMixBalanceMax, boolean liquidity) {
    return liquidity ? denomination : mustMixBalanceMax;
  }

  public static String computeInputsHash(Collection<Utxo> utxos) {
    List inputs = new ArrayList();
    Iterator var2 = utxos.iterator();

    while (var2.hasNext()) {
      Utxo utxo = (Utxo) var2.next();
      inputs.add(utxo.getHash() + String.valueOf(utxo.getIndex()));
    }

    Collections.sort(inputs);
    String inputsString = joinStrings(";", inputs);
    return Util.sha512Hex(inputsString);
  }

  private static String joinStrings(String delimiter, Collection<String> strings) {
    StringBuilder sb = new StringBuilder();
    boolean first = true;

    for (Iterator var4 = strings.iterator(); var4.hasNext(); first = false) {
      String str = (String) var4.next();
      if (!first) {
        sb.append(delimiter);
      }

      sb.append(str);
    }

    return sb.toString();
  }

  public static byte[] decodeBytes(String encoded) {
    return encoded == null ? null : z85.decode(encoded);
  }

  public static String encodeBytes(byte[] data) {
    return data == null ? null : z85.encode(data);
  }
}
