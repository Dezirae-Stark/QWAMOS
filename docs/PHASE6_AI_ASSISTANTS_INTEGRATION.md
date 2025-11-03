# QWAMOS Phase 6 - AI Assistants Integration

## Overview

Integration of three AI assistants into QWAMOS as optional, privacy-focused services that can be toggled on/off via UI and CLI.

**Date:** 2025-11-03
**Status:** Phase 6 @ 0% → 30%
**Integration Type:** Optional services with local/cloud hybrid architecture

---

## Three AI Assistants

### 1. Kali GPT (Local LLM - Pentesting)
**Purpose:** On-device AI pentesting assistant
**Model:** Llama 3.1 8B (quantized for mobile)
**Privacy:** 100% local, no cloud dependency
**Use Cases:**
- Security testing guidance
- CVE database queries
- Exploit suggestions
- Tool automation (nmap, sqlmap, metasploit, burpsuite)
- Report generation

### 2. Claude (Anthropic API - General Purpose)
**Purpose:** Advanced reasoning and coding assistant
**Model:** Claude 3.5 Sonnet (API)
**Privacy:** Cloud-based, encrypted API calls via Tor
**Use Cases:**
- Complex problem solving
- Code analysis and generation
- System architecture design
- Technical documentation
- Long-form reasoning tasks

### 3. ChatGPT (OpenAI API - General Purpose)
**Purpose:** Versatile AI assistant
**Model:** GPT-4 Turbo (API)
**Privacy:** Cloud-based, encrypted API calls via Tor
**Use Cases:**
- General assistance
- Quick Q&A
- Text generation
- Summarization
- Creative tasks

---

## Architecture

### Directory Structure

```
ai/
├── kali_gpt/                      # Local LLM
│   ├── kali_gpt_controller.py     # Llama controller
│   ├── models/                    # Model files (4-8GB)
│   │   └── llama-3.1-8b-q4.gguf  # Quantized model
│   ├── prompts/                   # System prompts
│   │   ├── pentesting.txt
│   │   ├── cve_lookup.txt
│   │   └── tool_usage.txt
│   ├── tools/                     # Tool integrations
│   │   ├── nmap_integration.py
│   │   ├── sqlmap_integration.py
│   │   ├── metasploit_integration.py
│   │   └── burpsuite_integration.py
│   └── knowledge/                 # Knowledge bases
│       ├── cve_database.json
│       └── exploitdb_index.json
├── claude/                        # Anthropic Claude
│   ├── claude_controller.py       # API controller
│   ├── prompts/
│   │   ├── system.txt
│   │   ├── coding.txt
│   │   └── analysis.txt
│   └── cache/                     # Response cache
│       └── .gitignore
├── chatgpt/                       # OpenAI ChatGPT
│   ├── chatgpt_controller.py      # API controller
│   ├── prompts/
│   │   ├── system.txt
│   │   └── assistant.txt
│   └── cache/
│       └── .gitignore
├── ai_manager.py                  # Central AI orchestrator
├── config/
│   ├── kali_gpt_config.json       # Model settings
│   ├── claude_config.json         # API settings
│   └── chatgpt_config.json        # API settings
└── tests/
    ├── test_kali_gpt.py
    ├── test_claude.py
    └── test_chatgpt.py
```

---

## Privacy & Security Model

### Network Routing

**Kali GPT (Local):**
```
User → QWAMOS → Kali GPT (localhost)
✅ No network access
✅ 100% private
✅ No API keys required
```

**Claude/ChatGPT (Cloud):**
```
User → QWAMOS → Tor/I2P → VPN → API
✅ Multi-hop anonymization
✅ Encrypted API calls (HTTPS over Tor)
✅ No IP leaks
✅ Optional: Request sanitization
```

### API Key Management

**Storage:** TEE (TrustZone/StrongBox)
```python
# Keys encrypted with Kyber-1024 + ChaCha20
{
  "claude_api_key": "sk-ant-...",  # Encrypted
  "openai_api_key": "sk-proj-...", # Encrypted
  "encryption": "kyber1024+chacha20poly1305"
}
```

**Access Control:**
- Biometric unlock required
- Keys never stored in plaintext
- Auto-lock after 5 minutes idle
- Wipe on panic gesture

---

