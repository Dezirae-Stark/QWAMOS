package com.samourai.whirlpool.protocol.soroban.payload.mix;

import com.samourai.soroban.client.AbstractSorobanPayloadable;

public class RevealOutputRequest extends AbstractSorobanPayloadable {
  public String receiveAddress;

  public RevealOutputRequest() {}

  public RevealOutputRequest(String receiveAddress) {
    this.receiveAddress = receiveAddress;
  }
}
