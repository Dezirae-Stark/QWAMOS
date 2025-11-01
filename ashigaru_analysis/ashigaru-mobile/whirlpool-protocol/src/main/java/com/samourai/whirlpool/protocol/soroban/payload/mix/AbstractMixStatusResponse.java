package com.samourai.whirlpool.protocol.soroban.payload.mix;

import com.samourai.soroban.client.AbstractSorobanPayloadable;
import com.samourai.whirlpool.protocol.soroban.payload.beans.MixStatus;

public abstract class AbstractMixStatusResponse extends AbstractSorobanPayloadable {
  public MixStatus mixStatus;

  public AbstractMixStatusResponse() {}

  public AbstractMixStatusResponse(MixStatus mixStatus) {
    this.mixStatus = mixStatus;
  }
}
