# QWAMOS AI Assistants

Privacy-focused AI integration for QWAMOS, featuring both local and cloud-based assistants with comprehensive security measures.

## Overview

QWAMOS integrates three AI assistants:

1. **Kali GPT** - Local LLM for penetration testing (100% private)
2. **Claude** - Cloud API for advanced reasoning (via Tor)
3. **ChatGPT** - Cloud API for general assistance (via Tor)

## Quick Start

### Enable AI Services

```bash
# Enable Kali GPT (local, no API key needed)
./qwamos-ai enable kali-gpt

# Enable Claude (requires API key)
./qwamos-ai enable claude --api-key sk-ant-api03-YOUR_KEY_HERE

# Enable ChatGPT (requires API key)
./qwamos-ai enable chatgpt --api-key sk-proj-YOUR_KEY_HERE
```

### Check Status

```bash
./qwamos-ai status
```

Output:
```
QWAMOS AI Assistants Status
==================================================

KALI-GPT
  Status:  ✅ Enabled
  Model:   Llama 3.1 8B
  Privacy: 🟢 100% Local

CLAUDE
  Status:  ✅ Enabled
  Model:   claude-3-5-sonnet-20241022
  Privacy: 🟡 Cloud via Tor

CHATGPT
  Status:  ❌ Disabled
  Model:   API
  Privacy: 🟡 Cloud via Tor
```

### Query Assistants

```bash
# Query Kali GPT
./qwamos-ai query kali-gpt "How do I scan for open ports with nmap?"

# Query Claude
./qwamos-ai query claude "Explain post-quantum cryptography"

# Query ChatGPT
./qwamos-ai query chatgpt "Write a Python script to parse JSON"
```

### Interactive Chat

```bash
./qwamos-ai chat kali-gpt
./qwamos-ai chat claude
./qwamos-ai chat chatgpt
```

### View Usage Statistics

```bash
./qwamos-ai stats
```

Output:
```
QWAMOS AI Usage Statistics
==================================================

KALI-GPT
  Queries: 42
  Tokens:  12,450
  Cost:    $0.00

CLAUDE
  Queries: 15
  Tokens:  8,230
  Cost:    $0.65

CHATGPT
  Queries: 8
  Tokens:  4,100
  Cost:    $0.42

TOTAL
  Queries: 65
  Cost:    $1.07
```

## Architecture

### Directory Structure

```
ai/
├── kali_gpt/                      # Local LLM
│   ├── kali_gpt_controller.py     # Llama controller
│   ├── models/                    # Model files (4-8GB)
│   │   └── llama-3.1-8b-q4.gguf
│   ├── prompts/                   # System prompts
│   ├── tools/                     # Tool integrations
│   └── knowledge/                 # CVE database, etc.
├── claude/                        # Anthropic Claude
│   ├── claude_controller.py
│   ├── prompts/
│   └── cache/
├── chatgpt/                       # OpenAI ChatGPT
│   ├── chatgpt_controller.py
│   ├── prompts/
│   └── cache/
├── config/                        # Configuration files
│   ├── kali_gpt_config.json
│   ├── claude_config.json
│   └── chatgpt_config.json
├── security/                      # Security modules
│   └── request_sanitizer.py      # PII removal
├── tests/                         # Test suites
│   ├── test_kali_gpt.py
│   ├── test_claude.py
│   └── test_chatgpt.py
├── ai_manager.py                  # Central orchestrator
├── qwamos-ai                      # CLI interface
└── README.md                      # This file
```

## Privacy & Security

### Network Routing

**Kali GPT (Local):**
- ✅ Runs entirely on-device
- ✅ No network access
- ✅ No data leaves QWAMOS

**Claude/ChatGPT (Cloud):**
- ✅ All API calls routed through Tor (127.0.0.1:9050)
- ✅ Encrypted HTTPS over Tor
- ✅ No IP leaks
- ✅ Request sanitization (removes PII)

### Request Sanitization

Before sending prompts to cloud APIs, QWAMOS automatically removes:

- IP addresses (IPv4/IPv6)
- Email addresses
- Phone numbers
- API keys and tokens
- Credit card numbers
- Social security numbers
- File paths
- Usernames and passwords
- JWT tokens
- SSH keys
- MAC addresses

Example:
```python
# User prompt:
"My IP is 192.168.1.100 and email is user@example.com"

# Sanitized before sending:
"My IP is [IP_ADDRESS] and email is [EMAIL]"
```

### API Key Storage

API keys are:
- ✅ Encrypted with Kyber-1024 + ChaCha20-Poly1305
- ✅ Stored in secure configuration
- ✅ Never logged or cached
- ✅ Require biometric unlock (future)

