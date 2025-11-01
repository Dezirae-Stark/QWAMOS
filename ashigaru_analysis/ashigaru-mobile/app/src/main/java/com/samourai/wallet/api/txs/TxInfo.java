package com.samourai.wallet.api.txs;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
@JsonInclude(JsonInclude.Include.NON_NULL)
public class TxInfo {

    private String hash;
    private Long time;
    private Integer version;
    private Long locktime;
    private Long result;

    private List<TxInfoInput> inputs;
    private List<TxInfoOut> out;
    @JsonProperty("block_height")
    private Long blockHeight;
    private Long balance;

    public String getHash() {
        return hash;
    }

    public void setHash(String hash) {
        this.hash = hash;
    }

    public Long getTime() {
        return time;
    }

    public void setTime(Long time) {
        this.time = time;
    }

    public Integer getVersion() {
        return version;
    }

    public void setVersion(Integer version) {
        this.version = version;
    }

    public Long getLocktime() {
        return locktime;
    }

    public void setLocktime(Long locktime) {
        this.locktime = locktime;
    }

    public Long getResult() {
        return result;
    }

    public void setResult(Long result) {
        this.result = result;
    }

    public List<TxInfoInput> getInputs() {
        return inputs;
    }

    public void setInputs(List<TxInfoInput> inputs) {
        this.inputs = inputs;
    }

    public List<TxInfoOut> getOut() {
        return out;
    }

    public void setOut(List<TxInfoOut> out) {
        this.out = out;
    }

    public Long getBlockHeight() {
        return blockHeight;
    }

    public void setBlockHeight(Long blockHeight) {
        this.blockHeight = blockHeight;
    }

    public Long getBalance() {
        return balance;
    }

    public void setBalance(Long balance) {
        this.balance = balance;
    }
}
