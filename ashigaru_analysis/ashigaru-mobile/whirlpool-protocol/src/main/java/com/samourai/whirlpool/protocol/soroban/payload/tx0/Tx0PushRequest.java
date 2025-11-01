package com.samourai.whirlpool.protocol.soroban.payload.tx0;

import com.samourai.soroban.client.AbstractSorobanPayloadable;

public class Tx0PushRequest extends AbstractSorobanPayloadable {
  public String tx64;
  public String poolId;

  public Tx0PushRequest() {}

  public Tx0PushRequest(String tx64, String poolId) {
    this.tx64 = tx64;
    this.poolId = poolId;
  }
}
