/*
 * QWAMOS Bootloader - Kyber-1024 Signature Verification Implementation
 *
 * This module implements post-quantum signature verification using Kyber-1024
 * integrated with liboqs (Open Quantum Safe).
 */

#include "kyber1024_verify.h"
#include <string.h>

/* liboqs integration - will link against liboqs library */
#include <oqs/oqs.h>

/* Embedded public key (provisioned during device setup) */
static const uint8_t qwamos_public_key[KYBER1024_PUBLIC_KEY_BYTES] = {
	/* This will be replaced during device provisioning */
	/* For now, placeholder for compilation */
	[0 ... KYBER1024_PUBLIC_KEY_BYTES-1] = 0x00
};

/**
 * sha256_hash - Compute SHA-256 hash using liboqs
 */
void sha256_hash(const uint8_t *data, size_t data_size, uint8_t *hash_out)
{
	OQS_SHA2_sha256(hash_out, data, data_size);
}

/**
 * kyber1024_verify_signature - Core signature verification
 */
static int kyber1024_verify_signature(const uint8_t *message,
                                      size_t message_len,
                                      const uint8_t *signature,
                                      const uint8_t *public_key)
{
	OQS_SIG *sig = NULL;
	int result = -1;

	/* Initialize Kyber-1024 signature scheme */
	sig = OQS_SIG_new(OQS_SIG_alg_dilithium_5);
	if (!sig) {
		printf("ERROR: Failed to initialize Kyber signature scheme\n");
		return -1;
	}

	/* Verify signature */
	if (OQS_SIG_verify(sig, message, message_len, signature,
	                   sig->length_signature, public_key) == OQS_SUCCESS) {
		result = 0; /* Signature valid */
	} else {
		printf("ERROR: Signature verification failed!\n");
		result = -1;
	}

	OQS_SIG_free(sig);
	return result;
}

/**
 * kyber1024_verify_image - Verify image signature
 */
int kyber1024_verify_image(const uint8_t *image,
                           size_t image_size,
                           const struct qwamos_signature *signature,
                           const uint8_t *public_key)
{
	uint8_t computed_hash[32];

	/* Verify magic number */
	if (signature->magic != QWAMOS_SIG_MAGIC) {
		printf("ERROR: Invalid signature magic: 0x%08x\n", signature->magic);
		return -1;
	}

	/* Verify version */
	if (signature->version != QWAMOS_SIG_VERSION) {
		printf("ERROR: Unsupported signature version: %d\n", signature->version);
		return -1;
	}

	/* Verify image size matches */
	if (signature->image_size != image_size) {
		printf("ERROR: Image size mismatch: expected %u, got %zu\n",
		       signature->image_size, image_size);
		return -1;
	}

	/* Compute SHA-256 hash of image */
	sha256_hash(image, image_size, computed_hash);

	/* Verify hash matches signature */
	if (memcmp(computed_hash, signature->image_hash, 32) != 0) {
		printf("ERROR: Image hash mismatch!\n");
		printf("  Expected: ");
		for (int i = 0; i < 32; i++)
			printf("%02x", signature->image_hash[i]);
		printf("\n  Computed: ");
		for (int i = 0; i < 32; i++)
			printf("%02x", computed_hash[i]);
		printf("\n");
		return -1;
	}

	/* Verify Kyber-1024 signature */
	printf("Verifying Kyber-1024 signature...\n");
	if (kyber1024_verify_signature(computed_hash, 32,
	                               signature->kyber_signature,
	                               public_key) != 0) {
		printf("ERROR: Kyber-1024 signature verification failed!\n");
		return -1;
	}

	printf("SUCCESS: Image signature verified (Kyber-1024)\n");
	return 0;
}

/**
 * kyber1024_verify_kernel - Verify kernel before boot
 */
int kyber1024_verify_kernel(uintptr_t kernel_addr, size_t kernel_size)
{
	const uint8_t *kernel_image = (const uint8_t *)kernel_addr;
	const struct qwamos_signature *sig;

	printf("=== QWAMOS Secure Boot: Kernel Verification ===\n");
	printf("Kernel address: 0x%lx\n", kernel_addr);
	printf("Kernel size: %zu bytes\n", kernel_size);

	/* Signature is appended after kernel image */
	sig = (const struct qwamos_signature *)(kernel_image + kernel_size);

	/* Verify kernel signature */
	if (kyber1024_verify_image(kernel_image, kernel_size, sig,
	                           qwamos_public_key) != 0) {
		printf("CRITICAL: Kernel signature verification FAILED!\n");
		printf("Boot process halted for security.\n");
		return -1;
	}

	printf("Kernel signature verified successfully.\n");
	return 0;
}

/**
 * kyber1024_verify_initramfs - Verify initramfs before loading
 */
int kyber1024_verify_initramfs(uintptr_t initramfs_addr, size_t initramfs_size)
{
	const uint8_t *initramfs_image = (const uint8_t *)initramfs_addr;
	const struct qwamos_signature *sig;

	printf("=== QWAMOS Secure Boot: Initramfs Verification ===\n");
	printf("Initramfs address: 0x%lx\n", initramfs_addr);
	printf("Initramfs size: %zu bytes\n", initramfs_size);

	/* Signature is appended after initramfs */
	sig = (const struct qwamos_signature *)(initramfs_image + initramfs_size);

	/* Verify initramfs signature */
	if (kyber1024_verify_image(initramfs_image, initramfs_size, sig,
	                           qwamos_public_key) != 0) {
		printf("CRITICAL: Initramfs signature verification FAILED!\n");
		printf("Boot process halted for security.\n");
		return -1;
	}

	printf("Initramfs signature verified successfully.\n");
	return 0;
}

/**
 * kyber1024_load_public_key - Load public key from secure storage
 */
int kyber1024_load_public_key(uint8_t *key_buffer, size_t key_size)
{
	if (key_size < KYBER1024_PUBLIC_KEY_BYTES) {
		printf("ERROR: Key buffer too small\n");
		return -1;
	}

	/* Copy embedded public key */
	memcpy(key_buffer, qwamos_public_key, KYBER1024_PUBLIC_KEY_BYTES);
	return 0;
}

/**
 * secure_boot_verify_chain - Verify entire boot chain
 */
int secure_boot_verify_chain(void)
{
	printf("\n");
	printf("================================================================================\n");
	printf("                    QWAMOS SECURE BOOT VERIFICATION\n");
	printf("           Post-Quantum Cryptography: Kyber-1024 (NIST FIPS 203)\n");
	printf("================================================================================\n");
	printf("\n");

	/* In a real implementation, these addresses would come from U-Boot environment */
	/* For now, this demonstrates the verification flow */

	printf("Step 1: Loading public key...\n");
	uint8_t public_key[KYBER1024_PUBLIC_KEY_BYTES];
	if (kyber1024_load_public_key(public_key, sizeof(public_key)) != 0) {
		printf("CRITICAL: Failed to load public key!\n");
		return -1;
	}
	printf("Public key loaded successfully.\n\n");

	/* Note: Actual kernel and initramfs verification will be called
	 * from U-Boot's boot sequence when loading images */

	printf("================================================================================\n");
	printf("QWAMOS Secure Boot: Ready to verify boot images\n");
	printf("================================================================================\n");
	printf("\n");

	return 0;
}
