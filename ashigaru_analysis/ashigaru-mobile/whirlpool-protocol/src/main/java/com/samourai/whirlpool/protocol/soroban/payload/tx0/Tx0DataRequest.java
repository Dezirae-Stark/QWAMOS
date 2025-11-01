package com.samourai.whirlpool.protocol.soroban.payload.tx0;

import com.samourai.soroban.client.AbstractSorobanPayloadable;

public class Tx0DataRequest extends AbstractSorobanPayloadable {
  public String scode;
  public String partnerId;

  public Tx0DataRequest() {}

  public Tx0DataRequest(String scode, String partnerId) {
    this.scode = scode;
    this.partnerId = partnerId;
  }
}
