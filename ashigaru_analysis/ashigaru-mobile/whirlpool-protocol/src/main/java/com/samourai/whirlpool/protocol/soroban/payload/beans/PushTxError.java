package com.samourai.whirlpool.protocol.soroban.payload.beans;

import java.util.Collection;

public class PushTxError {
  public String error;
  public Collection<Integer> voutsAddressReuse;

  public PushTxError() {}

  public PushTxError(String error, Collection<Integer> voutsAddressReuse) {
    this.error = error;
    this.voutsAddressReuse = voutsAddressReuse;
  }

  public PushTxError(String error) {
    this(error, null);
  }

  @Override
  public String toString() {
    return "PushTxErrorResponse{"
        + "error='"
        + error
        + '\''
        + ", voutsAddressReuse="
        + voutsAddressReuse
        + '}';
  }
}
