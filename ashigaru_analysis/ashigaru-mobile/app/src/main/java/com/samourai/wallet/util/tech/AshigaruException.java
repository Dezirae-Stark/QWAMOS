package com.samourai.wallet.util.tech;

public class AshigaruException extends Exception {
    public AshigaruException() {
    }

    public AshigaruException(String message) {
        super(message);
    }

    public AshigaruException(String message, Throwable cause) {
        super(message, cause);
    }

    public AshigaruException(Throwable cause) {
        super(cause);
    }
}
