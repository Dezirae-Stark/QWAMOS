# Kali GPT Integration Specification

**Feature Owner:** QWAMOS Development Team
**Priority:** HIGH
**Target Phase:** Phase 5 (Months 18-20)
**Status:** PLANNED

---

## Overview

Integrate Kali GPT (Kali Linux's AI-powered penetration testing assistant) natively into the QWAMOS kali-vm, providing natural language interaction with security tools, automated vulnerability assessment, and intelligent pentesting guidance.

**Kali GPT** is an AI assistant specifically trained on:
- Penetration testing methodologies
- Kali Linux tool usage
- Security vulnerabilities and exploits
- Network security assessment
- Web application testing
- Social engineering techniques

---

## Architecture

### Current QWAMOS Kali Integration

```
kali-vm
    ├─> Kali Linux base system
    ├─> Penetration testing tools
    └─> Manual tool execution (command line)
```

### Enhanced with Kali GPT

```
kali-vm (ENHANCED)
    │
    ├─> Kali GPT Engine
    │   ├─> Natural language processing
    │   ├─> Tool command generation
    │   ├─> Vulnerability analysis
    │   └─> Report generation
    │
    ├─> QWAMOS UI Integration
    │   ├─> Chat interface (React Native)
    │   ├─> Voice commands (optional)
    │   ├─> Real-time suggestions
    │   └─> Interactive tutorials
    │
    ├─> Tool Automation
    │   ├─> Nmap scanner automation
    │   ├─> SQLmap injection testing
    │   ├─> Metasploit exploit selection
    │   └─> Burp Suite configuration
    │
    └─> Knowledge Base
        ├─> CVE database
        ├─> Exploit database (ExploitDB)
        ├─> OWASP Top 10
        └─> Pentesting playbooks
```

---

## Implementation Options

### Option 1: Cloud-Based Kali GPT (Easier)

**Architecture:**
```
QWAMOS kali-vm
    └─> Kali GPT Client
        └─> API calls → Kali GPT Cloud Service
            └─> Returns commands/analysis
```

**Pros:**
- No local AI model (smaller footprint)
- Always up-to-date with latest exploits
- Faster responses (powerful cloud GPUs)

**Cons:**
- Requires internet connection
- Privacy concerns (sending pentest data to cloud)
- Subscription cost

### Option 2: On-Device Kali GPT (Recommended)

**Architecture:**
```
QWAMOS kali-vm
    └─> Local LLM (Llama 3.1 8B quantized)
        └─> Fine-tuned on Kali/security data
            └─> Fully offline AI assistant
```

**Pros:**
- ✅ **Complete privacy** (no data leaves device)
- ✅ Works offline (critical for pentesting)
- ✅ No subscription costs
- ✅ Customizable for specific use cases

**Cons:**
- Requires 6-8GB RAM for kali-vm
- Initial model download (~5GB)
- Slightly slower inference on mobile

**Recommended:** **Option 2** for privacy and offline capability

---

## Technical Implementation

### 1. Local LLM Setup

**Model Selection:**
- **Llama 3.1 8B (Quantized Q4_K_M)** - Best balance of size/performance
- **Alternative:** Mistral 7B Instruct (faster, less accurate)

**Model Storage:**
```
kali-vm/opt/kali-gpt/
    ├─> models/
    │   ├─> llama-3.1-8b-kali-q4.gguf (5.2GB)
    │   └─> tokenizer.json
    ├─> prompts/
    │   ├─> system_prompt.txt
    │   └─> tool_templates/
    └─> knowledge/
        ├─> cve_database.json
        ├─> exploitdb_index.json
        └─> owasp_top10.json
```

**Inference Engine:**
- **llama.cpp** - Fast C++ inference for ARM64
- **Python bindings:** llama-cpp-python

```bash
# Install llama.cpp for ARM64
cd /opt/kali-gpt
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make -j$(nproc) LLAMA_OPENBLAS=1  # Use OpenBLAS for ARM optimization

# Install Python bindings
pip install llama-cpp-python
```

### 2. Fine-Tuning Data

**Training Dataset:**
```
kali-gpt-training-data/
    ├─> conversations/
    │   ├─> nmap_examples.jsonl
    │   ├─> sqlmap_examples.jsonl
    │   ├─> metasploit_examples.jsonl
    │   └─> burp_suite_examples.jsonl
    ├─> tool_docs/
    │   ├─> nmap_man_pages.txt
    │   ├─> metasploit_modules.txt
    │   └─> kali_tool_list.txt
    └─> vulnerabilities/
        ├─> cve_descriptions.jsonl
        └─> exploit_techniques.jsonl
```

**Example Training Conversation:**
```json
{
  "conversations": [
    {
      "human": "How do I scan a network for open ports?",
      "assistant": "To scan a network for open ports, use nmap:\n\n```bash\nnmap -sS -p- 192.168.1.0/24\n```\n\n- `-sS`: SYN scan (stealthy)\n- `-p-`: Scan all 65535 ports\n- `192.168.1.0/24`: Target network\n\nFor faster results, scan common ports only:\n```bash\nnmap -F 192.168.1.0/24\n```"
    },
    {
      "human": "I found port 80 and 443 open on 192.168.1.100. How do I test for SQL injection?",
      "assistant": "Use sqlmap to test for SQL injection:\n\n```bash\nsqlmap -u \"http://192.168.1.100/page.php?id=1\" --batch --dbs\n```\n\n- `-u`: Target URL\n- `--batch`: Automatic mode (no prompts)\n- `--dbs`: Enumerate databases\n\nIf injection is found, dump tables:\n```bash\nsqlmap -u \"http://192.168.1.100/page.php?id=1\" -D database_name --tables\n```"
    }
  ]
}
```

**Fine-Tuning Command:**
```bash
# Using LoRA (Low-Rank Adaptation) for efficient fine-tuning
python train_kali_gpt.py \
    --base_model llama-3.1-8b \
    --data_path kali-gpt-training-data/ \
    --output_dir models/llama-3.1-8b-kali \
    --lora_rank 8 \
    --num_epochs 3 \
    --batch_size 4
