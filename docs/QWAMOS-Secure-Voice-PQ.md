# QWAMOS Secure Voice: Post-Quantum Encrypted VoIP

## Overview

QWAMOS Secure Voice is a post-quantum secure voice communication system built on Simlar (a Liblinphone-based VoIP client) specifically hardened for the QWAMOS mobile operating system. It provides end-to-end encrypted voice calls using post-quantum hybrid cryptography to protect against both current and future quantum computing threats.

**Key Features:**
- **Post-Quantum ZRTP**: Hybrid key agreement using Kyber lattice-based cryptography
- **Zero Classical Fallback**: Enforces PQ-only policy - classical-only calls are automatically rejected
- **Gateway Routing**: All VoIP traffic routed through QWAMOS secure gateway (Tor/I2P/DNSCrypt)
- **Carrier Call Warnings**: Optional warnings/blocks on insecure mobile carrier calls
- **Open Source**: GPL-licensed, auditable cryptographic implementation

---

## Cryptographic Architecture

### Post-Quantum ZRTP Key Agreement

QWAMOS Secure Voice uses ZRTP (Z Real-Time Transport Protocol) with post-quantum hybrid key agreement suites:

#### Supported PQ Key Agreement Suites (Priority Order)

1. **K448Kyb1024** *(Highest Security)*
   - Elliptic Curve: Goldilocks Curve448 (classical component)
   - PQ Component: CRYSTALS-Kyber-1024 (NIST PQC standard)
   - Security Level: ~256-bit classical + ~256-bit PQ
   - Use Case: Maximum security for high-value communications

2. **K255Kyb512** *(Balanced)*
   - Elliptic Curve: Curve25519 (Bernstein curve, classical component)
   - PQ Component: CRYSTALS-Kyber-512 (NIST PQC standard)
   - Security Level: ~128-bit classical + ~128-bit PQ
   - Use Case: Standard secure communications with good performance

#### Blocked/Removed Suites (QWAMOS Policy)

The following classical-only suites are **explicitly disabled** and will cause call rejection:
- X255 (pure Curve25519, no PQ)
- X448 (pure Curve448, no PQ)
- DH2K, DH3K (pure Diffie-Hellman, no PQ)
- Ec25, Ec38, Ec52 (pure elliptic curve, no PQ)

**Rationale:** These suites offer no protection against quantum adversaries. QWAMOS policy mandates PQ-hybrid minimum.

### SRTP Media Encryption

After ZRTP key agreement establishes shared secrets, voice media is encrypted using **SRTP** (Secure Real-time Transport Protocol):

- **Cipher Suites**: AES-256-CM with HMAC-SHA1
- **Key Derivation**: From ZRTP-derived master secret
- **Forward Secrecy**: Each call uses unique ephemeral keys

---

## Threat Model

### Protected Against

1. **Harvest Now, Decrypt Later (HNDL) Attacks**
   - Adversary records encrypted VoIP traffic today
   - Adversary waits for large-scale quantum computer (10-20 years)
   - With classical crypto: Adversary can decrypt historical calls
   - **With QWAMOS PQ**: Kyber resists quantum attacks, traffic remains secure

2. **Active Man-in-the-Middle (MitM)**
   - ZRTP SAS (Short Authentication String) verification
   - Users verbally compare 4-character SAS to detect MitM
   - If SAS matches, authentication is cryptographically sound

3. **Network-Level Surveillance**
   - All signaling and media routed through QWAMOS gateway
   - SIP over TLS, ZRTP for media
   - Traffic anonymized via Tor/I2P (if configured)

### Not Protected Against

1. **Endpoint Compromise**
   - Malware on either device can capture plaintext audio
   - QWAMOS uses VM isolation to mitigate but doesn't eliminate this risk

2. **Baseband/Carrier Network (GSM/VoLTE)**
   - Standard mobile carrier calls use SS7/VoLTE
   - These are **not end-to-end encrypted**
   - Carrier and government can intercept
   - **QWAMOS mitigation**: Carrier call warnings encourage secure VoIP instead

