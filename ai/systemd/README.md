# QWAMOS AI Systemd Services

Systemd service units for managing QWAMOS AI assistant backend services.

## Services Overview

| Service | Description | Dependencies | Memory Limit |
|---------|-------------|--------------|--------------|
| `qwamos-ai-manager.service` | Central AI orchestrator | Tor | 2GB |
| `qwamos-ai-kali-gpt.service` | Local Kali GPT LLM server | None | 8GB |
| `qwamos-ai-claude.service` | Claude API daemon | Tor | 1GB |
| `qwamos-ai-chatgpt.service` | ChatGPT API daemon | Tor | 1GB |

## Installation

### 1. Copy Service Files

```bash
sudo cp *.service /etc/systemd/system/
```

### 2. Reload Systemd

```bash
sudo systemctl daemon-reload
```

### 3. Enable Services (Auto-start on Boot)

```bash
# Enable AI Manager (required)
sudo systemctl enable qwamos-ai-manager.service

# Enable specific AI services as needed
sudo systemctl enable qwamos-ai-kali-gpt.service  # Optional
sudo systemctl enable qwamos-ai-claude.service     # Optional
sudo systemctl enable qwamos-ai-chatgpt.service    # Optional
```

## Usage

### Start Services

```bash
# Start AI Manager
sudo systemctl start qwamos-ai-manager.service

# Start Kali GPT (local LLM)
sudo systemctl start qwamos-ai-kali-gpt.service

# Start Claude (API via Tor)
sudo systemctl start qwamos-ai-claude.service

# Start ChatGPT (API via Tor)
sudo systemctl start qwamos-ai-chatgpt.service
```

### Stop Services

```bash
sudo systemctl stop qwamos-ai-manager.service
sudo systemctl stop qwamos-ai-kali-gpt.service
sudo systemctl stop qwamos-ai-claude.service
sudo systemctl stop qwamos-ai-chatgpt.service
```

### Check Status

```bash
# Check status of all AI services
systemctl status qwamos-ai-*.service

# Check individual service
systemctl status qwamos-ai-kali-gpt.service
```

### View Logs

```bash
# Real-time logs for AI Manager
sudo journalctl -u qwamos-ai-manager.service -f

# Last 100 lines from Kali GPT
sudo journalctl -u qwamos-ai-kali-gpt.service -n 100

# Logs since yesterday
sudo journalctl -u qwamos-ai-claude.service --since yesterday

# All AI service logs
sudo journalctl -u 'qwamos-ai-*' -f
```

### Restart Services

```bash
# Restart after configuration changes
sudo systemctl restart qwamos-ai-manager.service
```

## Service Details

### AI Manager Service

**Purpose:** Central orchestration daemon for all AI services

**Port:** Unix socket at `/var/run/qwamos/ai-manager.sock`

**Configuration:** `/opt/qwamos/ai/config/ai_manager_config.json`

**Dependencies:**
- Tor (for cloud API routing)

**Auto-restart:** Yes (10s delay)

---

### Kali GPT Service

**Purpose:** Local LLM server for penetration testing assistance

**Type:** 100% local (no network access)

**Model:** Llama 3.1 8B quantized (Q4_K_M)

**Model Path:** `/opt/qwamos/ai/kali_gpt/models/llama-3.1-8b-q4.gguf`

**Memory:** 5-8GB RAM required

**Configuration:** `/opt/qwamos/ai/config/kali_gpt_config.json`

**Network:** Completely isolated (`PrivateNetwork=true`)

**Auto-restart:** Yes (15s delay)

---

### Claude Service

**Purpose:** Anthropic Claude API daemon with Tor routing

**Type:** Cloud API via Tor

**Proxy:** `socks5h://127.0.0.1:9050`

**Configuration:** `/opt/qwamos/ai/config/claude_config.json`

**API Key Storage:** Encrypted in config file

**Dependencies:**
- Tor service must be running
- Valid Anthropic API key required

**Network Restrictions:** Only localhost (127.0.0.1) for Tor connection

**Auto-restart:** Yes (10s delay)

---

### ChatGPT Service

**Purpose:** OpenAI ChatGPT API daemon with Tor routing

**Type:** Cloud API via Tor

**Proxy:** `socks5h://127.0.0.1:9050`

**Configuration:** `/opt/qwamos/ai/config/chatgpt_config.json`

**API Key Storage:** Encrypted in config file

**Dependencies:**
- Tor service must be running
- Valid OpenAI API key required

