package com.samourai.whirlpool.protocol.soroban.payload.registerInput;

import com.samourai.soroban.client.AbstractSorobanPayloadable;

public class RegisterInputResponse extends AbstractSorobanPayloadable {
  public String mixId;
  public byte[] mixPublicKey;

  public RegisterInputResponse() {}

  public RegisterInputResponse(String mixId, byte[] mixPublicKey) {
    this.mixId = mixId;
    this.mixPublicKey = mixPublicKey;
  }
}
