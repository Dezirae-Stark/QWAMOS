package com.samourai.whirlpool.protocol.soroban.payload.registerInput;

import com.samourai.soroban.client.AbstractSorobanPayloadable;

public class RegisterInputRequest extends AbstractSorobanPayloadable {
  public String utxoHash;
  public long utxoIndex;
  public String signature;
  public int blockHeight;

  public RegisterInputRequest() {}

  public RegisterInputRequest(String utxoHash, long utxoIndex, String signature, int blockHeight) {
    this.utxoHash = utxoHash;
    this.utxoIndex = utxoIndex;
    this.signature = signature;
    this.blockHeight = blockHeight;
  }
}
