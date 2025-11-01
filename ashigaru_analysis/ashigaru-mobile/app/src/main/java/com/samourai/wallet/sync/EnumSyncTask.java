package com.samourai.wallet.sync;

public enum EnumSyncTask {

    DOJO_CONNECTED("Dojo connected"),
    SYNC_PUB_KEYS("Extended public keys"),
    SYNC_PCODES("Incoming BIP47 connections"),
    PAYNYM("PayNym"),
    PAYNYM_CONTACT("PayNym contacts"),
    ;

    private String caption;

    EnumSyncTask(final String caption) {
        this.caption = caption;
    }

    public String getCaption() {
        return caption;
    }

    public boolean isAboutPayNym() {
        return this == PAYNYM || this == PAYNYM_CONTACT;
    }
}
