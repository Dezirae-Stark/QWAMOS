package com.samourai.whirlpool.protocol.soroban.payload.mix;

import com.samourai.whirlpool.protocol.soroban.payload.beans.MixStatus;

public class MixStatusResponseSigning extends AbstractMixStatusResponse {
  public String transaction64;

  public MixStatusResponseSigning() {
    this(null);
  }

  public MixStatusResponseSigning(String transaction64) {
    super(MixStatus.SIGNING);
    this.transaction64 = transaction64;
  }
}
