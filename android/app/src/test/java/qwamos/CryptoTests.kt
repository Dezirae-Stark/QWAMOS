package qwamos

import org.junit.Test
import org.junit.Assert.*
import org.junit.Before

/**
 * QWAMOS Cryptography Unit Tests (Kotlin)
 * Tests for post-quantum cryptography in Android
 */
class CryptoTests {

    private lateinit var mockKyber: MockKyberKeygen
    private lateinit var mockChaCha: MockChaCha20Poly1305

    @Before
    fun setUp() {
        mockKyber = MockKyberKeygen()
        mockChaCha = MockChaCha20Poly1305()
    }

    @Test
    fun testKyberKeygeneration() {
        val (publicKey, privateKey) = mockKyber.generateKeypair()

        assertNotNull(publicKey)
        assertNotNull(privateKey)
        assertTrue(publicKey.isNotEmpty())
        assertTrue(privateKey.isNotEmpty())
    }

    @Test
    fun testKyberPublicKeySize() {
        val (publicKey, _) = mockKyber.generateKeypair()

        // Kyber-1024 public key should be 1568 bytes
        assertEquals(1568, publicKey.size)
    }

    @Test
    fun testKyberPrivateKeySize() {
        val (_, privateKey) = mockKyber.generateKeypair()

        // Kyber-1024 private key should be 3168 bytes
        assertEquals(3168, privateKey.size)
    }

    @Test
    fun testChaCha20Poly1305Encryption() {
        val plaintext = "Hello, QWAMOS!".toByteArray()
        val key = ByteArray(32) { it.toByte() }
        val nonce = ByteArray(12) { it.toByte() }

        val (ciphertext, tag) = mockChaCha.encrypt(plaintext, key, nonce)

        assertNotNull(ciphertext)
        assertNotNull(tag)
        assertEquals(16, tag.size)
    }

    @Test
    fun testChaCha20Poly1305Decryption() {
        val plaintext = "Test message".toByteArray()
        val key = ByteArray(32) { it.toByte() }
        val nonce = ByteArray(12) { it.toByte() }

        val (ciphertext, tag) = mockChaCha.encrypt(plaintext, key, nonce)
        val decrypted = mockChaCha.decrypt(ciphertext, tag, key, nonce)

        assertArrayEquals(plaintext, decrypted)
    }

    @Test(expected = IllegalArgumentException::class)
    fun testChaCha20InvalidKeySize() {
        val plaintext = "Test".toByteArray()
        val invalidKey = ByteArray(16) { it.toByte() } // Wrong size
        val nonce = ByteArray(12) { it.toByte() }

        mockChaCha.encrypt(plaintext, invalidKey, nonce)
    }

    @Test(expected = IllegalArgumentException::class)
    fun testChaCha20InvalidNonceSize() {
        val plaintext = "Test".toByteArray()
        val key = ByteArray(32) { it.toByte() }
        val invalidNonce = ByteArray(8) { it.toByte() } // Wrong size

        mockChaCha.encrypt(plaintext, key, invalidNonce)
    }
}

/**
 * Mock Kyber-1024 key generation
 */
class MockKyberKeygen {
    private val publicKeySize = 1568
    private val privateKeySize = 3168

    fun generateKeypair(): Pair<ByteArray, ByteArray> {
        val publicKey = ByteArray(publicKeySize) { it.toByte() }
        val privateKey = ByteArray(privateKeySize) { it.toByte() }
        return Pair(publicKey, privateKey)
    }
}

/**
 * Mock ChaCha20-Poly1305 AEAD cipher
 */
class MockChaCha20Poly1305 {
    private val tagSize = 16

    fun encrypt(plaintext: ByteArray, key: ByteArray, nonce: ByteArray): Pair<ByteArray, ByteArray> {
        if (key.size != 32) {
            throw IllegalArgumentException("Key must be 32 bytes")
        }
        if (nonce.size != 12) {
            throw IllegalArgumentException("Nonce must be 12 bytes")
        }

        // Mock encryption - simple XOR with key
        val ciphertext = ByteArray(plaintext.size) { i ->
            (plaintext[i].toInt() xor key[i % key.size].toInt()).toByte()
        }

        // Mock tag
        val tag = ByteArray(tagSize) { i ->
            (key[i % key.size].toInt() xor nonce[i % nonce.size].toInt()).toByte()
        }

        return Pair(ciphertext, tag)
    }

    fun decrypt(ciphertext: ByteArray, tag: ByteArray, key: ByteArray, nonce: ByteArray): ByteArray {
        if (key.size != 32) {
            throw IllegalArgumentException("Key must be 32 bytes")
        }
        if (nonce.size != 12) {
            throw IllegalArgumentException("Nonce must be 12 bytes")
        }

        // Verify tag (mock verification)
        val expectedTag = ByteArray(tagSize) { i ->
            (key[i % key.size].toInt() xor nonce[i % nonce.size].toInt()).toByte()
        }

        if (!tag.contentEquals(expectedTag)) {
            throw SecurityException("Authentication verification failed")
        }

        // Mock decryption - XOR with key
        return ByteArray(ciphertext.size) { i ->
            (ciphertext[i].toInt() xor key[i % key.size].toInt()).toByte()
        }
    }
}