3. **SIP Server Metadata**
   - SIP server sees call metadata (who called whom, when, duration)
   - Does NOT see call content (encrypted by ZRTP/SRTP)
   - **QWAMOS mitigation**: Use Tor/I2P to hide IP addresses from SIP server

4. **Physical Access / Side Channels**
   - Acoustic leakage, compromised hardware, physical observation
   - Outside scope of software-only security

---

## Network Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    QWAMOS Secure Voice                      │
│                  (Simlar PQ Fork - Dom0)                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ SIP/TLS Signaling + ZRTP/SRTP Media
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              QWAMOS Network Gateway (NetVM)                 │
│     - InviZible Pro (Tor/I2P/DNSCrypt orchestration)        │
│     - Firewall rules (all traffic forced through gateway)   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Anonymized/Encrypted Transport
                       │
                       ▼
              ┌────────────────────┐
              │   Tor Exit Node    │  (if Tor mode)
              │   OR I2P Outproxy  │  (if I2P mode)
              └─────────┬──────────┘
                        │
                        ▼
              ┌────────────────────┐
              │  SIP Server (TLS)  │
              │   (simlar.org or   │
              │   custom server)   │
              └─────────┬──────────┘
                        │
                        │ SIP Signaling + ZRTP Handshake
                        │
                        ▼
              ┌────────────────────┐
              │  Remote Endpoint   │
              │ (QWAMOS or PQ-     │
              │  compatible client)│
              └────────────────────┘