```

### 3. Kali GPT Python Service

```python
# /opt/kali-gpt/kali_gpt_service.py

from llama_cpp import Llama
import json
import re

class KaliGPT:
    def __init__(self):
        self.llm = Llama(
            model_path="/opt/kali-gpt/models/llama-3.1-8b-kali-q4.gguf",
            n_ctx=4096,  # Context window
            n_threads=4,  # CPU threads
            n_gpu_layers=0  # CPU-only for ARM
        )

        self.system_prompt = self._load_system_prompt()
        self.conversation_history = []

    def _load_system_prompt(self):
        return """You are Kali GPT, an expert penetration testing assistant.
You help security professionals use Kali Linux tools effectively.

Rules:
1. Provide accurate, working command examples
2. Explain tool options clearly
3. Warn about legal/ethical considerations
4. Suggest next steps in pentesting workflow
5. Output commands in markdown code blocks

Always emphasize: "Use only on systems you own or have permission to test."
"""

    def ask(self, question: str, context: dict = None) -> dict:
        """
        Ask Kali GPT a question

        Args:
            question: User's question
            context: Optional context (scan results, target info, etc.)

        Returns:
            {
                "response": "AI response text",
                "commands": ["extracted command 1", "command 2"],
                "tools": ["nmap", "sqlmap"],
                "next_steps": ["suggestion 1", "suggestion 2"]
            }
        """

        # Build prompt
        prompt = self._build_prompt(question, context)

        # Generate response
        response = self.llm(
            prompt,
            max_tokens=512,
            temperature=0.7,
            top_p=0.9,
            stop=["Human:", "\n\n\n"]
        )

        response_text = response['choices'][0]['text']

        # Parse response
        commands = self._extract_commands(response_text)
        tools = self._extract_tools(response_text)
        next_steps = self._extract_next_steps(response_text)

        return {
            "response": response_text,
            "commands": commands,
            "tools": tools,
            "next_steps": next_steps
        }

    def _build_prompt(self, question: str, context: dict = None) -> str:
        prompt = f"{self.system_prompt}\n\n"

        # Add conversation history
        for msg in self.conversation_history[-3:]:  # Last 3 messages
            prompt += f"Human: {msg['question']}\nAssistant: {msg['response']}\n\n"

        # Add context if provided
        if context:
            prompt += f"Context:\n{json.dumps(context, indent=2)}\n\n"

        prompt += f"Human: {question}\nAssistant:"

        return prompt

    def _extract_commands(self, text: str) -> list:
        """Extract shell commands from markdown code blocks"""
        commands = []
        pattern = r'```(?:bash|shell)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)

        for match in matches:
            # Split by lines, filter comments
            lines = [l.strip() for l in match.split('\n') if l.strip() and not l.strip().startswith('#')]
            commands.extend(lines)

        return commands

    def _extract_tools(self, text: str) -> list:
        """Identify tools mentioned in response"""
        tools = []
        tool_keywords = ['nmap', 'sqlmap', 'metasploit', 'msfconsole', 'burp',
                        'nikto', 'gobuster', 'hydra', 'john', 'aircrack']

        text_lower = text.lower()
        for tool in tool_keywords:
            if tool in text_lower:
                tools.append(tool)

        return list(set(tools))

    def _extract_next_steps(self, text: str) -> list:
        """Extract suggested next steps"""
        next_steps = []

        # Look for "Next:" or numbered lists
        if "Next:" in text or "next step" in text.lower():
            # Simple extraction (can be improved with better parsing)
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if 'next' in line.lower() and i + 1 < len(lines):
                    next_steps.append(lines[i + 1].strip())

        return next_steps

    def execute_command(self, command: str) -> dict:
        """
        Execute a suggested command and return results

        Args:
            command: Shell command to execute

        Returns:
            {
                "stdout": "command output",
                "stderr": "error output",
                "exit_code": 0
            }
        """
        import subprocess

        # Safety check - prompt user for confirmation
        print(f"⚠️  About to execute: {command}")
        print("   Press Enter to continue, Ctrl+C to cancel")
        input()

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }


