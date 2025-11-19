# QWAMOS Nightly Security Scan Report

**Date**: 2025-11-19T03:51:14+00:00
**Workflow Run**: 19489060805
**Commit**: 65a941a75bd8e60208bc18cdb10256a9f0e01306

---

## Executive Summary

| Test Suite | Status |
|------------|--------|
| Static Analysis | success |
| Gateway Security | success |
| VM Isolation | success |
| Post-Quantum Crypto | success |

## 1. Static Analysis Results

### CodeQL Analysis
- Status: Completed
- View detailed results in GitHub Security tab

### Bandit (Python Security)
```
Run started:2025-11-19 03:49:01.995364+00:00

Test results:
>> Issue: [B108:hardcoded_tmp_directory] Probable insecure usage of temp file/directory.
   Severity: Medium   Confidence: Medium
   CWE: CWE-377 (https://cwe.mitre.org/data/definitions/377.html)
   More Info: https://bandit.readthedocs.io/en/1.9.1/plugins/b108_hardcoded_tmp_directory.html
   Location: ./ai/tests/test_ai_integration.py:317:27
316	            controller = KaliGPTController(
317	                model_path='/tmp/test_model.gguf'
318	            )

--------------------------------------------------
>> Issue: [B413:blacklist] The pyCrypto library and its module ECC are no longer actively maintained and have been deprecated. Consider using pyca/cryptography library.
   Severity: High   Confidence: High
   CWE: CWE-327 (https://cwe.mitre.org/data/definitions/327.html)
   More Info: https://bandit.readthedocs.io/en/1.9.1/blacklists/blacklist_imports.html#b413-import-pycrypto
   Location: ./cluster/cluster_node.py:194:8
193	        # For now, use ECDH (Curve25519) via secrets
194	        from Crypto.PublicKey import ECC
195	

--------------------------------------------------
>> Issue: [B413:blacklist] The pyCrypto library and its module SHA256 are no longer actively maintained and have been deprecated. Consider using pyca/cryptography library.
   Severity: High   Confidence: High
   CWE: CWE-327 (https://cwe.mitre.org/data/definitions/327.html)
   More Info: https://bandit.readthedocs.io/en/1.9.1/blacklists/blacklist_imports.html#b413-import-pycrypto
   Location: ./crypto/pqc_advanced.py:39:0
38	
39	from Crypto.Hash import SHA256, SHA3_256
```

### Semgrep (Security Rules)
```
                    
                    
┌──────────────────┐
│ 56 Code Findings │
└──────────────────┘
                                            
    .github/workflows/project-automation.yml
   ❯❯❱ yaml.github-actions.security.run-shell-injection.run-shell-injection
          Using variable interpolation `${{...}}` with `github` context data in a `run:` step could allow an  
          attacker to inject their own code into the runner. This would allow them to steal secrets and code. 
          `github` context data can have arbitrary user input and should be treated as untrusted. Instead, use
          an intermediate environment variable with `env:` to store the data and use the environment variable 
          in the `run:` script. Be sure to use double-quotes the environment variable, like this: "$ENVVAR".  
          Details: https://sg.run/pkzk                                                                        
                                                                                                              
          488┆ run: |
          489┆   echo "## 🤖 Project Board Automation Summary" >> $GITHUB_STEP_SUMMARY
          490┆   echo "" >> $GITHUB_STEP_SUMMARY
          491┆   echo "**Event:** ${{ github.event_name }}" >> $GITHUB_STEP_SUMMARY
          492┆   echo "**Action:** ${{ github.event.action }}" >> $GITHUB_STEP_SUMMARY
          493┆
          494┆   if [ "${{ github.event_name }}" == "issues" ]; then
          495┆     echo "**Issue:** #${{ github.event.issue.number }}" >> $GITHUB_STEP_SUMMARY
          496┆     echo "**Title:** ${{ github.event.issue.title }}" >> $GITHUB_STEP_SUMMARY
          497┆   elif [ "${{ github.event_name }}" == "pull_request" ] || [ "${{ github.event_name }}" ==
               "pull_request_review" ]; then                                                             
             [hid 15 additional lines, adjust with --max-lines-per-finding] 
                                           
    .github/workflows/release-generator.yml
   ❯❯❱ yaml.github-actions.security.run-shell-injection.run-shell-injection
```

## 2. Gateway Security Test Results

```
QWAMOS Gateway Security Tests
=============================
Timestamp: 2025-11-19T03:47:00+00:00

Test 1: Tor Connectivity
------------------------
✓ PASS: Tor SOCKS port (9050) is accessible
```

## 3. VM Isolation Test Results

```
QWAMOS VM Isolation Security Tests
===================================
Timestamp: 2025-11-19T03:47:02+00:00

Test 1: Filesystem Isolation
----------------------------
Testing QEMU filesystem isolation...
⚠ WARN: QEMU VM rootfs not found (may not be built yet)
```

## 4. Post-Quantum Cryptography Test Results

```
QWAMOS Post-Quantum Cryptography Security Tests
==================================================
Timestamp: 2025-11-19T03:48:55.522315

Test 1: Kyber-1024 Key Generation
----------------------------------------
⚠ WARN: liboqs Python bindings not available
  Testing with mock validation...
✓ PASS: liboqs source code present

Test 2: Kyber + ChaCha20-Poly1305 Wrapping
----------------------------------------
✓ PASS: ChaCha20-Poly1305 encryption/decryption successful
  Ciphertext size: 16 bytes
  Tag size: 16 bytes

Test 3: No Weak Crypto Fallback
----------------------------------------
⚠ WARN: Found potential weak crypto usage:
  AES: 3 file(s)
    - ./ai_app_builder/qa/quality_assurance.py
    - ./ai_app_builder/auditor/security/security_auditor.py
    - ./keyboard/crypto/pq_keystore_service.py
✓ PASS: Kyber usage found in 23 file(s)

==================================================
PQC Security Test Summary
==================================================
Passed: 3/3
Failed: 0/3

Result: PASSED
```

## Artifacts

Detailed reports available as workflow artifacts:
- Static Analysis Reports
- Gateway Security Reports
- VM Isolation Reports
- PQC Security Reports

---

*Report generated by QWAMOS Nightly Security Scan*