```

**Call Flow:**
1. **Registration**: QWAMOS Secure Voice registers with SIP server over TLS (via gateway)
2. **Call Initiation**: User dials; SIP INVITE sent through gateway
3. **ZRTP Handshake**: PQ key agreement (K448Kyb1024 or K255Kyb512)
4. **SAS Verification**: Users compare 4-character code (e.g., "golf-lima-oscar")
5. **Media Stream**: SRTP-encrypted audio with PQ-derived keys
6. **Policy Enforcement**: If remote doesn't support PQ, call is auto-terminated

---

## Usage

### Making a Secure Call

1. **Launch QWAMOS Secure Voice**
   - From main QWAMOS UI: "Secure Voice (PQ-Encrypted)" app
   - Or directly from app drawer (icon: green shield + phone)

2. **Enter Simlar ID or Phone Number**
   - Simlar IDs are like phone numbers (e.g., `*1234567890`)
   - Contacts can be imported from QWAMOS global contacts

3. **Initiate Call**
   - Call connects, ZRTP handshake begins automatically
   - You'll see "Connecting..." then "Negotiating Encryption..."

4. **Verify Security**
   - **SAS Verification** (CRITICAL for MitM detection):
     - After ~2-3 seconds, a 4-word code appears (e.g., "golf-lima-oscar-tango")
     - **Verbally ask** the other person for their SAS
     - If codes match: Click "Verified" → Green shield icon
     - If codes differ: HANG UP IMMEDIATELY (MitM attack)

   - **PQ Indicator**:
     - 🔒 **Green "PQ-Secured (Kyber-1024)"** = Maximum security
     - 🔒 **Yellow-green "PQ-Secured (Kyber-512)"** = Standard security
     - 🚫 **Red "Classical Only - BLOCKED"** = Call auto-terminated (policy violation)

5. **During Call**
   - Green shield = PQ secure + SAS verified
   - Yellow shield = PQ secure but SAS not verified yet
   - Audio quality, network stats shown in UI

### Receiving a Secure Call

1. **Incoming Call Notification**
   - Shows caller ID (if registered contact)
   - Ringtone plays (customizable)

2. **Answer Call**
   - Swipe/click to answer
   - ZRTP handshake happens automatically

3. **Verify SAS**
   - Same as outgoing: compare 4-word code with caller
   - Mark as verified if match

### Interpreting Security Icons

| Icon | Meaning | Action |
|------|---------|--------|
| 🔒 **PQ-Secured (Kyber-1024)** | Highest security, PQ hybrid active | ✅ Safe to talk |
| 🔒 **PQ-Secured (Kyber-512)** | Standard security, PQ hybrid active | ✅ Safe to talk |
| 🔓 **SAS Not Verified** | Encryption active but not authenticated | ⚠️ Verify SAS now |
| 🚫 **Classical Only** | No PQ support, call blocked | ❌ Call terminated |
| ⚠️ **Insecure** | No encryption | ❌ Never happens (enforcement) |

---

## Inbound Carrier Call Warning System

QWAMOS can optionally warn or block inbound calls from the mobile carrier network (GSM/VoLTE), which are **not end-to-end encrypted**.

### How It Works

1. **Detection**: QWAMOS monitors `TelephonyManager` for `CALL_STATE_RINGING`
2. **Warning Display**: High-priority notification or dialog:
   ```
   ⚠️ INSECURE CARRIER CALL DETECTED

   Caller: +1-555-123-4567

   This call uses the mobile carrier network and is NOT
   end-to-end encrypted. Your carrier and government agencies
   can intercept this call.

   Options:
   [Accept Insecure Call]  [Deny & Use Secure VoIP]
   ```
3. **User Choice**:
   - **Accept Insecure Call**: Normal carrier call proceeds
   - **Deny & Use Secure VoIP**:
     - Carrier call is rejected (if API permits)
     - QWAMOS Secure Voice launches with caller info
     - User can initiate encrypted callback

### Configuration

Settings → Security → Secure Voice Policy:

- ☐ **Warn on inbound carrier calls** (default: ON in secure profile)
- ☐ **Auto-deny carrier calls in secure profile** (default: OFF)
- ☐ **Show VoIP switch option** (default: ON)

**Profiles:**
- **Standard Profile**: Warning shown, user chooses
- **Secure Profile**: Warning shown, recommended deny
- **Paranoid Profile**: Auto-deny, force secure VoIP only

---

## Technical Implementation Details

### Liblinphone Version & PQ Build

- **Liblinphone SDK Version**: 5.4.24 (or later with PQ support)
- **PQ Enablement**: Built with `-DENABLE_PQCRYPTO=ON` CMake flag
- **Binary Distribution**: QWAMOS uses custom-built Liblinphone AAR with PQ enabled
  - Standard Maven artifacts **do not** include PQ support
  - Build from source: `git clone https://github.com/BelledonneCommunications/liblinphone.git`

### Runtime PQ Verification

QWAMOS uses `QwamosPqSecurityHelper` class to verify PQ usage:

```java
// Check if call is PQ secured
boolean isPqSecured = QwamosPqSecurityHelper.isCallPqSecured(call);

// Get detailed security level
SecurityLevel level = QwamosPqSecurityHelper.getCallSecurityLevel(call);
// Returns: PQ_HYBRID_STRONG, PQ_HYBRID_STANDARD, CLASSICAL_ONLY, etc.

// Enforce policy (auto-terminate non-PQ calls)
boolean allowed = QwamosPqSecurityHelper.enforceQwamosPqPolicy(call);
if (!allowed) {
    terminateCall();
    showError(QwamosPqSecurityHelper.getPqPolicyViolationMessage());
}
```

### Configuration Files

**linphonerc** (ZRTP config):
```ini
[sip]
media_encryption=zrtp
media_encryption_mandatory=1
zrtp_key_agreement_suites=K448Kyb1024,K255Kyb512
```

**BuildConfig Flags**:
```gradle
buildConfigField("boolean", "QWAMOS_PQ_ONLY", "true")
buildConfigField("boolean", "ENFORCE_PQ_VOIP_ONLY", "true")
```

### Logging & Debugging

All QWAMOS Secure Voice operations are logged with tag `QWAMOS_PQ_VOICE`:

