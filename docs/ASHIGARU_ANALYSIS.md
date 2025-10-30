# Ashigaru Component Analysis

**Date:** 2025-10-30
**Analyzed By:** QWAMOS Development Team

---

## Overview

Ashigaru is a privacy-focused mobile cryptocurrency wallet system, forked from Samourai Wallet after the latter's legal issues. The project includes multiple components that are highly relevant to QWAMOS development.

**Key Insight:** Ashigaru provides battle-tested implementations of Tor integration, Whirlpool CoinJoin, and privacy-focused mobile architecture that align perfectly with QWAMOS goals.

---

## Components Analyzed

### 1. Ashigaru-Mobile (8.3 MB)

**Type:** Native Android Application (Java/Kotlin + Gradle)

**Description:** Full-featured Bitcoin wallet with privacy enhancements

**Key Components:**
- `bitcoinj/` - Bitcoin protocol implementation (SPV wallet)
- `whirlpool-client/` - CoinJoin client for transaction privacy
- `whirlpool-protocol/` - Whirlpool protocol definitions
- `soroban-client-java/` - Stellar blockchain integration
- `boltzmann-java/` - Transaction entropy analysis
- `hummingbird-android/` - Cryptocurrency library
- `extlibj/` - External Java libraries
- `xmanager-protocol/` - XPUB manager protocol

**Build System:**
- Gradle 8.x
- Android SDK (likely targeting API 31-34)
- Native Android UI (likely XML layouts)

**Relevance to QWAMOS:**
- ✅ Can be integrated into AEGIS Vault as the Bitcoin wallet
- ✅ Whirlpool CoinJoin provides transaction privacy
- ✅ Battle-tested Bitcoin implementation
- ❌ Not React Native (would need UI rewrite for QWAMOS native UI)
- ⚠️ Could run in android-vm or extract core libraries for vault-vm

**Integration Strategy:**
1. **Option A:** Run full Ashigaru app inside android-vm
2. **Option B:** Extract bitcoinj + whirlpool libraries for vault-vm
3. **Option C:** Use Ashigaru backend with QWAMOS React Native frontend

**Recommended:** Option B - Extract core libraries for AEGIS Vault

---

### 2. Ashigaru-JTorProx (17 MB)

**Type:** Android Tor Proxy Library

**Description:** Tor integration for Android apps, forked from Samourai's Tor Onion Proxy Library

**Key Components:**
- `android/` - Android library module
- `android_tor_installer/` - Tor binary installation
- `java/` - Pure Java Tor controller
- `universal/` - Cross-platform Tor bindings

**Features:**
- Embedded Tor binaries for Android (ARMv7, ARM64, x86)
- SOCKS5 proxy (port 9050 default)
- Tor control port integration
- Circuit management
- Stream isolation support

**Build System:**
- Gradle
- Native Tor binaries (compiled for Android architectures)

**Relevance to QWAMOS:**
- ✅✅✅ **CRITICAL COMPONENT** for Whonix Gateway integration
- ✅ Provides Tor for android-vm without full Whonix VM
- ✅ Stream isolation aligns with QWAMOS multi-VM design
- ✅ Can be adapted for whonix-vm or native Tor on QWAMOS
- ✅ GPL license compatible with QWAMOS

**Integration Strategy:**
1. Extract Tor binaries for ARM64
2. Port Tor controller to QWAMOS Python backend
3. Integrate with Whonix Gateway VM
4. Configure for transparent proxy (iptables routing)
5. Implement stream isolation per VM

**Recommended Action:** Immediate integration into `network/tor/` directory

**Code Example (JTorProx):**
```java
// Start Tor
TorStarter torStarter = new TorStarter();
torStarter.startTor(context);

// Get SOCKS proxy
int socksPort = torStarter.getSocksPort(); // 9050

// Configure stream isolation
torStarter.setStreamIsolation(isolationKey);
```

**Equivalent in QWAMOS (Python):**
```python
# network/tor/controller.py
import stem
from stem.control import Controller

class QwamosTorController:
    def start_tor(self):
        # Start Tor process
        self.tor_process = subprocess.Popen([
            '/usr/bin/tor',
            '-f', '/etc/qwamos/torrc'
        ])

    def get_socks_port(self) -> int:
        return 9050

    def set_stream_isolation(self, vm_name: str):
        # Create unique SOCKS port per VM
        vm_port = 9050 + self.vm_ports[vm_name]
        return vm_port
```

---

### 3. Ashigaru-Whirlpool-Client (231 KB)

**Type:** Java Library

