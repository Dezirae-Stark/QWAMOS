# Chimera Decoy Protocol Specification

**Component:** QWAMOS Phase 5 - Network Isolation
**Version:** 1.0.0
**Status:** Specification Complete - Implementation Pending
**Priority:** Medium
**Security Level:** Defensive Obfuscation Layer

---

## Executive Summary

The **Chimera Decoy Protocol** is a defensive network traffic obfuscation system designed to defeat traffic analysis, pattern recognition, and behavioral fingerprinting attacks against QWAMOS users. Named after the mythological creature with multiple heads, Chimera generates realistic decoy traffic patterns that blend with legitimate user activity, making it extremely difficult for adversaries to determine what the user is actually doing.

**Key Objectives:**
- **Traffic Analysis Resistance:** Prevent ISPs, state actors, and network observers from determining user activity patterns
- **Behavioral Obfuscation:** Generate realistic cover traffic that mimics legitimate usage patterns
- **Timing Attack Mitigation:** Eliminate timing-based correlation attacks against Tor/VPN traffic
- **Volume Normalization:** Maintain constant network activity to prevent traffic volume analysis

**Threat Model:**
- Nation-state level adversaries with network surveillance capabilities
- ISPs performing deep packet inspection (DPI) and traffic analysis
- Upstream network observers attempting Tor traffic correlation
- Machine learning-based traffic classification systems
- Long-term pattern analysis attacks

---

## Architecture Overview

### Traffic Generation Modes

Chimera operates in multiple modes simultaneously, creating a multi-headed traffic generation system:

```
┌────────────────────────────────────────────────────────────────┐
│                    Chimera Protocol Controller                 │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              Traffic Pattern Engine                       │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │  ML-Based Pattern Generator                         │ │ │
│  │  │  - Learns from legitimate user behavior             │ │ │
│  │  │  - Generates statistically similar traffic          │ │ │
│  │  │  - Adapts to time-of-day patterns                   │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌───────────┬───────────┬───────────┬───────────┬──────────┐ │
│  │  Head 1   │  Head 2   │  Head 3   │  Head 4   │  Head 5  │ │
│  │  HTTP/S   │  Streaming│  Messaging│  Downloads│  Gaming  │ │
│  │  Browsing │  Video    │  Apps     │  Updates  │  Traffic │ │
│  └─────┬─────┴─────┬─────┴─────┬─────┴─────┬─────┴─────┬────┘ │
│        │           │           │           │           │      │
└────────┼───────────┼───────────┼───────────┼───────────┼──────┘
         │           │           │           │           │
         ▼           ▼           ▼           ▼           ▼
    ┌────────────────────────────────────────────────────────┐
    │         Whonix Gateway / Network Router                │
    │  ┌──────────────────────────────────────────────────┐ │
    │  │  Traffic Mixer & Scheduler                       │ │
    │  │  - Interleaves real + decoy traffic              │ │
    │  │  - Maintains constant bandwidth profile          │ │
    │  │  - Prevents traffic analysis                     │ │
    │  └──────────────────────────────────────────────────┘ │
    └────────────────────────────────────────────────────────┘
                            │
                            ▼
                      [ Tor / I2P / VPN ]
                            │
                            ▼
                       [ Internet ]
```

---

## Five Heads of Chimera

### Head 1: HTTP/HTTPS Browsing Simulation

**Purpose:** Simulate realistic web browsing behavior

**Techniques:**
- **Synthetic Page Loads:** Generate HTTP/HTTPS requests that mimic loading real websites
  - Random User-Agent rotation (desktop + mobile browsers)
  - Realistic request patterns (HTML → CSS → JS → Images)
  - Timing between requests matches real browsing (2-10s think time)
  - Cookie handling and session management
- **Content Types:** Mix of news sites, social media, e-commerce, blogs
- **Bandwidth Profile:** 50-500 KB per page load, 2-5 pages per session
- **Session Duration:** 5-30 minute browsing sessions with pauses

