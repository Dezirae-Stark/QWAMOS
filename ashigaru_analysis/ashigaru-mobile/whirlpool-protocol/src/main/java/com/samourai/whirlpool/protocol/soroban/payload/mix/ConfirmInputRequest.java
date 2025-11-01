package com.samourai.whirlpool.protocol.soroban.payload.mix;

import com.samourai.soroban.client.AbstractSorobanPayloadable;

public class ConfirmInputRequest extends AbstractSorobanPayloadable {
  public String blindedBordereau64;
  public String userHash;

  public ConfirmInputRequest() {}

  public ConfirmInputRequest(String blindedBordereau64, String userHash) {
    this.blindedBordereau64 = blindedBordereau64;
    this.userHash = userHash;
  }
}
