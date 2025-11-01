package com.samourai.whirlpool.protocol.soroban.exception;

import com.samourai.soroban.client.exception.SorobanException;
import com.samourai.whirlpool.protocol.soroban.payload.beans.PushTxError;

public class PushTxErrorException extends SorobanException {
  private PushTxError pushTxError;

  public PushTxErrorException(PushTxError pushTxError) {
    super("pushTx error: " + pushTxError.error);
    this.pushTxError = pushTxError;
  }

  public PushTxError getPushTxError() {
    return pushTxError;
  }
}