**Implementation:**
```python
class HTTPBrowsingDecoy:
    """Head 1: HTTP/HTTPS browsing simulation"""

    def __init__(self):
        self.user_agents = self._load_user_agents()
        self.site_profiles = self._load_site_profiles()
        self.session_tracker = {}

    async def generate_browsing_session(self):
        """Generate a realistic browsing session"""
        session = aiohttp.ClientSession()
        user_agent = random.choice(self.user_agents)

        # Pick 3-7 sites to "visit"
        sites = random.sample(self.site_profiles, random.randint(3, 7))

        for site in sites:
            # Load main page
            await self._synthetic_page_load(session, site['url'], user_agent)

            # Random think time (2-10 seconds)
            await asyncio.sleep(random.uniform(2, 10))

            # Load 1-3 sub-pages
            for _ in range(random.randint(1, 3)):
                subpage = random.choice(site['subpages'])
                await self._synthetic_page_load(session, subpage, user_agent)
                await asyncio.sleep(random.uniform(1, 5))

        await session.close()

    async def _synthetic_page_load(self, session, url, user_agent):
        """Simulate loading a web page with resources"""
        # Main HTML (discard response body to save bandwidth)
        await session.head(url, headers={'User-Agent': user_agent})

        # Simulate loading 5-15 resources (CSS, JS, images)
        for _ in range(random.randint(5, 15)):
            # Generate random resource path
            resource = f"{url}/{self._random_resource_path()}"
            await session.head(resource, headers={'User-Agent': user_agent})
            await asyncio.sleep(random.uniform(0.1, 0.5))
```

### Head 2: Video Streaming Simulation

**Purpose:** Mimic video streaming services (YouTube, Netflix, etc.)

**Techniques:**
- **Constant Bitrate Streams:** Generate traffic matching video streaming patterns
  - 720p: ~2.5 Mbps sustained
  - 1080p: ~5 Mbps sustained
  - 4K: ~15-25 Mbps sustained
- **Adaptive Bitrate:** Simulates ABR streaming with quality changes
- **Buffering Behavior:** Periodic bursts followed by sustained transfer
- **Session Characteristics:**
  - 10-60 minute "watch" sessions
  - Periodic pause/resume events
  - Quality switching based on "available bandwidth"

**Implementation:**
```python
class VideoStreamingDecoy:
    """Head 2: Video streaming simulation"""

    BITRATES = {
        '360p': 500_000,   # 500 Kbps
        '720p': 2_500_000, # 2.5 Mbps
        '1080p': 5_000_000,# 5 Mbps
        '4K': 20_000_000   # 20 Mbps
    }

    async def stream_video_session(self, duration_minutes=20):
        """Simulate a video streaming session"""
        quality = random.choice(['720p', '1080p'])
        bitrate = self.BITRATES[quality]

        # Initial buffering burst (first 10 seconds)
        await self._burst_transfer(bitrate * 10, duration=2)

        # Sustained streaming with occasional quality changes
        elapsed = 0
        while elapsed < duration_minutes * 60:
            # Stream for 30-120 seconds at current quality
            chunk_duration = random.uniform(30, 120)
            await self._sustained_transfer(bitrate, chunk_duration)
            elapsed += chunk_duration

            # 20% chance to change quality
            if random.random() < 0.2:
                quality = random.choice(['720p', '1080p'])
                bitrate = self.BITRATES[quality]
                await asyncio.sleep(random.uniform(1, 3))  # Buffering

            # 10% chance to pause
            if random.random() < 0.1:
                await asyncio.sleep(random.uniform(5, 30))  # Pause duration

    async def _sustained_transfer(self, bitrate, duration):
        """Generate sustained traffic at specified bitrate"""
        bytes_per_second = bitrate // 8
        chunk_size = 16384  # 16 KB chunks

        for _ in range(int(duration)):
            bytes_to_send = bytes_per_second
            while bytes_to_send > 0:
                # Send to /dev/null via Tor (discarded at exit)
                chunk = min(chunk_size, bytes_to_send)
                await self._send_decoy_bytes(chunk)
                bytes_to_send -= chunk
                await asyncio.sleep(chunk / bytes_per_second)
```

### Head 3: Messaging App Simulation

**Purpose:** Mimic encrypted messaging apps (Signal, WhatsApp, Telegram)

**Techniques:**
- **Message Send Pattern:** Small encrypted payloads (500 bytes - 5 KB)
- **Typing Indicators:** Frequent small packets during "typing"
- **Media Messages:** Occasional larger transfers (100 KB - 5 MB for images)
- **Voice/Video Calls:** Sustained bidirectional traffic (50-150 Kbps)
- **Background Sync:** Periodic keepalive messages every 30-60s

