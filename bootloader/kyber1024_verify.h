/*
 * QWAMOS Bootloader - Kyber-1024 Signature Verification
 *
 * Post-quantum signature verification for secure boot using Kyber-1024
 * (NIST FIPS 203 - ML-KEM)
 *
 * This module provides cryptographic verification of kernel and initramfs
 * signatures to ensure only authorized code executes during boot.
 */

#ifndef __KYBER1024_VERIFY_H__
#define __KYBER1024_VERIFY_H__

#include <stdint.h>
#include <stddef.h>

/* Kyber-1024 parameter constants (NIST FIPS 203) */
#define KYBER1024_PUBLIC_KEY_BYTES    1568
#define KYBER1024_SECRET_KEY_BYTES    3168
#define KYBER1024_CIPHERTEXT_BYTES    1568
#define KYBER1024_SHARED_SECRET_BYTES 32
#define KYBER1024_SIGNATURE_BYTES     3309

/* QWAMOS boot image signature header */
struct qwamos_signature {
	uint32_t magic;                              /* Magic: 'QWAM' */
	uint32_t version;                            /* Signature format version */
	uint32_t image_size;                         /* Size of signed image */
	uint8_t  image_hash[32];                     /* SHA-256 hash of image */
	uint8_t  kyber_signature[KYBER1024_SIGNATURE_BYTES]; /* Kyber-1024 signature */
	uint8_t  reserved[64];                       /* Reserved for future use */
} __attribute__((packed));

#define QWAMOS_SIG_MAGIC 0x4D415751  /* 'QWAM' */
#define QWAMOS_SIG_VERSION 1

/**
 * kyber1024_verify_image - Verify image signature using Kyber-1024
 * @image: Pointer to image data
 * @image_size: Size of image in bytes
 * @signature: Pointer to signature structure
 * @public_key: Kyber-1024 public key (embedded in bootloader)
 *
 * Returns: 0 on success (signature valid), -1 on failure
 */
int kyber1024_verify_image(const uint8_t *image,
                           size_t image_size,
                           const struct qwamos_signature *signature,
                           const uint8_t *public_key);

/**
 * kyber1024_verify_kernel - Verify kernel image before boot
 * @kernel_addr: Address of loaded kernel image
 * @kernel_size: Size of kernel image
 *
 * Returns: 0 if verified, -1 if verification fails (blocks boot)
 */
int kyber1024_verify_kernel(uintptr_t kernel_addr, size_t kernel_size);

/**
 * kyber1024_verify_initramfs - Verify initramfs before loading
 * @initramfs_addr: Address of loaded initramfs
 * @initramfs_size: Size of initramfs
 *
 * Returns: 0 if verified, -1 if verification fails (blocks boot)
 */
int kyber1024_verify_initramfs(uintptr_t initramfs_addr, size_t initramfs_size);

/**
 * kyber1024_load_public_key - Load public key from secure storage
 * @key_buffer: Buffer to store public key
 * @key_size: Size of buffer (must be >= KYBER1024_PUBLIC_KEY_BYTES)
 *
 * Returns: 0 on success, -1 on failure
 *
 * The public key is stored in a read-only partition during device
 * provisioning and cannot be modified without re-flashing.
 */
int kyber1024_load_public_key(uint8_t *key_buffer, size_t key_size);

/**
 * sha256_hash - Compute SHA-256 hash of data
 * @data: Pointer to data
 * @data_size: Size of data in bytes
 * @hash_out: Output buffer for hash (32 bytes)
 */
void sha256_hash(const uint8_t *data, size_t data_size, uint8_t *hash_out);

/**
 * secure_boot_verify_chain - Verify entire boot chain
 *
 * This function verifies:
 * 1. Bootloader signature (self-verification)
 * 2. Kernel signature
 * 3. Initramfs signature
 * 4. Device tree blob signature (if present)
 *
 * Returns: 0 if all signatures valid, -1 otherwise (halts boot)
 */
int secure_boot_verify_chain(void);

#endif /* __KYBER1024_VERIFY_H__ */
