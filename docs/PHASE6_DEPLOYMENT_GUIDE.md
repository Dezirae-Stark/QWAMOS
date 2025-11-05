# QWAMOS Phase 6: AI Assistants Deployment Guide

Complete deployment guide for QWAMOS AI Assistant integration system.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)

---

## Overview

Phase 6 implements three AI assistants:

1. **Kali GPT** - Local LLM (100% private, no network)
2. **Claude** - Anthropic API via Tor
3. **ChatGPT** - OpenAI API via Tor

### Architecture

```
┌─────────────────────────────────────────────────┐
│         React Native UI (Frontend)              │
│  ┌──────────┬──────────┬───────────────────┐   │
│  │AIAssistants│AIChat   │AIStats            │   │
│  └──────────┴──────────┴───────────────────┘   │
└─────────────────┬───────────────────────────────┘
                  │ NativeModules
┌─────────────────▼───────────────────────────────┐
│         Java Native Bridge                      │
│         QWAMOSAIBridge.java                     │
└─────────────────┬───────────────────────────────┘
                  │ ProcessBuilder
┌─────────────────▼───────────────────────────────┐
│         Python Backend                          │
│  ┌──────────────────────────────────────────┐  │
│  │  ai_manager.py (Central Orchestrator)    │  │
│  └──────────────────────────────────────────┘  │
│  ┌────────────┬─────────────┬──────────────┐  │
│  │Kali GPT    │Claude       │ChatGPT       │  │
│  │Controller  │Controller   │Controller    │  │
│  └────────────┴─────────────┴──────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## Prerequisites

### System Requirements

- **OS:** Linux (systemd-based)
- **Memory:** Minimum 8GB RAM (for Kali GPT)
- **Storage:** 10GB free space (for Kali GPT model)
- **Network:** Internet access (for model download and cloud APIs)

### Software Dependencies

```bash
# Python 3.8+
python3 --version

# pip3
pip3 --version

# systemd
systemctl --version

# Tor (for cloud APIs)
tor --version
```

### Install Python Dependencies

```bash
pip3 install anthropic openai requests pysocks cryptography llama-cpp-python
```

---

## Installation

### Automated Installation (Recommended)

```bash
cd /data/data/com.termux/files/home/QWAMOS/ai
sudo ./scripts/deploy_ai_services.sh
```

The deployment script will:
1. ✅ Create directory structure
2. ✅ Copy backend files
3. ✅ Install systemd services
4. ✅ Set permissions
5. ✅ Install dependencies
6. ✅ Download Kali GPT model (optional)
7. ✅ Enable and start services

### Manual Installation

#### 1. Create Directory Structure

```bash
sudo mkdir -p /opt/qwamos/ai/{kali_gpt,claude,chatgpt,config,cache,logs}
sudo mkdir -p /opt/qwamos/ai/kali_gpt/{models,prompts,tools,knowledge,cache}
sudo mkdir -p /opt/qwamos/ai/claude/{prompts,cache}
sudo mkdir -p /opt/qwamos/ai/chatgpt/{prompts,cache}
sudo mkdir -p /var/log/qwamos
```

#### 2. Copy Backend Files

```bash
cd /data/data/com.termux/files/home/QWAMOS/ai

# Copy main files
sudo cp ai_manager.py /opt/qwamos/ai/
sudo cp qwamos-ai /opt/qwamos/ai/
sudo chmod +x /opt/qwamos/ai/qwamos-ai

# Copy controllers
sudo cp -r kali_gpt/ /opt/qwamos/ai/
sudo cp -r claude/ /opt/qwamos/ai/
sudo cp -r chatgpt/ /opt/qwamos/ai/

# Copy config
sudo cp -r config/ /opt/qwamos/ai/