# FastAPI service for QWAMOS UI
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
kali_gpt = KaliGPT()

class Question(BaseModel):
    question: str
    context: dict = None

@app.post("/api/kali-gpt/ask")
async def ask_kali_gpt(q: Question):
    try:
        response = kali_gpt.ask(q.question, q.context)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/kali-gpt/execute")
async def execute_command(command: str):
    try:
        result = kali_gpt.execute_command(command)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 4. React Native UI Integration

```typescript
// frontend/screens/KaliGPT.tsx

import React, { useState, useRef, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, ActivityIndicator } from 'react-native';
import { KaliGPTService } from '../services/kaliGPTService';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  commands?: string[];
  timestamp: Date;
}

const KaliGPTScreen = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollViewRef = useRef<ScrollView>(null);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await KaliGPTService.ask(input);

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response,
        commands: response.commands,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Auto-scroll to bottom
      setTimeout(() => {
        scrollViewRef.current?.scrollToEnd({ animated: true });
      }, 100);

    } catch (error) {
      console.error('Kali GPT error:', error);
      alert('Failed to get response from Kali GPT');
    } finally {
      setLoading(false);
    }
  };

  const executeCommand = async (command: string) => {
    try {
      setLoading(true);
      const result = await KaliGPTService.executeCommand(command);

      // Show command output
      const outputMessage: Message = {
        role: 'assistant',
        content: `Command executed:\n\`\`\`\n${command}\n\`\`\`\n\nOutput:\n\`\`\`\n${result.stdout}\n\`\`\``,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, outputMessage]);
    } catch (error) {
      alert('Command execution failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={{ flex: 1, backgroundColor: '#0a0e27' }}>
      {/* Header */}
      <View style={{ padding: 16, borderBottomWidth: 1, borderColor: '#1a1f3a' }}>
        <Text style={{ fontSize: 24, fontWeight: 'bold', color: '#00ffff' }}>
          🤖 Kali GPT Assistant
        </Text>
        <Text style={{ color: '#888', marginTop: 4 }}>
          AI-powered penetration testing guidance
        </Text>
      </View>

      {/* Chat Messages */}
      <ScrollView
        ref={scrollViewRef}
        style={{ flex: 1, padding: 16 }}
        contentContainerStyle={{ paddingBottom: 20 }}
      >
        {messages.map((msg, index) => (
          <View key={index} style={{
            marginBottom: 16,
            alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
            maxWidth: '85%'
          }}>
            <View style={{
              backgroundColor: msg.role === 'user' ? '#00ffff' : '#1a1f3a',
              padding: 12,
              borderRadius: 12
            }}>
              <Text style={{
                color: msg.role === 'user' ? '#000' : '#fff',
                fontSize: 15
              }}>
                {msg.content}
              </Text>

              {/* Command Buttons */}
              {msg.commands && msg.commands.length > 0 && (
                <View style={{ marginTop: 12 }}>
                  <Text style={{ color: '#00ff00', fontSize: 12, marginBottom: 8 }}>
                    Suggested commands:
                  </Text>
                  {msg.commands.map((cmd, idx) => (
                    <TouchableOpacity
                      key={idx}
                      onPress={() => executeCommand(cmd)}
                      style={{
                        backgroundColor: '#ff00ff',
                        padding: 8,
                        borderRadius: 6,
                        marginBottom: 6
                      }}
                    >
                      <Text style={{ color: '#fff', fontFamily: 'monospace', fontSize: 12 }}>
                        ▶ {cmd}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>
              )}
            </View>

            <Text style={{ color: '#666', fontSize: 10, marginTop: 4 }}>
              {msg.timestamp.toLocaleTimeString()}
            </Text>
          </View>
        ))}

        {loading && (
          <View style={{ alignItems: 'center', marginVertical: 20 }}>
            <ActivityIndicator size="large" color="#00ffff" />
            <Text style={{ color: '#888', marginTop: 8 }}>Thinking...</Text>
          </View>
        )}
      </ScrollView>

      {/* Input Box */}
      <View style={{
        padding: 16,
        borderTopWidth: 1,
        borderColor: '#1a1f3a',
        flexDirection: 'row',
        alignItems: 'center'
      }}>
        <TextInput
          value={input}
          onChangeText={setInput}
          placeholder="Ask Kali GPT anything..."
          placeholderTextColor="#666"
          style={{
            flex: 1,
            backgroundColor: '#1a1f3a',
            color: '#fff',
            padding: 12,
            borderRadius: 8,
            marginRight: 8,
            fontSize: 15
          }}
          multiline
          onSubmitEditing={sendMessage}
        />
        <TouchableOpacity
          onPress={sendMessage}
          disabled={loading || !input.trim()}
          style={{
            backgroundColor: input.trim() ? '#00ffff' : '#333',
            padding: 12,
            borderRadius: 8
          }}
        >
          <Text style={{ color: '#000', fontWeight: 'bold' }}>Send</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

export default KaliGPTScreen;
```

```typescript
// frontend/services/kaliGPTService.ts

import axios from 'axios';

const KALI_GPT_API = 'http://kali-vm.qwamos:8000/api/kali-gpt';

export class KaliGPTService {
  static async ask(question: string, context?: any) {
    const response = await axios.post(`${KALI_GPT_API}/ask`, {
      question,
      context
    });
    return response.data;
  }

  static async executeCommand(command: string) {
    const response = await axios.post(`${KALI_GPT_API}/execute`, {
      command
    });
    return response.data;
  }
}
```

---

## Example Use Cases

### Use Case 1: Network Reconnaissance

**User:** "I need to scan 192.168.1.0/24 for live hosts"

**Kali GPT Response:**
```
To discover live hosts on the network, use nmap with ping scan:

```bash
nmap -sn 192.168.1.0/24
```

- `-sn`: Ping scan (no port scan)
- Discovers hosts without being too noisy

For more detailed host discovery:
```bash
nmap -sS -sV -O 192.168.1.0/24
```

- `-sS`: SYN scan
- `-sV`: Service version detection
- `-O`: OS detection

**Next steps:**
1. Save scan results: `nmap -sS 192.168.1.0/24 -oN scan_results.txt`
2. Identify interesting hosts with open ports
3. Enumerate services on target hosts
```

**UI shows:**
- ▶ `nmap -sn 192.168.1.0/24` (tap to execute)
- ▶ `nmap -sS -sV -O 192.168.1.0/24` (tap to execute)

### Use Case 2: Web Application Testing

**User:** "Found a website at 192.168.1.50. How do I test for vulnerabilities?"

**Kali GPT Response:**
```
Here's a step-by-step approach to web app testing:

**Step 1: Reconnaissance**
```bash
whatweb http://192.168.1.50
```
Identifies CMS, frameworks, and technologies

**Step 2: Directory Enumeration**
```bash
gobuster dir -u http://192.168.1.50 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
```

**Step 3: Vulnerability Scanning**
```bash
nikto -h http://192.168.1.50
```

**Step 4: SQL Injection Testing**
```bash
sqlmap -u "http://192.168.1.50/page.php?id=1" --batch --risk=3 --level=5
```

**Important:** Ensure you have authorization before testing!
```

---

## Advanced Features

### 1. Context-Aware Suggestions

Kali GPT remembers conversation context:

```
User: "I found port 22 open on 192.168.1.100"
Kali GPT: "Port 22 is SSH. Let me help you enumerate it..."

User: "Also port 80"
Kali GPT: "Great! Port 80 is HTTP. Since you already have SSH (port 22)
           and HTTP (port 80) on 192.168.1.100, let's test both:

           For SSH: ssh-audit 192.168.1.100
           For HTTP: nikto -h http://192.168.1.100"
```

### 2. Vulnerability Database Integration

```python
def query_cve_database(service: str, version: str):
    """Query CVE database for known vulnerabilities"""
    cve_db = load_cve_database()
    vulns = cve_db.search(service=service, version=version)

    return {
        "vulnerabilities": vulns,
        "exploits": find_exploits(vulns),
        "mitigations": suggest_mitigations(vulns)
    }
```

**Example:**
```
User: "Nmap shows Apache 2.4.29 on the target"
Kali GPT: "Apache 2.4.29 has known vulnerabilities:

           🔴 CVE-2017-15710: Out of bounds write
           🟡 CVE-2018-1312: Authentication bypass

           Exploits available in Metasploit:
           - exploit/multi/http/apache_mod_cgi_bash_env_exec

           Suggested commands:
           msfconsole
           use exploit/multi/http/apache_mod_cgi_bash_env_exec
           set RHOST 192.168.1.100
           exploit"
```

### 3. Automated Report Generation

```python
def generate_pentest_report(conversation_history: list) -> str:
    """Generate professional penetration testing report"""

    report = {
        "executive_summary": summarize_findings(conversation_history),
        "methodology": extract_tools_used(conversation_history),
        "findings": parse_vulnerabilities(conversation_history),
        "recommendations": suggest_remediations(conversation_history)
    }

    return render_report_template(report)
```

---

## Security & Ethical Considerations

### 1. Authorization Checks

```python
def before_execution(command: str):
    """Warn user about authorization"""
    print("""
    ⚠️  IMPORTANT: Penetration Testing Authorization

    Executing: {command}

    You must have EXPLICIT WRITTEN PERMISSION to test this system.
    Unauthorized access is illegal under:
    - CFAA (Computer Fraud and Abuse Act) - USA
    - Computer Misuse Act - UK
    - And similar laws worldwide

    Do you have authorization? (yes/no): """.format(command=command))

    response = input().lower()
    if response != 'yes':
        print("❌ Command cancelled")
        exit(1)
```

### 2. Responsible Disclosure

Kali GPT includes guidance on responsible disclosure:

```
"Found a vulnerability? Here's how to report it responsibly:

1. Document the vulnerability (screenshots, PoC)
2. Contact the organization's security team
3. Give them 90 days to patch before public disclosure
4. Follow coordinated disclosure practices

Resources:
- CERT Coordination Center: https://www.kb.cert.org/vuls/
- HackerOne: https://www.hackerone.com/
```

---

## Performance Optimization

### 1. Model Quantization

For ARM mobile devices, use quantized models:

- **Q4_K_M:** 4-bit quantization (5.2GB, fast)
- **Q5_K_M:** 5-bit quantization (6.4GB, better accuracy)
- **Q8_0:** 8-bit quantization (8.5GB, best accuracy)

**Recommended:** Q4_K_M for mobile

### 2. Inference Optimization

```python
# Use llama.cpp with NEON optimizations for ARM
llm = Llama(
    model_path="model.gguf",
    n_ctx=4096,
    n_threads=4,  # Use 4 CPU threads
    n_batch=512,  # Batch size for faster inference
    use_mlock=True,  # Lock model in RAM
)
```

### 3. Response Caching

Cache common queries to reduce inference time:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_response(question: str) -> str:
    return kali_gpt.ask(question)
```

---

## Testing Strategy

### Unit Tests

```python
def test_nmap_command_generation():
    question = "How do I scan a network?"
    response = kali_gpt.ask(question)

    assert 'nmap' in response['tools']
    assert len(response['commands']) > 0
    assert 'nmap' in response['commands'][0]

def test_sqlmap_injection_testing():
    question = "Test for SQL injection on http://example.com/page.php?id=1"
    response = kali_gpt.ask(question)

    assert 'sqlmap' in response['tools']
    assert 'http://example.com/page.php?id=1' in response['commands'][0]
```

### Integration Tests

1. Test full pentesting workflow
2. Verify command execution
3. Test report generation
4. Validate vulnerability database queries

---

## Timeline

- **Month 18:** Set up local LLM, fine-tune on Kali data
- **Month 19:** Develop Python service, React Native UI
- **Month 20:** Testing, optimization, documentation

**Total:** 3 months

---

## Resources

- Llama 3.1 8B: https://huggingface.co/meta-llama/Meta-Llama-3.1-8B
- llama.cpp: https://github.com/ggerganov/llama.cpp
- Kali Linux Tools: https://www.kali.org/tools/
- ExploitDB: https://www.exploit-db.com/

---

**Status:** Ready for Implementation
**Next Steps:** Download and quantize Llama 3.1 8B model in Phase 5
