package com.samourai.wallet.sync;

public enum EnumSyncTaskStatus {
    IN_PROGRESS,
    LOCAL_IN_PROGRESS,
    IN_PROGRESS_LONG,
    LOCAL_IN_PROGRESS_LONG,
    SUCCEEDED,
    FAILED,
    SKIPPED,
    ;

    public static EnumSyncTaskStatus provideRandomlyOneStatus() {
        final int index = (int) (Math.random() * EnumSyncTaskStatus.values().length);
        return EnumSyncTaskStatus.values()[index];
    }

    public boolean isInProgress() {
        return this == IN_PROGRESS || this == LOCAL_IN_PROGRESS ||
                this == IN_PROGRESS_LONG || this == LOCAL_IN_PROGRESS_LONG;
    }

    public boolean isLocalInProgress() {
        return this == LOCAL_IN_PROGRESS || this == LOCAL_IN_PROGRESS_LONG;
    }
}
