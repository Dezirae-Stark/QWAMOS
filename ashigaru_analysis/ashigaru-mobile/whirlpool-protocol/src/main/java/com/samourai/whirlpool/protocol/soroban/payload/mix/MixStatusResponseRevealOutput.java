package com.samourai.whirlpool.protocol.soroban.payload.mix;

import com.samourai.whirlpool.protocol.soroban.payload.beans.MixStatus;

public class MixStatusResponseRevealOutput extends AbstractMixStatusResponse {

  public MixStatusResponseRevealOutput() {
    super(MixStatus.REVEAL_OUTPUT);
  }
}
