package com.samourai.wallet.api.txs;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown = true)
@JsonInclude(JsonInclude.Include.NON_NULL)
public class TxInfoInput {

    private Integer vin;
    private Long sequence;
    @JsonProperty("prev_out")
    private TxInfoInputPrevOut prevOut;

    public Integer getVin() {
        return vin;
    }

    public Long getSequence() {
        return sequence;
    }

    public TxInfoInputPrevOut getPrevOut() {
        return prevOut;
    }
}
