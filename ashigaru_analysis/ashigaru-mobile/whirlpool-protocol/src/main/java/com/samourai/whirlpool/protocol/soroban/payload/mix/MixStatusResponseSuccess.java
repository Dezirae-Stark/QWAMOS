package com.samourai.whirlpool.protocol.soroban.payload.mix;

import com.samourai.whirlpool.protocol.soroban.payload.beans.MixStatus;

public class MixStatusResponseSuccess extends AbstractMixStatusResponse {
  public String txid;

  public MixStatusResponseSuccess() {
    this(null);
  }

  public MixStatusResponseSuccess(String txid) {
    super(MixStatus.SUCCESS);
    this.txid = txid;
  }
}