**Implementation:**
```python
class MessagingDecoy:
    """Head 3: Messaging app simulation"""

    async def message_session(self, duration_minutes=30):
        """Simulate messaging activity"""
        while duration_minutes > 0:
            # Random interval between messages (1-10 minutes)
            await asyncio.sleep(random.uniform(60, 600))

            action = random.choices(
                ['text', 'image', 'voice', 'typing'],
                weights=[70, 15, 10, 5]
            )[0]

            if action == 'text':
                # Send text message (500 bytes - 2 KB encrypted)
                await self._send_message(random.randint(500, 2000))

            elif action == 'image':
                # Send image (100 KB - 2 MB)
                await self._send_media(random.randint(100_000, 2_000_000))

            elif action == 'voice':
                # Voice message (30s - 2min @ ~20 KB/s)
                duration = random.uniform(30, 120)
                await self._sustained_transfer(20_000, duration)

            elif action == 'typing':
                # Typing indicator (rapid small packets)
                for _ in range(random.randint(3, 10)):
                    await self._send_message(50)  # Tiny keepalive
                    await asyncio.sleep(random.uniform(0.5, 2))

            duration_minutes -= random.uniform(1, 5)
```

### Head 4: Download/Update Simulation

**Purpose:** Mimic software downloads, OS updates, app store traffic

**Techniques:**
- **Large File Downloads:** 10 MB - 500 MB sustained transfers
- **Resume Support:** Interrupted downloads that resume
- **Package Manager Traffic:** Metadata updates + package downloads
- **Burst Pattern:** Idle periods followed by large transfers
- **Checksums/Verification:** Small requests after downloads

**Implementation:**
```python
class DownloadDecoy:
    """Head 4: Software download/update simulation"""

    async def download_session(self):
        """Simulate software download activity"""
        # Decide what to "download"
        downloads = random.choices(
            ['app_update', 'os_update', 'game', 'media'],
            weights=[40, 20, 25, 15]
        )[0]

        if downloads == 'app_update':
            # Small-medium app (5-50 MB)
            size = random.randint(5_000_000, 50_000_000)
            await self._download_file(size, resume_prob=0.1)

        elif downloads == 'os_update':
            # Large OS update (200-800 MB)
            size = random.randint(200_000_000, 800_000_000)
            await self._download_file(size, resume_prob=0.3)

        elif downloads == 'game':
            # Game download (500 MB - 5 GB)
            size = random.randint(500_000_000, 5_000_000_000)
            await self._download_file(size, resume_prob=0.5)

    async def _download_file(self, size_bytes, resume_prob=0.2):
        """Simulate downloading a file with potential resume"""
        downloaded = 0
        bitrate = random.randint(5_000_000, 50_000_000)  # 5-50 Mbps

        while downloaded < size_bytes:
            # Download a chunk
            chunk_size = min(10_000_000, size_bytes - downloaded)  # 10 MB chunks
            await self._burst_transfer(chunk_size, bitrate=bitrate)
            downloaded += chunk_size

            # Random chance to pause/resume (simulates interruption)
            if random.random() < resume_prob:
                await asyncio.sleep(random.uniform(5, 30))
```

### Head 5: Gaming Traffic Simulation

**Purpose:** Mimic online gaming traffic patterns

**Techniques:**
- **Low Latency Packets:** Frequent small packets (100-300 bytes @ 20-60 Hz)
- **Voice Chat:** Sustained VoIP traffic alongside game data
- **Lobby/Matchmaking:** Burst patterns when joining/leaving games
- **Asset Downloads:** Occasional larger transfers for game updates
- **Bidirectional:** Both upload and download simultaneously

**Implementation:**
```python
class GamingDecoy:
    """Head 5: Gaming traffic simulation"""

    async def gaming_session(self, duration_minutes=45):
        """Simulate online gaming session"""
        # Join game (lobby traffic burst)
        await self._burst_transfer(500_000, duration=2)  # 500 KB burst

        # Main game loop
        elapsed = 0
        while elapsed < duration_minutes * 60:
            # Game state updates (60 Hz, 200 bytes per packet)
            for _ in range(60):
                await self._send_packet(200)
                await asyncio.sleep(1/60)  # 16.67ms between packets

            elapsed += 1

            # Occasional voice chat (50% chance during gaming)
            if random.random() < 0.5:
                asyncio.create_task(self._voice_chat(duration=30))

        # Leave game (final burst)
        await self._burst_transfer(200_000, duration=1)

    async def _voice_chat(self, duration):
        """Simulate voice chat during gaming"""
        bitrate = 64_000  # 64 Kbps
        await self._sustained_transfer(bitrate, duration)
```

