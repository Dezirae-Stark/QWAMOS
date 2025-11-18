# Post-Quantum Mesh Transport Protocol

## Connection Establishment

### Handshake Protocol

```
Device A                           Device B
   |                                   |
   |--- Hello (Device ID, Kyber PK) -->|
   |                                   |
   |<-- Response (Device ID, Kyber PK)-|
   |                                   |
   |-- Kyber Encaps(shared_secret) --->|
   |                                   |
   |<-- Kyber Encaps(shared_secret) ---|
   |                                   |
[Derive ChaCha20 key from shared secrets]
   |                                   |
   |<== Encrypted Messages (ChaCha20)==|
```

### Key Rotation

Every 1 hour or 1 GB of data transferred:
1. Perform new Kyber key exchange
2. Derive fresh ChaCha20 key
3. Switch to new key atomically
4. Securely erase old key

## Message Format

```
[4 bytes: Message length]
[12 bytes: ChaCha20 nonce]
[N bytes: Encrypted payload]
[16 bytes: Poly1305 tag]
```

**Encryption**: ChaCha20-Poly1305 AEAD
**Nonce**: Incremental counter + random salt
**Maximum message size**: 16 MB

## Reliability and Ordering

- **Reliability**: TCP-like acknowledgments and retransmission
- **Ordering**: Sequence numbers for in-order delivery
- **Congestion Control**: Token bucket rate limiting

---

**Last Updated:** 2025-11-17
