package com.samourai.whirlpool.protocol.soroban.payload.mix;

import com.samourai.whirlpool.protocol.soroban.payload.beans.MixStatus;

public class MixStatusResponseConfirmInput extends AbstractMixStatusResponse {

  public MixStatusResponseConfirmInput() {
    super(MixStatus.CONFIRM_INPUT);
  }
}
