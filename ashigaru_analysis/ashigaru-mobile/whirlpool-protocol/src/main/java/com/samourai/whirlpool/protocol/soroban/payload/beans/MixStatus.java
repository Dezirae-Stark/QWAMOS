package com.samourai.whirlpool.protocol.soroban.payload.beans;

public enum MixStatus {
  // > WhirlpoolApiClient.REGISTER_INPUT_POLLING_FREQUENCY_MS
  CONFIRM_INPUT(60000), // abort CONFIRM_INPUT if no response from coordinator after 1min
  REGISTER_OUTPUT(60000), // mix fail after 60s min on REGISTER_OUTPUT
  REVEAL_OUTPUT(50000), // mix fail after 50s on REVEAL_OUTPUT
  SIGNING(50000), // mix fail after 50s on SIGNING
  SUCCESS(null),
  FAIL(null);

  private Integer timeoutMs;

  MixStatus(Integer timeoutMs) {
    this.timeoutMs = timeoutMs;
  }

  public Integer getTimeoutMs() {
    return timeoutMs;
  }
}