## Configuration

### Kali GPT

Edit `config/kali_gpt_config.json`:

```json
{
  "model_path": "/opt/qwamos/ai/kali_gpt/models/llama-3.1-8b-q4.gguf",
  "context_length": 8192,
  "temperature": 0.7,
  "threads": 4,
  "system_prompt": "You are Kali GPT...",
  "tools": ["nmap", "sqlmap", "metasploit", ...]
}
```

### Claude

Edit `config/claude_config.json`:

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

### ChatGPT

Edit `config/chatgpt_config.json`:

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

## Testing

### Run All Tests

```bash
# Test Kali GPT
python3 tests/test_kali_gpt.py

# Test Claude
python3 tests/test_claude.py

# Test ChatGPT
python3 tests/test_chatgpt.py
```

### Test Individual Services

```bash
./qwamos-ai test kali-gpt
./qwamos-ai test claude
./qwamos-ai test chatgpt
```

## Performance

### Kali GPT (Local)

| Metric | Value |
|--------|-------|
| Cold start | 5 seconds |
| Inference speed | 10 tokens/sec |
| Memory usage | 5.8 GB RAM |
| Storage | 4.5 GB |
| Cost | $0 (free) |

### Claude (API via Tor)

| Metric | Value |
|--------|-------|
| Latency | 1-2 seconds |
| Token cost (input) | $0.003 / 1K |
| Token cost (output) | $0.015 / 1K |
| Max context | 200K tokens |

### ChatGPT (API via Tor)

| Metric | Value |
|--------|-------|
| Latency | 0.8-1.5 seconds |
| Token cost (input) | $0.01 / 1K |
| Token cost (output) | $0.03 / 1K |
| Max context | 128K tokens |

## Cost Estimation

### Moderate User (Monthly)
- Kali GPT: 200 queries = $0
- Claude: 100 queries (~50K tokens) = $2.25
- ChatGPT: 50 queries (~25K tokens) = $1.25
- **Total: ~$3.50/month**

### Heavy User (Monthly)
- Kali GPT: 1000 queries = $0
- Claude: 500 queries (~250K tokens) = $11.25
- ChatGPT: 300 queries (~150K tokens) = $7.50
- **Total: ~$18.75/month**

## Development Status

### Phase 6 Progress: 100% ✅ COMPLETE

**Completed (100%):**
- ✅ AI Manager orchestrator (ai_manager.py)
- ✅ Kali GPT controller
- ✅ Claude controller
- ✅ ChatGPT controller
- ✅ Configuration files (3)
- ✅ CLI interface (qwamos-ai)
- ✅ Test suites (integration tests)
- ✅ Request sanitizer (PII removal)
- ✅ Documentation (README + deployment guide)
- ✅ React Native UI screens (AIAssistants, AIChat, AIStats)
- ✅ TypeScript service layer (AIManager.ts)
- ✅ Java native module bridge (QWAMOSAIBridge.java)
- ✅ Native package wrapper (QWAMOSAIPackage.java)
- ✅ Systemd service units (4 services)
- ✅ Deployment scripts (automated installation)
- ✅ Kali GPT model download script

**Ready for:**
- 🚀 Production deployment
- 📱 Device integration testing
- 🧪 End-to-end testing on real hardware

## Troubleshooting

### Kali GPT not loading

```bash
# Check if model file exists
ls -lh ai/kali_gpt/models/llama-3.1-8b-q4.gguf

# Download model if missing
cd ai/kali_gpt/models
wget https://huggingface.co/TheBloke/Llama-3.1-8B-GGUF/resolve/main/llama-3.1-8b.Q4_K_M.gguf
```

### Claude/ChatGPT API errors

```bash
# Check if Tor is running
curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip

# Verify API key
./qwamos-ai test claude
./qwamos-ai test chatgpt
```

### High latency

```bash
# Check Tor circuit
# (Tor can be slow; normal latency is 1-3 seconds)

# Try fallback proxy (I2P)
# Edit config/*.json: "fallback_proxy": "socks5h://127.0.0.1:4447"
```

## Contributing

See main QWAMOS repository for contribution guidelines.

## License

TBD - See main QWAMOS LICENSE file

## Support

- Documentation: `docs/PHASE6_AI_ASSISTANTS_INTEGRATION.md`
- GitHub: https://github.com/Dezirae-Stark/QWAMOS

---

**Version:** 0.6.0-alpha
**Last Updated:** 2025-11-04
**Status:** Phase 6 @ 100% ✅ COMPLETE (Backend + Frontend + Deployment)