**Description:** Client implementation of Whirlpool CoinJoin protocol

**Features:**
- Automated CoinJoin mixing
- Coordinator communication
- UTXO pool management
- Mixing fee calculation

**Relevance to QWAMOS:**
- ✅ Enhances AEGIS Vault with transaction privacy
- ✅ Can be integrated with Ashigaru-Mobile in vault-vm
- ⚠️ Requires network access (conflicts with airgap, use in work-vm instead)

**Integration Strategy:**
- Run Whirlpool client in work-vm (not vault-vm due to network requirement)
- Coordinate with AEGIS Vault for transaction signing
- Use QR code bridge for unsigned → signed transaction flow

---

### 4. Ashigaru-Whirlpool-Protocol (51 KB)

**Type:** Protocol Definition Library

**Description:** Whirlpool protocol specifications and message formats

**Relevance to QWAMOS:**
- ✅ Required for Whirlpool-Client
- ✅ Lightweight, easy to integrate

---

### 5. Ashigaru-Whirlpool-Server (334 KB)

**Type:** Java Server Application

**Description:** Coordinator server for Whirlpool CoinJoin

**Relevance to QWAMOS:**
- ⚠️ Server-side component (not needed for client)
- ❌ Most users will use public Whirlpool coordinators
- ⚠️ Could run own coordinator for privacy, but requires infrastructure

**Recommended:** Skip for QWAMOS v1.0 (use public coordinators)

---

### 6. Ashigaru-Terminal (90 MB)

**Type:** Desktop Application (likely Electron or JavaFX)

**Description:** Desktop version of Ashigaru wallet

**Relevance to QWAMOS:**
- ⚠️ Too large, likely contains duplicate functionality
- ⚠️ Could be useful for x86 emulation testing (QEMU)
- ❌ Not needed for mobile OS

**Recommended:** Skip extraction, focus on mobile components

---

### 7. Other Components

**Ashigaru-Java-Http-Client (41 KB)**
- HTTP client library
- ✅ Lightweight, potentially useful for API calls

**Ashigaru-Java-Server (91 KB)**
- Backend server component
- ⚠️ Server-side (skip for mobile OS)

**Ashigaru-Java-Websocket-Server (25 KB)**
- WebSocket server
- ⚠️ Server-side (skip for mobile OS)

**Ashigaru-XManager-Server (66 KB)**
- XPUB manager server
- ⚠️ Server-side (skip for mobile OS)

**Ashigaru-Brand-Assets (7.4 MB)**
- Logos, icons, branding
- ✅ May contain useful UI assets for QWAMOS theme

---

## Integration Roadmap

### Phase 1: Immediate Integration (Month 2-3)

#### 1. JTorProx → QWAMOS Tor Integration

**Steps:**
1. Extract Tor binaries from JTorProx
   ```bash
   cd ashigaru_analysis/ashigaru-jtorprox/android/libs/
   cp arm64-v8a/libtor.so ~/QWAMOS/network/tor/bin/
   ```

2. Create Python Tor controller
   ```python
   # network/tor/controller.py
   class TorController:
       def __init__(self):
           self.tor_binary = '/opt/qwamos/tor/libtor.so'
           self.control_port = 9051
           self.socks_port = 9050

       def start(self):
           # Start Tor daemon
           pass

       def create_circuit(self, vm_name: str):
           # Create isolated circuit for VM
           pass
   ```

3. Configure Whonix Gateway VM to use JTorProx binaries

4. Test Tor connectivity from android-vm

**ETA:** 1 week

---

#### 2. Ashigaru-Mobile → AEGIS Vault Integration

**Option A: Run in Android VM**
```
work-vm
    └─> android-vm
        └─> Ashigaru Mobile APK
```

**Pros:**
- No code changes needed
- Full functionality immediately
- Familiar interface

**Cons:**
- Runs in android-vm, not true airgap
- Cannot leverage vault-vm isolation

**Option B: Extract Bitcoin Libraries**
```
vault-vm (airgapped)
    └─> bitcoinj library
    └─> Whirlpool client
    └─> QWAMOS custom UI (Python/Qt or CLI)
```

**Pros:**
- True airgap in vault-vm
- Lightweight
- Full control over UI

**Cons:**
- Requires porting Java libraries to Python or running JVM in vault-vm
- Custom UI development

**Recommended:** Start with Option A (android-vm), migrate to Option B in Phase 2

**Steps:**
1. Copy Ashigaru APK to android-vm
   ```bash
   cp ~/storage/downloads/Mega/ashigaru_mobile_v1.1.1.apk \
      ~/QWAMOS/vms/android/apps/
   ```