```bash
adb logcat | grep QWAMOS
```

Example log output:
```
QWAMOS: ZRTP Post-Quantum encryption available: true
QWAMOS: PQ-only ZRTP policy enforced - classical key agreement disabled
QWAMOS: Call meets PQ security requirements
QWAMOS: ZRTP SAS authentication token: golf-lima-oscar-tango
```

---

## Comparison with Standard VoIP

| Feature | Standard VoIP (Simlar/Linphone) | QWAMOS Secure Voice |
|---------|----------------------------------|---------------------|
| Encryption | ZRTP (classical ECDH) | ZRTP-PQ (Kyber hybrid) |
| Quantum Resistant | ❌ No | ✅ Yes |
| Policy Enforcement | Optional | Mandatory (PQ-only) |
| Network Routing | Direct clearnet | Via Tor/I2P gateway |
| Carrier Call Warning | ❌ No | ✅ Yes (optional) |
| Classical Fallback | ✅ Allowed | ❌ Blocked |
| SAS Verification | Optional | Recommended |
| Package Name | org.simlar | org.qwamos.securevoice |

---

## FAQs

### Can I call non-QWAMOS users?

**Partially.** The remote endpoint must support ZRTP with post-quantum key agreement (Kyber). This includes:
- Other QWAMOS Secure Voice users ✅
- Liblinphone 5.x+ built with `-DENABLE_PQCRYPTO=ON` ✅
- Standard Linphone/Simlar (classical only) ❌ (call will be blocked)
- Regular phone calls (PSTN/VoLTE) ❌ (not encrypted at all)

**Recommendation**: Invite contacts to QWAMOS or a PQ-compatible client.

### What if the other person doesn't have PQ support?

The call will be **automatically terminated** with message:
```
Remote endpoint does not support post-quantum secure voice.
Call cancelled per QWAMOS security policy.
Both endpoints must use QWAMOS Secure Voice or PQ-enabled clients.
```

You can disable this enforcement by setting `ENFORCE_PQ_VOIP_ONLY=false` in build config (not recommended).

### How do I know if PQ is actually being used?

1. **UI Indicator**: Green shield with "PQ-Secured (Kyber-1024)" or "PQ-Secured (Kyber-512)"
2. **Logs**: Check `adb logcat | grep QWAMOS` for confirmation
3. **Call Stats**: In-call menu → Security Details shows ZRTP key agreement algorithm

### Can the carrier/government still intercept?

**VoIP over QWAMOS gateway**:
- **Call content**: ❌ No (end-to-end encrypted with PQ)
- **Metadata**: ⚠️ Partially (SIP server sees caller IDs, use Tor/I2P to hide IPs)
- **Traffic analysis**: ⚠️ Possible (timing, packet sizes) but content is safe

**Carrier voice calls (GSM/VoLTE)**:
- **Call content**: ✅ Yes (carrier has plaintext access)
- **Metadata**: ✅ Yes (carrier knows everything)
- **QWAMOS mitigation**: Warnings + option to use secure VoIP instead

### What about group calls / conference?

QWAMOS Secure Voice currently supports **1-to-1 calls only**. Group calls with PQ ZRTP are theoretically possible but not yet implemented in Liblinphone. Future enhancement planned.

### Performance impact of PQ crypto?

Kyber is highly efficient:
- **Key generation**: ~0.5ms
- **Encapsulation**: ~0.6ms
- **Decapsulation**: ~0.7ms
- **Total handshake overhead**: < 50ms additional vs classical ECDH

**Impact**: Negligible for users. Call setup may be 50-100ms slower, imperceptible in practice.

---

## Build Instructions

### Building PQ-Enabled Liblinphone

1. **Clone Liblinphone**:
   ```bash
   git clone https://github.com/BelledonneCommunications/liblinphone.git
   cd liblinphone
   ```

2. **Enable PQ in CMake**:
   ```bash
   mkdir build && cd build
   cmake .. -DENABLE_PQCRYPTO=ON -DCMAKE_BUILD_TYPE=Release
   make -j$(nproc)
   ```