---

## Traffic Mixing and Scheduling

### Constant Bandwidth Mode

**Goal:** Maintain constant network activity to prevent traffic volume analysis

```python
class ChimeraController:
    """Main Chimera protocol controller"""

    def __init__(self, target_bandwidth_mbps=10):
        self.target_bandwidth = target_bandwidth_mbps * 1_000_000  # Convert to bps
        self.heads = [
            HTTPBrowsingDecoy(),
            VideoStreamingDecoy(),
            MessagingDecoy(),
            DownloadDecoy(),
            GamingDecoy()
        ]
        self.real_traffic_monitor = RealTrafficMonitor()

    async def maintain_constant_bandwidth(self):
        """Main control loop: keep bandwidth constant"""
        while True:
            # Measure real user traffic in last second
            real_bandwidth = self.real_traffic_monitor.get_current_usage()

            # Calculate decoy traffic needed to reach target
            decoy_needed = max(0, self.target_bandwidth - real_bandwidth)

            if decoy_needed > 0:
                # Randomly select heads to activate
                active_heads = random.sample(
                    self.heads,
                    k=random.randint(1, 3)
                )

                # Distribute decoy bandwidth across active heads
                for head in active_heads:
                    asyncio.create_task(
                        head.generate_traffic(decoy_needed / len(active_heads))
                    )

            await asyncio.sleep(1)  # Re-evaluate every second
```

### Adaptive Mode

**Goal:** Adapt decoy traffic to match user's legitimate behavior patterns

```python
class AdaptiveChimeraController:
    """ML-based adaptive traffic generation"""

    def __init__(self):
        self.behavior_model = UserBehaviorModel()
        self.pattern_generator = PatternGenerator()

    async def adaptive_traffic_generation(self):
        """Generate decoy traffic matching user patterns"""
        # Learn from user's real traffic over time
        user_patterns = await self.behavior_model.analyze_user_behavior()

        # Time-of-day patterns
        current_hour = datetime.now().hour

        if 9 <= current_hour <= 17:  # Work hours
            # More messaging, browsing, fewer videos
            self.pattern_generator.set_weights({
                'messaging': 0.4,
                'browsing': 0.3,
                'video': 0.1,
                'downloads': 0.2
            })

        elif 18 <= current_hour <= 23:  # Evening
            # More video, gaming, browsing
            self.pattern_generator.set_weights({
                'video': 0.4,
                'gaming': 0.2,
                'browsing': 0.3,
                'messaging': 0.1
            })

        else:  # Late night/early morning
            # Minimal activity (OS updates, background sync)
            self.pattern_generator.set_weights({
                'downloads': 0.6,
                'messaging': 0.3,
                'browsing': 0.1
            })

        # Generate traffic matching these patterns
        await self.pattern_generator.generate()
```

---

## Security Considerations

### Bandwidth Cost Management

**Problem:** Chimera can consume significant bandwidth with constant traffic

**Solution: Tiered Modes:**

1. **Stealth Mode (Low):** 1-2 Mbps constant
   - Minimal decoy traffic
   - Focus on timing attack mitigation
   - Suitable for metered connections

2. **Balanced Mode (Medium):** 5-10 Mbps constant (Default)
   - Moderate decoy traffic
   - Good traffic analysis resistance
   - ~20-30 GB/day data usage

3. **Maximum Anonymity (High):** 20-50 Mbps constant
   - Heavy decoy traffic
   - Maximum protection against traffic analysis
   - ~100-200 GB/day data usage
   - Only for unlimited connections

**User Control:**
```json
{
  "chimera_mode": "balanced",
  "bandwidth_limit_mbps": 10,
  "schedule": {
    "06:00-23:00": "balanced",
    "23:00-06:00": "stealth"
  },
  "data_cap": {
    "enabled": true,
    "daily_limit_gb": 30,
    "monthly_limit_gb": 500
  }
}
```