2. Install via ADB when android-vm boots
   ```bash
   adb install ashigaru_mobile_v1.1.1.apk
   ```

3. Configure Ashigaru to use Tor from Whonix Gateway

4. Test wallet creation and transaction signing

**ETA:** 2 weeks

---

### Phase 2: Deep Integration (Month 5-6)

#### 1. Pure Vault-VM Bitcoin Wallet

**Goal:** Extract bitcoinj + whirlpool into standalone vault-vm wallet

**Approach:**
- Run JVM in vault-vm (OpenJDK ARM64)
- Package bitcoinj + whirlpool as JAR
- Create Python wrapper for wallet operations
- QR code signing interface

**Files to Extract:**
```
ashigaru-mobile/bitcoinj/              → vault-vm/bitcoin/bitcoinj/
ashigaru-mobile/whirlpool-client/      → vault-vm/bitcoin/whirlpool/
ashigaru-mobile/whirlpool-protocol/    → vault-vm/bitcoin/whirlpool/
ashigaru-mobile/boltzmann-java/        → vault-vm/bitcoin/boltzmann/
```

**Wallet Manager Architecture:**
```python
# security/aegis/wallets/ashigaru/wallet_manager.py

import jpype
import jpype.imports

class AshigaruWalletManager:
    def __init__(self):
        # Start JVM with bitcoinj classpath
        jpype.startJVM(classpath=[
            '/opt/vault-vm/bitcoin/bitcoinj.jar',
            '/opt/vault-vm/bitcoin/whirlpool.jar'
        ])

        from org.bitcoinj.wallet import Wallet
        self.wallet = Wallet()

    def create_wallet(self, seed: str):
        # Create wallet from BIP39 seed
        pass

    def sign_transaction(self, unsigned_tx: bytes) -> bytes:
        # Sign transaction offline
        pass

    def export_xpub(self) -> str:
        # Export XPUB for watching
        pass
```

**ETA:** 4 weeks

---

#### 2. Whirlpool CoinJoin Integration

**Goal:** Enable Whirlpool mixing from work-vm coordinated with vault-vm

**Flow:**
```
work-vm (online)
    ├─> Whirlpool client
    ├─> Coordinator communication
    └─> Create unsigned CoinJoin TX
        └─> QR code
            └─> User scans with vault-vm
                └─> vault-vm signs TX
                    └─> QR code
                        └─> work-vm broadcasts
```

**Implementation:**
```python
# vms/work/whirlpool_manager.py

class WhirlpoolManager:
    def __init__(self):
        self.coordinator_url = "https://coordinator.whirlpool.ashigaru.rs"

    def start_mixing(self, utxos: list):
        # Register UTXOs for mixing
        mix_tx = self.coordinator.create_mix_tx(utxos)

        # Create QR code for signing
        qr = QRCodeGenerator.encode(mix_tx)
        return qr

    def broadcast_signed_tx(self, signed_tx: bytes):
        # Broadcast via Tor
        self.tor_client.broadcast(signed_tx)
```

**ETA:** 3 weeks

---

### Phase 3: UI Integration (Month 9-10)

#### 1. React Native Frontend for Ashigaru Wallet

**Goal:** Create QWAMOS-native UI for Ashigaru wallet matching mockups

**React Native Components:**
```typescript
// frontend/screens/AegisVault.tsx

const AegisVault = () => {
  const [wallet, setWallet] = useState<AshigaruWallet | null>(null);
  const [balance, setBalance] = useState<number>(0);

  const scanUnsignedTx = () => {
    // Open QR scanner
    // Parse unsigned transaction
    // Sign with vault-vm
  };

  return (
    <Screen>
      <WalletSelector
        wallets={['Ashigaru Bitcoin', 'Cake Wallet XMR', 'Sparrow']}
      />
      <BalanceDisplay balance={balance} currency="BTC" />
      <QRScanner onScan={scanUnsignedTx} />
      <AirgapStatusIndicator enabled={true} />
    </Screen>
  );
};
```

**Native Module Bridge:**
```typescript
// frontend/services/ashigaruService.ts

import { NativeModules } from 'react-native';

const { AshigaruWalletModule } = NativeModules;

export class AshigaruService {
  static async createWallet(seed: string): Promise<string> {
    return await AshigaruWalletModule.createWallet(seed);
  }

  static async signTransaction(unsignedTx: string): Promise<string> {
    return await AshigaruWalletModule.signTransaction(unsignedTx);
  }

  static async getBalance(): Promise<number> {
    return await AshigaruWalletModule.getBalance();
  }
}
```

