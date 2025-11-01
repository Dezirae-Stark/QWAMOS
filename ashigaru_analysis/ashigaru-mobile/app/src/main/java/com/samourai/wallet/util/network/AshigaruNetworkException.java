package com.samourai.wallet.util.network;

public class AshigaruNetworkException extends Exception {
    public AshigaruNetworkException() {
    }

    public AshigaruNetworkException(String message) {
        super(message);
    }

    public AshigaruNetworkException(String message, Throwable cause) {
        super(message, cause);
    }

    public AshigaruNetworkException(Throwable cause) {
        super(cause);
    }
}
