package com.samourai.whirlpool.protocol.soroban.payload.tx0;

import com.samourai.soroban.protocol.payload.SorobanErrorMessage;
import com.samourai.whirlpool.protocol.WhirlpoolErrorCode;
import com.samourai.whirlpool.protocol.soroban.payload.beans.PushTxError;

public class Tx0PushResponseError extends SorobanErrorMessage {
  public PushTxError pushTxError;

  public Tx0PushResponseError() {}

  public Tx0PushResponseError(String message, PushTxError pushTxError) {
    super(WhirlpoolErrorCode.PUSHTX_ERROR, message);
    this.pushTxError = pushTxError;
  }

  @Override
  public String toString() {
    return "PushTxErrorResponse{"
        + "pushTxError='"
        + pushTxError
        + "', message='"
        + message
        + '\''
        + '}';
  }
}
