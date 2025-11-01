package com.samourai.whirlpool.protocol.soroban.payload.upStatus;

import com.samourai.soroban.client.AbstractSorobanPayloadable;

public class UpStatusMessage extends AbstractSorobanPayloadable {
  public String origin;

  public UpStatusMessage() {}

  public UpStatusMessage(String origin) {
    this.origin = origin;
  }
}
