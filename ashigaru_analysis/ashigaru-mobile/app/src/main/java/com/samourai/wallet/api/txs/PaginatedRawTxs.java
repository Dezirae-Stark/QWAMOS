package com.samourai.wallet.api.txs;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;

import org.apache.commons.collections4.CollectionUtils;

import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
@JsonInclude(JsonInclude.Include.NON_NULL)
public class PaginatedRawTxs {

    @JsonProperty("n_tx")
    private int totalTx;

    private int page;

    @JsonProperty("n_tx_page")
    private int pageSize;
    private List<TxInfo> txs;

    public int getTotalTx() {
        return totalTx;
    }

    public void setTotalTx(int totalTx) {
        this.totalTx = totalTx;
    }

    public int getPage() {
        return page;
    }

    public void setPage(int page) {
        this.page = page;
    }

    public int getPageSize() {
        return pageSize;
    }

    public void setPageSize(int pageSize) {
        this.pageSize = pageSize;
    }

    public List<TxInfo> getTxs() {
        return txs;
    }

    public void setTxs(List<TxInfo> txs) {
        this.txs = txs;
    }

    public boolean shouldBeLastPage() {
        return CollectionUtils.size(txs) < pageSize;
    }
}