3. **Build Android AAR**:
   ```bash
   cd android
   ./prepare.py -DENABLE_PQCRYPTO=ON
   ./gradlew assembleRelease
   ```

4. **Integrate into Simlar**:
   - Copy `linphone-sdk-android-release.aar` to `simlar-for-QWAMOS/app/libs/linphone-sdk/5.4.24/`
   - Gradle will use local AAR instead of Maven artifact

### Building QWAMOS Secure Voice (Simlar Fork)

```bash
cd simlar-for-QWAMOS
./gradlew assembleRelease
# Output: app/build/outputs/apk/alwaysOnline/release/app-alwaysOnline-release.apk
```

Install:
```bash
adb install app/build/outputs/apk/alwaysOnline/release/app-alwaysOnline-release.apk
```

---

## Security Audits & Compliance

- **Cryptographic Libraries**: Liblinphone (GPL), bctoolbox, bzrtp
- **PQ Algorithm**: CRYSTALS-Kyber (NIST PQC Standardized, 2024)
- **Code Audit**: QWAMOS-specific changes are open-source (see GitHub)
- **Compliance**: GPL v2/v3 (same as upstream Simlar/Liblinphone)

**Third-Party Audit Recommendations**:
1. Verify ZRTP handshake uses Kyber (Wireshark/tcpdump)
2. Review QwamosPqSecurityHelper enforcement logic
3. Test policy bypass attempts (should fail)

---

## Troubleshooting

### Call fails immediately with "Classical Only - BLOCKED"

**Cause**: Remote endpoint doesn't support PQ ZRTP.

**Solution**:
- Ensure remote uses QWAMOS Secure Voice or PQ-enabled Liblinphone
- Check remote's Liblinphone version: Settings → About → Version
- Verify remote built with `ENABLE_PQCRYPTO=ON`

### "Post-Quantum encryption NOT available" warning

**Cause**: Liblinphone AAR doesn't have PQ support compiled in.

**Solution**:
- Rebuild Liblinphone with `-DENABLE_PQCRYPTO=ON` (see Build Instructions)
- Ensure using custom AAR, not standard Maven artifact

### Carrier call warning doesn't appear

**Cause**: Permissions not granted or feature disabled.

**Solution**:
- Grant `READ_PHONE_STATE` permission
- Enable in Settings → Security → Secure Voice Policy → "Warn on inbound carrier calls"

### SAS doesn't match between endpoints

**Cause**: Potential MitM attack OR network/timing issue.

**Solution**:
- HANG UP IMMEDIATELY
- Retry call (if still mismatch, investigate network path)
- Verify both endpoints using latest QWAMOS Secure Voice

---

## License

QWAMOS Secure Voice is based on Simlar, which is licensed under **GPLv2+**.

Dependencies:
- **Liblinphone**: GPLv3
- **bzrtp (ZRTP implementation)**: GPLv3
- **CRYSTALS-Kyber**: Public domain (NIST PQC)

QWAMOS modifications and additions: GPLv3

---

## References

- [Liblinphone PQ Documentation](https://gitlab.linphone.org/BC/public/liblinphone/-/wikis/home)
- [ZRTP RFC 6189](https://www.rfc-editor.org/rfc/rfc6189.html)
- [CRYSTALS-Kyber (NIST PQC)](https://pq-crystals.org/kyber/)
- [QWAMOS Architecture Docs](./ARCHITECTURE.md)
- [Simlar Project](https://www.simlar.org/)

---

**For questions, issues, or security reports:**
- GitHub Issues: https://github.com/Dezirae-Stark/QWAMOS/issues
- Security: qwamos-security@[yourdomain] (PGP key on website)

**Last Updated**: 2025-11-17
**QWAMOS Version**: 1.0-alpha
**Simlar Fork Version**: feature/qwamos-pq-secure-voice