## Implementation: AI Manager

### File: `ai/ai_manager.py`

**Purpose:** Central orchestrator for all AI services

**Features:**
- Service registration and discovery
- Toggle individual assistants on/off
- Route queries to appropriate assistant
- Context management
- Usage tracking
- Cost monitoring (for API services)

**Key Methods:**
```python
class AIManager:
    def enable_kali_gpt(self)
    def enable_claude(self, api_key: str)
    def enable_chatgpt(self, api_key: str)

    def disable_kali_gpt(self)
    def disable_claude(self)
    def disable_chatgpt(self)

    def query(self, service: str, prompt: str, context: dict)
    def get_status(self) -> dict
    def get_usage_stats(self) -> dict
```

---

## Implementation: Kali GPT (Local LLM)

### File: `ai/kali_gpt/kali_gpt_controller.py`

**Model:** Llama 3.1 8B (4-bit quantized, ~4.5GB)
**Backend:** llama.cpp (optimized for ARM64)

**Features:**
1. **Pentesting Guidance**
   - Scan target analysis
   - Vulnerability assessment
   - Exploit recommendations
   - Post-exploitation strategies

2. **Tool Integration**
   ```python
   # Example: Automated nmap scan analysis
   kali_gpt.analyze_nmap_results("/tmp/scan.xml")

   # Output:
   # - Open ports analysis
   # - Service version vulnerabilities
   # - Recommended exploits
   # - Next steps
   ```

3. **CVE Database**
   - Offline CVE lookup (2020-2025)
   - CVSS score interpretation
   - Patch availability
   - Exploit code links

4. **Report Generation**
   ```python
   kali_gpt.generate_report({
       "target": "192.168.1.100",
       "scans": [...],
       "findings": [...],
       "recommendations": [...]
   })
   ```

**Performance:**
- Inference speed: ~10 tokens/sec (ARM64)
- Memory usage: 5-6GB RAM
- Cold start: ~5 seconds
- Warm inference: ~500ms per query

---

## Implementation: Claude Integration

### File: `ai/claude/claude_controller.py`

**API:** Anthropic Claude 3.5 Sonnet
**Endpoint:** https://api.anthropic.com/v1/messages

**Features:**
1. **Advanced Reasoning**
   - Complex problem decomposition
   - Multi-step analysis
   - Code review and generation
   - System design

2. **Privacy-Enhanced Requests**
   ```python
   # Route through Tor
   session = requests.Session()
   session.proxies = {
       'http': 'socks5h://127.0.0.1:9050',
       'https': 'socks5h://127.0.0.1:9050'
   }

   # Optional: Sanitize requests
   sanitized_prompt = remove_pii(user_prompt)

   response = claude.query(sanitized_prompt)
   ```

3. **Context Management**
   - Conversation history (local storage)
   - System prompts for QWAMOS context
   - Token usage tracking
   - Cost estimation

4. **Streaming Responses**
   ```python
   for chunk in claude.stream_query(prompt):
       print(chunk, end='', flush=True)
   ```

**API Configuration:**
```json
{
  "model": "claude-3-5-sonnet-20241022",
  "max_tokens": 4096,
  "temperature": 0.7,
  "routing": "tor",
  "cache_responses": true,
  "sanitize_requests": true
}
```

---

## Implementation: ChatGPT Integration

### File: `ai/chatgpt/chatgpt_controller.py`

**API:** OpenAI GPT-4 Turbo
**Endpoint:** https://api.openai.com/v1/chat/completions

**Features:**
1. **Versatile Assistance**
   - Quick answers
   - Code snippets
   - Explanations
   - Brainstorming

2. **Function Calling**
   ```python
   # Example: Execute terminal commands
   chatgpt.query("Run nmap scan on 192.168.1.1",
                 functions=[execute_command])

   # ChatGPT responds with function call:
   # execute_command("nmap -sV 192.168.1.1")
   ```

3. **Image Analysis** (GPT-4 Vision)
   ```python
   # Analyze screenshots
   chatgpt.analyze_image("/sdcard/screenshot.png",
                         "What vulnerabilities do you see?")
   ```

4. **Code Interpreter**
   - Python code execution in sandbox
   - Data analysis
   - Visualization generation