# Copy security modules
sudo cp -r security/ /opt/qwamos/ai/
```

#### 3. Install Systemd Services

```bash
sudo cp systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
```

#### 4. Create QWAMOS User

```bash
sudo useradd -r -s /bin/false qwamos
```

#### 5. Set Permissions

```bash
sudo chown -R qwamos:qwamos /opt/qwamos/ai
sudo chmod 700 /opt/qwamos/ai/config  # Protect API keys
```

#### 6. Download Kali GPT Model

```bash
sudo /opt/qwamos/ai/scripts/download_kali_gpt_model.sh
```

Select quantization level (Q4_K_M recommended for 4.5GB).

---

## Configuration

### Kali GPT (Local LLM)

Edit `/opt/qwamos/ai/config/kali_gpt_config.json`:

```json
{
  "model_path": "/opt/qwamos/ai/kali_gpt/models/llama-3.1-8b-q4.gguf",
  "context_length": 8192,
  "temperature": 0.7,
  "threads": 4,
  "system_prompt": "You are Kali GPT, a penetration testing assistant..."
}
```

**No API key required** - Runs 100% locally.

### Claude (Anthropic API)

Edit `/opt/qwamos/ai/config/claude_config.json`:

```json
{
  "model": "claude-3-5-sonnet-20241022",
  "max_tokens": 4096,
  "routing": {
    "method": "tor",
    "proxy": "socks5h://127.0.0.1:9050"
  },
  "privacy": {
    "sanitize_requests": true,
    "cache_locally": true
  },
  "cost_limits": {
    "max_monthly_cost": 50.00
  }
}
```

**Enable with API key:**

```bash
sudo /opt/qwamos/ai/qwamos-ai enable claude --api-key sk-ant-YOUR_KEY_HERE
```

### ChatGPT (OpenAI API)

Edit `/opt/qwamos/ai/config/chatgpt_config.json`:

```json
{
  "model": "gpt-4-turbo-preview",
  "max_tokens": 4096,
  "routing": {
    "method": "tor",
    "proxy": "socks5h://127.0.0.1:9050"
  },
  "features": {
    "function_calling": true,
    "vision": true
  }
}
```

**Enable with API key:**

```bash
sudo /opt/qwamos/ai/qwamos-ai enable chatgpt --api-key sk-proj-YOUR_KEY_HERE
```

---

## Service Management

### Enable Services

```bash
# Enable AI Manager (required)
sudo systemctl enable qwamos-ai-manager.service

# Enable specific AI services
sudo systemctl enable qwamos-ai-kali-gpt.service
sudo systemctl enable qwamos-ai-claude.service
sudo systemctl enable qwamos-ai-chatgpt.service
```

### Start Services

```bash
sudo systemctl start qwamos-ai-manager.service
sudo systemctl start qwamos-ai-kali-gpt.service
```

### Check Status

```bash
systemctl status qwamos-ai-*.service
```

### View Logs

```bash
# Real-time logs
sudo journalctl -u qwamos-ai-manager.service -f

# Last 100 lines
sudo journalctl -u qwamos-ai-kali-gpt.service -n 100
```

---

## Testing

### Run Integration Tests

```bash
cd /data/data/com.termux/files/home/QWAMOS/ai/tests
python3 test_ai_integration.py
```

Expected output:
```
test_enable_claude (__main__.TestAIIntegration) ... ok
test_query_kali_gpt (__main__.TestAIIntegration) ... ok
test_usage_stats_tracking (__main__.TestAIIntegration) ... ok
...

Ran 15 tests in 0.234s

OK
```

### Test AI Services

#### Test Kali GPT

```bash
/opt/qwamos/ai/qwamos-ai query kali-gpt "How do I scan ports with nmap?"
```

Expected response:
```
To scan ports with nmap:

1. Basic scan:
   nmap <target_ip>

2. Scan specific ports:
   nmap -p 80,443 <target_ip>

3. Full port scan:
   nmap -p- <target_ip>
...
```

#### Test Claude

```bash
/opt/qwamos/ai/qwamos-ai query claude "Explain post-quantum cryptography"
```

#### Test ChatGPT

```bash
/opt/qwamos/ai/qwamos-ai query chatgpt "Write a Python hello world script"
```

### Test Tor Routing

Verify cloud API requests route through Tor:

```bash
# Check Tor status
sudo systemctl status qwamos-tor.service

# Test Tor connection
curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip
```

Expected response:
```json
{"IsTor": true, "IP": "xxx.xxx.xxx.xxx"}
```

---

## React Native UI Integration

### 1. Register Native Module

Edit `MainApplication.java`:

```java
import com.qwamos.ai.QWAMOSAIPackage;

@Override
protected List<ReactPackage> getPackages() {
  return Arrays.<ReactPackage>asList(
    new MainReactPackage(),
    new QWAMOSNetworkPackage(),  // Existing
    new QWAMOSAIPackage()         // Add this
  );
}
```

### 2. Import AI Screens

In your React Native app:

```typescript
import { AIAssistantsScreen } from './ui/screens/AIAssistants';
import { AIChatScreen } from './ui/screens/AIChat';
import { AIStatsScreen } from './ui/screens/AIStats';
```

### 3. Test UI Components

```bash
# Run React Native app
npx react-native run-android
```

---

## Troubleshooting

### Issue: Kali GPT won't start

**Symptoms:**
```
systemctl status qwamos-ai-kali-gpt.service
● qwamos-ai-kali-gpt.service - QWAMOS Kali GPT Local LLM Service
   Loaded: loaded
   Active: failed (Result: exit-code)
