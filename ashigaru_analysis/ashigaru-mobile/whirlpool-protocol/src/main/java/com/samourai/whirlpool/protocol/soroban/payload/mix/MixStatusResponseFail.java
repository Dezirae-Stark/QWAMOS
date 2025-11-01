package com.samourai.whirlpool.protocol.soroban.payload.mix;

import com.samourai.whirlpool.protocol.soroban.payload.beans.BlameReason;
import com.samourai.whirlpool.protocol.soroban.payload.beans.MixStatus;

public class MixStatusResponseFail extends AbstractMixStatusResponse {
  public BlameReason blame; // null when client is not faulty

  public MixStatusResponseFail() {
    this(null);
  }

  public MixStatusResponseFail(BlameReason blame) {
    super(MixStatus.FAIL);
    this.blame = blame;
  }
}