**API Configuration:**
```json
{
  "model": "gpt-4-turbo-preview",
  "max_tokens": 4096,
  "temperature": 0.7,
  "routing": "tor",
  "functions": ["execute_command", "read_file", "analyze_scan"]
}
```

---

## CLI Interface

### Command: `qwamos-ai`

**Usage:**
```bash
# Enable/disable services
qwamos-ai enable kali-gpt
qwamos-ai enable claude --api-key sk-ant-...
qwamos-ai enable chatgpt --api-key sk-proj-...

qwamos-ai disable kali-gpt
qwamos-ai disable claude
qwamos-ai disable chatgpt

# Check status
qwamos-ai status
# Output:
# Kali GPT:  ✅ Enabled (local)
# Claude:    ✅ Enabled (API, Tor routing)
# ChatGPT:   ❌ Disabled

# Query assistants
qwamos-ai query kali-gpt "Analyze nmap scan results"
qwamos-ai query claude "Explain this code: $(cat script.py)"
qwamos-ai query chatgpt "Summarize this log file"

# Interactive mode
qwamos-ai chat kali-gpt
qwamos-ai chat claude
qwamos-ai chat chatgpt

# Usage stats
qwamos-ai stats
# Output:
# Kali GPT:  150 queries, 0 cost
# Claude:    45 queries, $2.35
# ChatGPT:   30 queries, $1.80
```

---

## React Native UI Integration

### New Screens

**1. AI Assistants Screen** (`ui/screens/AIAssistants.tsx`)

```typescript
interface AIAssistantsScreenProps {}

const AIAssistantsScreen: React.FC<AIAssistantsScreenProps> = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>AI Assistants</Text>

      {/* Kali GPT Card */}
      <AIServiceCard
        name="Kali GPT"
        description="Local pentesting assistant"
        icon="shield-lock"
        status={kaliGptStatus}
        onToggle={toggleKaliGpt}
        privacy="🟢 100% Local"
      />

      {/* Claude Card */}
      <AIServiceCard
        name="Claude"
        description="Advanced reasoning assistant"
        icon="brain"
        status={claudeStatus}
        onToggle={toggleClaude}
        privacy="🟡 Cloud via Tor"
        requiresApiKey={true}
      />

      {/* ChatGPT Card */}
      <AIServiceCard
        name="ChatGPT"
        description="General purpose assistant"
        icon="comment-dots"
        status={chatGptStatus}
        onToggle={toggleChatGpt}
        privacy="🟡 Cloud via Tor"
        requiresApiKey={true}
      />

      {/* Usage Stats */}
      <UsageStatsCard stats={usageStats} />
    </View>
  );
};
```

**2. AI Chat Screen** (`ui/screens/AIChat.tsx`)

```typescript
interface AIChatScreenProps {
  service: 'kali-gpt' | 'claude' | 'chatgpt';
}

const AIChatScreen: React.FC<AIChatScreenProps> = ({ service }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');

  const sendMessage = async () => {
    const response = await AIManager.query(service, input);
    setMessages([...messages,
      { role: 'user', content: input },
      { role: 'assistant', content: response }
    ]);
  };

  return (
    <View style={styles.container}>
      <ChatHeader service={service} />
      <MessageList messages={messages} />
      <ChatInput
        value={input}
        onChangeText={setInput}
        onSend={sendMessage}
      />
    </View>
  );
};
```

### UI Components

**1. AIServiceCard** (`ui/components/AIServiceCard.tsx`)
- Service name and icon
- Status indicator (enabled/disabled)
- Toggle switch
- Privacy level badge
- "Open Chat" button
- API key input (if required)

**2. ChatMessage** (`ui/components/ChatMessage.tsx`)
- User/assistant differentiation
- Markdown rendering
- Code syntax highlighting
- Copy to clipboard
- Timestamp

**3. UsageStatsCard** (`ui/components/UsageStatsCard.tsx`)
- Query counts per service
- API costs (Claude, ChatGPT)
- Token usage
- Response time averages

---

## Configuration Files

### `ai/config/kali_gpt_config.json`