**ETA:** 4 weeks

---

## Licensing Considerations

### JTorProx
- **License:** GNU GPLv3
- **Forked From:** Samourai Wallet (Apache 2.0)
- **Compatibility:** ✅ Compatible with QWAMOS GPLv3

### Ashigaru-Mobile
- **License:** GNU GPLv3
- **Forked From:** Samourai Wallet (Apache 2.0)
- **Compatibility:** ✅ Compatible with QWAMOS GPLv3

### Whirlpool Components
- **License:** GNU GPLv3
- **Compatibility:** ✅ Compatible with QWAMOS GPLv3

**Conclusion:** All Ashigaru components are GPLv3, fully compatible with QWAMOS. No licensing conflicts.

---

## Technical Debt & Considerations

### 1. JVM in Vault-VM

**Challenge:** Running Java libraries (bitcoinj) in vault-vm requires JVM

**Options:**
- **Option A:** OpenJDK ARM64 in vault-vm (~200MB)
- **Option B:** Port bitcoinj to Python (massive effort, not recommended)
- **Option C:** Use Electrum wallet instead (Python native)

**Recommendation:** Option A (OpenJDK) for Ashigaru integration, Option C (Electrum) as alternative

### 2. Whirlpool CoinJoin Network Access

**Challenge:** CoinJoin requires network communication, conflicts with airgap

**Solution:**
- Run Whirlpool client in work-vm (online)
- Coordinate with vault-vm via QR codes for signing
- Clear separation: work-vm = network, vault-vm = keys

### 3. Android APK in Android VM

**Challenge:** Running full Ashigaru APK in android-vm is heavy

**Solution:**
- Phase 1: Full APK in android-vm (quick start)
- Phase 2: Extract core libraries to vault-vm (lightweight)

---

## Code Extraction Plan

### Immediate Actions (This Week)

```bash
# 1. Extract Tor binaries
mkdir -p ~/QWAMOS/network/tor/bin
cp ashigaru_analysis/ashigaru-jtorprox/android/libs/arm64-v8a/* \
   ~/QWAMOS/network/tor/bin/

# 2. Copy Ashigaru APK to android-vm
mkdir -p ~/QWAMOS/vms/android/apps
cp ~/storage/downloads/Mega/ashigaru_mobile_v1.1.1.apk \
   ~/QWAMOS/vms/android/apps/

# 3. Extract Whirlpool libraries
mkdir -p ~/QWAMOS/security/aegis/wallets/ashigaru
cp -r ashigaru_analysis/ashigaru-mobile/whirlpool-client \
      ~/QWAMOS/security/aegis/wallets/ashigaru/
cp -r ashigaru_analysis/ashigaru-mobile/whirlpool-protocol \
      ~/QWAMOS/security/aegis/wallets/ashigaru/

# 4. Extract bitcoinj
mkdir -p ~/QWAMOS/security/aegis/wallets/ashigaru/bitcoinj
cp -r ashigaru_analysis/ashigaru-mobile/bitcoinj \
      ~/QWAMOS/security/aegis/wallets/ashigaru/

# 5. Document integration
# (this file)
```

---

## Summary

Ashigaru components provide CRITICAL functionality for QWAMOS:

### High Priority (Immediate Integration)
1. ✅✅✅ **JTorProx** - Tor integration for Whonix Gateway
2. ✅✅ **Ashigaru-Mobile** - Bitcoin wallet for AEGIS Vault
3. ✅ **Whirlpool-Client** - Transaction privacy (CoinJoin)

### Medium Priority (Phase 2)
4. ✅ **bitcoinj** - Bitcoin library extraction
5. ✅ **Whirlpool-Protocol** - Protocol definitions

### Low Priority (Future)
6. ⚠️ **Brand Assets** - UI resources (optional)
7. ❌ **Server Components** - Not needed for mobile OS
8. ❌ **Terminal** - Desktop app (not relevant)

**Recommendation:** Proceed with JTorProx integration immediately, followed by Ashigaru-Mobile testing in android-vm.

---

**Next Steps:**
1. Extract Tor binaries and create Python controller
2. Test Tor connectivity in QWAMOS environment
3. Set up android-vm with Ashigaru APK
4. Design QR code transaction signing flow
5. Begin Phase 1 integration (2-3 weeks)

---

**Status:** Analysis Complete
**Integration Priority:** CRITICAL (Tor) + HIGH (Wallet)
**ETA to Integration:** 2-4 weeks