### Traffic Destination Selection

**Problem:** Where to send decoy traffic without revealing intent?

**Solution:**
- **Public CDN Endpoints:** Send requests to major CDNs (Cloudflare, Akamai)
  - Appear as normal web traffic
  - Use HEAD requests to minimize bandwidth
- **Tor Exit Diversity:** Spread across multiple exit nodes
- **I2P Eepsites:** Use I2P network for decoy destinations
- **Legitimate Services:** Actually fetch real content (news, weather) and discard

### Detection Resistance

**Adversary Capabilities:**
- Deep Packet Inspection (DPI)
- Machine Learning traffic classification
- Statistical analysis of packet timing

**Countermeasures:**
- **TLS Everywhere:** All decoy traffic uses TLS 1.3
- **Realistic TLS Handshakes:** Use real certificate chains
- **Application Layer Realism:** Send actual HTTP headers, cookies
- **Statistical Mixing:** Blend decoy timing with real traffic
- **No Predictable Patterns:** Randomize everything (timing, order, volume)

---

## Integration with Phase 5 Network Isolation

### Architecture Integration

```
┌─────────────────────────────────────────────────────────────┐
│                  QWAMOS Network Manager                     │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Network Mode: TOR + DNSCrypt + Chimera           │    │
│  └────────────────────────────────────────────────────┘    │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────────┐        ┌─────────────────────────┐   │
│  │ Real User       │        │  Chimera Controller     │   │
│  │ Traffic         │        │  (Decoy Generator)      │   │
│  └────────┬────────┘        └──────────┬──────────────┘   │
│           │                             │                   │
│           └─────────┬───────────────────┘                   │
│                     │                                       │
│           ┌─────────▼──────────┐                           │
│           │  Traffic Mixer     │                           │
│           │  & Scheduler       │                           │
│           └─────────┬──────────┘                           │
│                     │                                       │
└─────────────────────┼───────────────────────────────────────┘
                      │
              ┌───────▼────────┐
              │  Tor Gateway   │
              └───────┬────────┘
                      │
                  [Internet]
```

### Configuration Files

**network/chimera/chimera_config.json:**
```json
{
  "enabled": true,
  "mode": "balanced",
  "target_bandwidth_mbps": 10,
  "adaptive_learning": true,
  "heads": {
    "browsing": {
      "enabled": true,
      "weight": 30,
      "user_agents_file": "/opt/qwamos/network/chimera/user_agents.txt"
    },
    "video_streaming": {
      "enabled": true,
      "weight": 25,
      "quality": "1080p"
    },
    "messaging": {
      "enabled": true,
      "weight": 20
    },
    "downloads": {
      "enabled": true,
      "weight": 15
    },
    "gaming": {
      "enabled": false,
      "weight": 10
    }
  },
  "schedule": {
    "06:00-23:00": "balanced",
    "23:00-06:00": "stealth"
  },
  "bandwidth_limits": {
    "daily_cap_gb": 30,
    "monthly_cap_gb": 500
  }
}
```

### Python Controller

**network/chimera/chimera_controller.py:**
```python
#!/usr/bin/env python3
"""
Chimera Decoy Protocol Controller
"""

import asyncio
import random
from typing import Dict
from pathlib import Path
import json

class ChimeraController:
    """Main Chimera protocol controller"""

    def __init__(self, config_path="/opt/qwamos/network/chimera/chimera_config.json"):
        self.config = self._load_config(config_path)
        self.enabled = self.config.get('enabled', False)
        self.mode = self.config.get('mode', 'balanced')
        self.target_bandwidth = self.config.get('target_bandwidth_mbps', 10) * 1_000_000

        # Initialize traffic heads
        self.heads = self._initialize_heads()

    def start(self):
        """Start Chimera decoy traffic generation"""
        if not self.enabled:
            print("⚠️  Chimera is disabled in configuration")
            return

        print(f"✅ Starting Chimera Decoy Protocol ({self.mode} mode)")
        print(f"   Target Bandwidth: {self.target_bandwidth / 1_000_000} Mbps")

        # Start async event loop for traffic generation
        asyncio.run(self._main_loop())

    async def _main_loop(self):
        """Main control loop"""
        while True:
            # Select random heads to activate
            active_heads = self._select_active_heads()

            # Generate traffic from each head
            tasks = []
            for head in active_heads:
                task = asyncio.create_task(head.generate_traffic())
                tasks.append(task)

            # Wait for all tasks to complete
            await asyncio.gather(*tasks)

            # Random interval before next activation
            await asyncio.sleep(random.uniform(10, 60))

    def stop(self):
        """Stop Chimera decoy traffic generation"""
        print("✅ Stopped Chimera Decoy Protocol")

    def _load_config(self, config_path):
        """Load Chimera configuration"""
        with open(config_path, 'r') as f:
            return json.load(f)

    def _initialize_heads(self):
        """Initialize traffic generation heads"""
        # Implementation here
        pass

    def _select_active_heads(self):
        """Select which heads to activate based on weights"""
        # Implementation here
        pass


if __name__ == "__main__":
    controller = ChimeraController()
    controller.start()
```