```json
{
  "model_path": "/opt/qwamos/ai/kali_gpt/models/llama-3.1-8b-q4.gguf",
  "context_length": 8192,
  "temperature": 0.7,
  "top_p": 0.9,
  "threads": 4,
  "gpu_layers": 0,
  "system_prompt": "You are Kali GPT, an expert penetration testing assistant...",
  "tools": [
    "nmap",
    "sqlmap",
    "metasploit",
    "burpsuite",
    "nikto",
    "gobuster"
  ],
  "knowledge_bases": [
    "cve_database",
    "exploitdb"
  ]
}
```

### `ai/config/claude_config.json`

```json
{
  "api_endpoint": "https://api.anthropic.com/v1/messages",
  "model": "claude-3-5-sonnet-20241022",
  "max_tokens": 4096,
  "temperature": 0.7,
  "routing": {
    "method": "tor",
    "proxy": "socks5h://127.0.0.1:9050",
    "verify_ssl": true
  },
  "privacy": {
    "sanitize_requests": true,
    "cache_locally": true,
    "log_queries": false
  },
  "cost_limits": {
    "max_monthly_cost": 50.00,
    "alert_threshold": 40.00
  }
}
```

### `ai/config/chatgpt_config.json`

```json
{
  "api_endpoint": "https://api.openai.com/v1/chat/completions",
  "model": "gpt-4-turbo-preview",
  "max_tokens": 4096,
  "temperature": 0.7,
  "routing": {
    "method": "tor",
    "proxy": "socks5h://127.0.0.1:9050",
    "verify_ssl": true
  },
  "features": {
    "function_calling": true,
    "vision": true,
    "code_interpreter": false
  },
  "cost_limits": {
    "max_monthly_cost": 50.00,
    "alert_threshold": 40.00
  }
}
```

---

## Security Considerations

### 1. API Key Protection
- ✅ Stored in TEE (TrustZone/StrongBox)
- ✅ Encrypted with Kyber-1024 + ChaCha20
- ✅ Require biometric unlock
- ✅ Auto-wipe on panic gesture
- ✅ Never logged or cached

### 2. Request Sanitization
```python
def sanitize_request(prompt: str) -> str:
    """Remove PII and sensitive data from prompts"""
    # Remove IP addresses
    prompt = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
                    '[IP_REDACTED]', prompt)

    # Remove API keys
    prompt = re.sub(r'sk-[a-zA-Z0-9]{48}', '[API_KEY]', prompt)

    # Remove email addresses
    prompt = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                    '[EMAIL]', prompt)

    # Remove phone numbers
    prompt = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                    '[PHONE]', prompt)

    return prompt
```

### 3. Network Isolation
- ✅ Claude/ChatGPT only accessible via Tor
- ✅ Kali GPT has no network access
- ✅ DNS over Tor for API resolution
- ✅ Kill switch prevents API leaks

### 4. Response Validation
```python
def validate_response(response: dict) -> bool:
    """Ensure API responses are safe"""
    # Check for malicious code injection
    if contains_suspicious_patterns(response['content']):
        return False

    # Verify response signature (if available)
    if not verify_response_integrity(response):
        return False

    return True
```

---

## Installation & Setup

### 1. Install Kali GPT (Local)

```bash
# Download Llama 3.1 8B model (4.5GB)
cd ~/QWAMOS/ai/kali_gpt/models
wget https://huggingface.co/TheBloke/Llama-3.1-8B-GGUF/resolve/main/llama-3.1-8b.Q4_K_M.gguf

# Install llama.cpp
pkg install clang cmake
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build

# Test model
./build/bin/main -m ../ai/kali_gpt/models/llama-3.1-8b.Q4_K_M.gguf \
                 -p "You are a pentesting assistant. Explain SQL injection." \
                 -n 128
```

### 2. Configure Claude

```bash
# Set API key (encrypted storage)
qwamos-ai enable claude --api-key sk-ant-api03-YOUR_KEY_HERE

# Test connection
qwamos-ai query claude "Hello, can you hear me?"
```

### 3. Configure ChatGPT

```bash
# Set API key
qwamos-ai enable chatgpt --api-key sk-proj-YOUR_KEY_HERE

# Test connection
qwamos-ai query chatgpt "Hello, test message"
```

---

## Testing

### Test 1: Kali GPT Inference
```bash
cd ~/QWAMOS/ai/tests
python3 test_kali_gpt.py
```

