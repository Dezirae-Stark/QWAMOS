package com.samourai.whirlpool.protocol.soroban.payload.tx0;

import com.samourai.soroban.client.AbstractSorobanPayloadable;

public class Tx0DataResponse extends AbstractSorobanPayloadable {
  public Tx0Data[] tx0Datas;

  public Tx0DataResponse() {}

  public Tx0DataResponse(Tx0Data[] tx0Datas) {
    this.tx0Datas = tx0Datas;
  }

  public static class Tx0Data {
    public String poolId;
    public String feePaymentCode;
    public long feeValue;
    public long feeChange;
    public int feeDiscountPercent;
    public String message;
    public String
        feePayload64; // encodeBytes(encodeFeePayload(feeIndex, scodePayload, partnerPayload))
    public String feePayloadCascading64;
    public String feeAddress;
    public String feeOutputSignature; // signature of serialized fee output (feeAddress + feeValue)

    public Tx0Data() {}

    public Tx0Data(
        String poolId,
        String feePaymentCode,
        long feeValue,
        long feeChange,
        int feeDiscountPercent,
        String message,
        String feePayload64,
        String feePayloadCascading64,
        String feeAddress,
        String feeOutputSignature) {
      this.poolId = poolId;
      this.feePaymentCode = feePaymentCode;
      this.feeValue = feeValue;
      this.feeChange = feeChange;
      this.feeDiscountPercent = feeDiscountPercent;
      this.message = message;
      this.feePayload64 = feePayload64;
      this.feePayloadCascading64 = feePayloadCascading64;
      this.feeAddress = feeAddress;
      this.feeOutputSignature = feeOutputSignature;
    }
  }
}
