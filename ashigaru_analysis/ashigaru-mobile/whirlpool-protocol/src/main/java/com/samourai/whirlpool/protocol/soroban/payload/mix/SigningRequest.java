package com.samourai.whirlpool.protocol.soroban.payload.mix;

import com.samourai.soroban.client.AbstractSorobanPayloadable;

public class SigningRequest extends AbstractSorobanPayloadable {
  public String[] witnesses64;

  public SigningRequest() {}

  public SigningRequest(String[] witnesses64) {
    this.witnesses64 = witnesses64;
  }
}