**Expected:**
```
✅ Model loaded successfully (4.5GB)
✅ Inference test passed (10 tokens/sec)
✅ CVE lookup functional
✅ Tool integration working
✅ Memory usage acceptable (5.8GB)
```

### Test 2: Claude API
```bash
python3 test_claude.py
```

**Expected:**
```
✅ API key validated
✅ Tor routing active
✅ Request successful (200 OK)
✅ Response received (1.2s latency)
✅ Token usage: 250 tokens
✅ Cost: $0.0025
```

### Test 3: ChatGPT API
```bash
python3 test_chatgpt.py
```

**Expected:**
```
✅ API key validated
✅ Tor routing active
✅ Request successful (200 OK)
✅ Response received (0.9s latency)
✅ Function calling enabled
✅ Token usage: 180 tokens
✅ Cost: $0.0018
```

---

## Performance Benchmarks

### Kali GPT (Local)
| Metric | Value |
|--------|-------|
| Cold start | 5 seconds |
| Inference speed | 10 tokens/sec |
| Memory usage | 5.8 GB RAM |
| Storage | 4.5 GB |
| Latency | ~500ms |
| Cost | $0 (free) |

### Claude (API)
| Metric | Value |
|--------|-------|
| Latency (via Tor) | 1-2 seconds |
| Token cost (input) | $0.003 / 1K |
| Token cost (output) | $0.015 / 1K |
| Max context | 200K tokens |
| Rate limit | 50 req/min |

### ChatGPT (API)
| Metric | Value |
|--------|-------|
| Latency (via Tor) | 0.8-1.5 seconds |
| Token cost (input) | $0.01 / 1K |
| Token cost (output) | $0.03 / 1K |
| Max context | 128K tokens |
| Rate limit | 10K req/min |

---

## Cost Estimation

### Monthly Usage Example

**Moderate User:**
- Kali GPT: 200 queries/month = $0
- Claude: 100 queries/month (~50K tokens) = $2.25
- ChatGPT: 50 queries/month (~25K tokens) = $1.25
- **Total: ~$3.50/month**

**Heavy User:**
- Kali GPT: 1000 queries/month = $0
- Claude: 500 queries/month (~250K tokens) = $11.25
- ChatGPT: 300 queries/month (~150K tokens) = $7.50
- **Total: ~$18.75/month**

---

## Timeline

### Phase 6a: AI Infrastructure (Week 1-2)
- Day 1-2: Create ai/ directory structure
- Day 3-4: Implement AIManager orchestrator
- Day 5-7: Kali GPT controller + llama.cpp integration
- Day 8-10: Claude controller + Tor routing
- Day 11-12: ChatGPT controller
- Day 13-14: Testing and bug fixes

### Phase 6b: UI Integration (Week 3)
- Day 15-16: AI Assistants screen
- Day 17-18: AI Chat screen
- Day 19-20: UI components (cards, messages)
- Day 21: Integration testing

### Phase 6c: Polish & Documentation (Week 4)
- Day 22-23: Performance optimization
- Day 24-25: Security hardening
- Day 26-27: User documentation
- Day 28: Final testing

**Total Estimated Time:** 4 weeks

---

## Success Criteria

✅ Kali GPT runs locally with <10s cold start
✅ Claude API calls route through Tor successfully
✅ ChatGPT API calls route through Tor successfully
✅ API keys stored securely in TEE
✅ No IP leaks during API calls
✅ UI allows toggling services on/off
✅ CLI interface functional
✅ Request sanitization working
✅ Cost tracking accurate
✅ All tests passing

---

## Future Enhancements

1. **Multi-Model Support**
   - Add Mistral, Gemini, LLaMA 3.2
   - Model switching within same assistant

2. **Voice Interface**
   - Speech-to-text input
   - Text-to-speech output
   - Conversation mode

3. **Context Sharing**
   - Share context between assistants
   - Collaborative problem solving

4. **Custom Fine-Tuning**
   - Fine-tune Kali GPT on user's pentest reports
   - Personalized responses

5. **Offline Mode**
   - Download Claude/GPT responses for offline viewing
   - Pre-cache common queries

---

**Document Version:** 1.0
**Status:** Draft
**Phase:** 6 @ 0% → 30% (with implementation)
**Last Updated:** 2025-11-03
