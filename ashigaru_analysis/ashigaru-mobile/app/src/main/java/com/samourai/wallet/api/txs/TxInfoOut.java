package com.samourai.wallet.api.txs;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;

@JsonIgnoreProperties(ignoreUnknown = true)
@JsonInclude(JsonInclude.Include.NON_NULL)
public class TxInfoOut {

    private Integer n;
    private Long value;
    private String addr;
    private String pubkey;
    private TxInfoXPub xpub;

    public Integer getN() {
        return n;
    }

    public void setN(Integer n) {
        this.n = n;
    }

    public Long getValue() {
        return value;
    }

    public void setValue(Long value) {
        this.value = value;
    }

    public String getAddr() {
        return addr;
    }

    public void setAddr(String addr) {
        this.addr = addr;
    }

    public String getPubkey() {
        return pubkey;
    }

    public void setPubkey(String pubkey) {
        this.pubkey = pubkey;
    }

    public TxInfoXPub getXpub() {
        return xpub;
    }

    public void setXpub(TxInfoXPub xpub) {
        this.xpub = xpub;
    }
}