---

## Implementation Timeline

**Week 1-2: Core Infrastructure**
- ChimeraController base class
- Traffic measurement/monitoring
- Bandwidth calculation logic

**Week 3-4: Traffic Heads**
- HTTP/HTTPS browsing simulation (Head 1)
- Video streaming simulation (Head 2)
- Messaging simulation (Head 3)

**Week 5-6: Advanced Heads**
- Download/update simulation (Head 4)
- Gaming simulation (Head 5)

**Week 7-8: Adaptive Learning**
- User behavior modeling
- ML-based pattern generation
- Time-of-day adaptation

**Week 9-10: Integration**
- NetworkManager integration
- React Native UI controls
- Testing and optimization

**Total Timeline:** 10 weeks

---

## Testing Strategy

### Unit Tests
- Each traffic head generates realistic patterns
- Bandwidth calculations are accurate
- Timing characteristics match real applications

### Integration Tests
- Chimera integrates cleanly with Tor/I2P/VPN
- No performance impact on real user traffic
- Bandwidth limits are respected

### Security Tests
- Traffic analysis resistance testing
- ML-based classification attempts
- Statistical analysis validation

### Performance Tests
- CPU usage < 5% on ARM64
- RAM usage < 100 MB
- Network overhead acceptable

---

## User Documentation

### Enabling Chimera

```bash
# Enable Chimera in balanced mode
qwamos network chimera enable --mode balanced

# Check status
qwamos network chimera status

# Configure bandwidth limit
qwamos network chimera set-bandwidth 10  # 10 Mbps

# Set schedule
qwamos network chimera schedule \
  --day "06:00-23:00:balanced" \
  --night "23:00-06:00:stealth"
```

### React Native UI

```
┌─────────────────────────────────────────────────┐
│  Network Protection: Chimera Decoy Protocol     │
├─────────────────────────────────────────────────┤
│                                                  │
│  Status: ✅ Active (Balanced Mode)              │
│                                                  │
│  Decoy Traffic Generated: 15.2 GB today         │
│  Real Traffic: 3.8 GB today                     │
│  Total: 19.0 GB today                           │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │  Mode Selection:                           │ │
│  │  ○ Stealth     (1-2 Mbps)                  │ │
│  │  ● Balanced    (5-10 Mbps) [Recommended]  │ │
│  │  ○ Maximum     (20-50 Mbps)                │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  [Advanced Settings] [Disable]                  │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## References

- **Traffic Analysis Attacks:** "Website Fingerprinting in Onion Routing Based Anonymization Networks" (WPES 2011)
- **Cover Traffic:** "CS-BuFLO: A Congestion Sensitive Website Fingerprinting Defense" (WPES 2014)
- **ML-Based Attacks:** "Deep Fingerprinting: Undermining Website Fingerprinting Defenses with Deep Learning" (CCS 2018)
- **Tor Traffic:** "Timing Analysis in Low-Latency Mix Networks" (S&P 2004)

---

**Status:** Specification Complete
**Next Step:** Begin implementation in Phase 5 (Week 11-20)
**Priority:** Medium (after core Tor/I2P/DNSCrypt integration)

**File Location:** `docs/CHIMERA_DECOY_PROTOCOL.md`
**Related:** `docs/PHASE5_NETWORK_ISOLATION.md`, `docs/TECHNICAL_ARCHITECTURE.md`