```

**Solutions:**

1. Check if model file exists:
   ```bash
   ls -lh /opt/qwamos/ai/kali_gpt/models/llama-3.1-8b-q4.gguf
   ```

2. Download model if missing:
   ```bash
   sudo /opt/qwamos/ai/scripts/download_kali_gpt_model.sh
   ```

3. Check memory:
   ```bash
   free -h  # Need at least 5GB available
   ```

4. Check logs:
   ```bash
   sudo journalctl -xe -u qwamos-ai-kali-gpt.service
   ```

---

### Issue: Claude/ChatGPT API errors

**Symptoms:**
```
Error: Failed to connect to Anthropic API
```

**Solutions:**

1. Check Tor service:
   ```bash
   sudo systemctl status qwamos-tor.service
   ```

2. Test Tor connection:
   ```bash
   curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip
   ```

3. Verify API key:
   ```bash
   /opt/qwamos/ai/qwamos-ai test claude
   ```

4. Check firewall:
   ```bash
   sudo nft list ruleset | grep 9050
   ```

---

### Issue: High memory usage

**Symptoms:**
- System slowdown
- Kali GPT crashes

**Solutions:**

1. Use smaller model quantization (Q2 or Q3):
   ```bash
   sudo /opt/qwamos/ai/scripts/download_kali_gpt_model.sh
   # Select Q2_K or Q3_K_M
   ```

2. Reduce context length:
   Edit `/opt/qwamos/ai/config/kali_gpt_config.json`:
   ```json
   {
     "context_length": 4096  // Reduced from 8192
   }
   ```

3. Stop service when not in use:
   ```bash
   sudo systemctl stop qwamos-ai-kali-gpt.service
   ```

---

### Issue: Native module not found

**Symptoms:**
```
Error: Cannot find module 'QWAMOSAIBridge'
```

**Solutions:**

1. Verify Java files are compiled:
   ```bash
   ls -l app/build/intermediates/javac/debug/classes/com/qwamos/ai/
   ```

2. Clean and rebuild:
   ```bash
   cd android
   ./gradlew clean
   ./gradlew assembleDebug
   ```

3. Restart Metro bundler:
   ```bash
   npx react-native start --reset-cache
   ```

---

## Performance Optimization

### Kali GPT Performance

**For faster inference:**

Edit `/opt/qwamos/ai/config/kali_gpt_config.json`:

```json
{
  "threads": 8,           // Increase (max = CPU cores)
  "batch_size": 512,      // Increase for throughput
  "mlock": true,          // Lock model in memory
  "use_mmap": true        // Use memory mapping
}
```

**For lower memory:**

```json
{
  "context_length": 2048,  // Reduce
  "threads": 4,            // Reduce
  "batch_size": 256        // Reduce
}
```

### Cloud API Performance

**Reduce latency:**

1. Use I2P as fallback to Tor (faster circuits)
2. Enable response caching
3. Reduce max_tokens in queries

---

## Security Best Practices

### API Key Security

1. ✅ API keys encrypted with Kyber-1024 + ChaCha20
2. ✅ Config directory: `chmod 700`
3. ✅ Never log API keys
4. ✅ Rotate keys monthly

### Network Security

1. ✅ All cloud API calls via Tor
2. ✅ PII sanitization before sending
3. ✅ Kali GPT: Complete network isolation
4. ✅ IP leak detection tests

### Resource Limits

All services have:
- Memory limits (1-8GB)
- CPU quotas (30-80%)
- Filesystem isolation
- No privilege escalation

---

## Backup and Restore

### Backup Configuration

```bash
tar czf qwamos-ai-backup-$(date +%Y%m%d).tar.gz \
  /opt/qwamos/ai/config/*.json \
  /opt/qwamos/ai/cache/* \
  /etc/systemd/system/qwamos-ai-*.service
```

### Restore Configuration

```bash
tar xzf qwamos-ai-backup-20251104.tar.gz -C /
sudo systemctl daemon-reload
sudo systemctl restart qwamos-ai-*.service
```

---

## Uninstallation

```bash
# Stop services
sudo systemctl stop qwamos-ai-*.service

# Disable services
sudo systemctl disable qwamos-ai-*.service

# Remove service files
sudo rm /etc/systemd/system/qwamos-ai-*.service

# Remove backend files
sudo rm -rf /opt/qwamos/ai

# Reload systemd
sudo systemctl daemon-reload
```

---

## Additional Resources

- **Main README:** `/opt/qwamos/ai/README.md`
- **Systemd Guide:** `/opt/qwamos/ai/systemd/README.md`
- **Test Suite:** `/opt/qwamos/ai/tests/`
- **GitHub:** https://github.com/Dezirae-Stark/QWAMOS

---

**Version:** 0.6.0-alpha
**Last Updated:** 2025-11-04
**Status:** Phase 6 @ 100% (Deployment Complete)
