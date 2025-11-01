package com.samourai.whirlpool.protocol.soroban.payload.mix;

import com.samourai.soroban.client.AbstractSorobanPayloadable;

public class ConfirmInputResponse extends AbstractSorobanPayloadable {
  public String signedBordereau64;

  public ConfirmInputResponse() {}

  public ConfirmInputResponse(String signedBordereau64) {
    this.signedBordereau64 = signedBordereau64;
  }
}
