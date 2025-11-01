package com.samourai.whirlpool.protocol.soroban.payload.tx0;

import com.samourai.soroban.client.AbstractSorobanPayloadable;

public class Tx0PushResponseSuccess extends AbstractSorobanPayloadable {
  public String txid;

  public Tx0PushResponseSuccess() {}

  public Tx0PushResponseSuccess(String txid) {
    this.txid = txid;
  }
}