**Network Restrictions:** Only localhost (127.0.0.1) for Tor connection

**Auto-restart:** Yes (10s delay)

## Security Features

All services include:

- ✅ **NoNewPrivileges** - Prevents privilege escalation
- ✅ **PrivateTmp** - Isolated /tmp directory
- ✅ **ProtectSystem=strict** - Read-only filesystem (except whitelisted paths)
- ✅ **ProtectHome** - No access to user home directories
- ✅ **ProtectKernelTunables** - No kernel parameter modification
- ✅ **RestrictNamespaces** - Namespace restriction
- ✅ **Resource Limits** - Memory and CPU quotas

### Network Isolation

- **Kali GPT:** Complete network isolation (`PrivateNetwork=true`)
- **Claude/ChatGPT:** Only localhost access for Tor proxy

## Troubleshooting

### Service Won't Start

```bash
# Check status for detailed error
systemctl status qwamos-ai-kali-gpt.service

# View logs
journalctl -xe -u qwamos-ai-kali-gpt.service
```

Common issues:
- **Model file missing:** Download Kali GPT model first
- **Permission denied:** Check file ownership and permissions
- **Tor not running:** Start Tor service for cloud APIs
- **Insufficient memory:** Kali GPT requires 5-8GB RAM

### High Memory Usage

Kali GPT uses 5-8GB RAM by design (LLM model size). To reduce:

1. Use a smaller quantized model (Q2 or Q3)
2. Reduce context length in config
3. Stop service when not in use

### Tor Connection Issues

```bash
# Check if Tor is running
systemctl status qwamos-tor.service

# Test Tor connection
curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip

# Restart Tor
sudo systemctl restart qwamos-tor.service
```

### API Key Errors

```bash
# Update API key
python3 /opt/qwamos/ai/ai_manager.py update-api-key claude sk-ant-YOUR_NEW_KEY
python3 /opt/qwamos/ai/ai_manager.py update-api-key chatgpt sk-proj-YOUR_NEW_KEY

# Restart service
sudo systemctl restart qwamos-ai-claude.service
```

## Performance Tuning

### Kali GPT Performance

Edit `/opt/qwamos/ai/config/kali_gpt_config.json`:

```json
{
  "threads": 8,              // Increase for faster inference
  "context_length": 4096,    // Reduce if running out of memory
  "batch_size": 512,         // Increase for throughput
  "temperature": 0.7         // Adjust creativity (0.0-1.0)
}
```

Then restart:
```bash
sudo systemctl restart qwamos-ai-kali-gpt.service
```

### CPU Priority

High-priority processing (already configured):
- Kali GPT: `Nice=-5`

### Memory Optimization

Current limits:
- AI Manager: 2GB
- Kali GPT: 8GB (6GB soft limit)
- Claude/ChatGPT: 1GB each

To adjust, edit service files and reload:
```bash
sudo systemctl daemon-reload
sudo systemctl restart qwamos-ai-kali-gpt.service
```

## Monitoring

### Resource Usage

```bash
# CPU and memory usage
systemctl status qwamos-ai-*.service

# Detailed resource monitoring
systemd-cgtop
```

### Service Health

```bash
# Check if services are active
systemctl is-active qwamos-ai-manager.service

# Check restart count
systemctl show qwamos-ai-kali-gpt.service -p NRestarts
```

## Logs Rotation

Logs are managed by journald with automatic rotation.

To limit log size:

```bash
# Edit /etc/systemd/journald.conf
SystemMaxUse=100M

# Restart journald
sudo systemctl restart systemd-journald
```

## Backup and Restore

### Backup Configuration

```bash
tar czf qwamos-ai-backup.tar.gz \
  /opt/qwamos/ai/config/*.json \
  /opt/qwamos/ai/cache/* \
  /etc/systemd/system/qwamos-ai-*.service
```

### Restore Configuration

```bash
tar xzf qwamos-ai-backup.tar.gz -C /
sudo systemctl daemon-reload
sudo systemctl restart qwamos-ai-*.service
```

## Uninstallation

```bash
# Stop and disable services
sudo systemctl stop qwamos-ai-*.service
sudo systemctl disable qwamos-ai-*.service

# Remove service files
sudo rm /etc/systemd/system/qwamos-ai-*.service

# Reload systemd
sudo systemctl daemon-reload
```

---

**Version:** 0.6.0-alpha
**Last Updated:** 2025-11-04
**Status:** Phase 6 @ 85% (systemd services complete)
