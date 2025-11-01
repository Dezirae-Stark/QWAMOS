package com.samourai.whirlpool.protocol.soroban.payload.mix;

import com.samourai.whirlpool.protocol.soroban.payload.beans.MixStatus;

public class MixStatusResponseRegisterOutput extends AbstractMixStatusResponse {
  public String inputsHash;

  public MixStatusResponseRegisterOutput() {
    this(null);
  }

  public MixStatusResponseRegisterOutput(String inputsHash) {
    super(MixStatus.REGISTER_OUTPUT);
    this.inputsHash = inputsHash;
  }
}
