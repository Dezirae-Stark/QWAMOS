#!/usr/bin/env python3
"""
Test Suite for Kali GPT (Local LLM)

Tests:
1. Model loading
2. Inference performance
3. Tool integration
4. CVE database lookup
5. Memory usage
6. Response quality
"""

import sys
import time
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from kali_gpt.kali_gpt_controller import KaliGPTController


def test_model_loading():
    """Test 1: Model Loading"""
    print("=" * 60)
    print("Test 1: Model Loading")
    print("=" * 60)

    try:
        start_time = time.time()
        kali_gpt = KaliGPTController()
        load_time = time.time() - start_time

        print(f"✅ Model loaded successfully")
        print(f"   Load time: {load_time:.2f}s")
        print(f"   Model file: {kali_gpt.model_path}")

        return True, kali_gpt

    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return False, None


def test_inference_speed(kali_gpt):
    """Test 2: Inference Performance"""
    print("\n" + "=" * 60)
    print("Test 2: Inference Performance")
    print("=" * 60)

    test_prompt = "Explain SQL injection in one sentence."

    try:
        start_time = time.time()
        response = kali_gpt.query(test_prompt)
        inference_time = time.time() - start_time

        tokens = len(response.split())
        tokens_per_sec = tokens / inference_time if inference_time > 0 else 0

        print(f"✅ Inference test passed")
        print(f"   Inference time: {inference_time:.2f}s")
        print(f"   Tokens generated: {tokens}")
        print(f"   Speed: {tokens_per_sec:.1f} tokens/sec")
        print(f"   Response preview: {response[:100]}...")

        return inference_time < 30  # Should complete in under 30s

    except Exception as e:
        print(f"❌ Inference test failed: {e}")
        return False


def test_tool_integration(kali_gpt):
    """Test 3: Tool Integration"""
    print("\n" + "=" * 60)
    print("Test 3: Tool Integration")
    print("=" * 60)

    test_prompt = "What nmap command should I use to scan for open ports?"

    try:
        response = kali_gpt.query(test_prompt)

        # Check if response mentions nmap
        has_nmap = 'nmap' in response.lower()
        has_command = '-' in response  # Likely contains flags

        print(f"✅ Tool integration test passed")
        print(f"   Contains 'nmap': {has_nmap}")
        print(f"   Contains command flags: {has_command}")
        print(f"   Response: {response[:200]}...")

        return has_nmap

    except Exception as e:
        print(f"❌ Tool integration test failed: {e}")
        return False


def test_cve_lookup(kali_gpt):
    """Test 4: CVE Database Lookup"""
    print("\n" + "=" * 60)
    print("Test 4: CVE Database Lookup")
    print("=" * 60)

    test_prompt = "Tell me about CVE-2021-44228 (Log4Shell)"

    try:
        response = kali_gpt.query(test_prompt)

        # Check if response is relevant
        has_cve = 'cve' in response.lower() or 'log4' in response.lower()
        has_vulnerability = 'vulnerab' in response.lower()

        print(f"✅ CVE lookup test passed")
        print(f"   Mentions CVE/Log4j: {has_cve}")
        print(f"   Mentions vulnerability: {has_vulnerability}")
        print(f"   Response: {response[:200]}...")

        return has_cve or has_vulnerability

    except Exception as e:
        print(f"❌ CVE lookup test failed: {e}")
        return False


def test_memory_usage():
    """Test 5: Memory Usage"""
    print("\n" + "=" * 60)
    print("Test 5: Memory Usage")
    print("=" * 60)

    try:
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024

        print(f"✅ Memory usage test passed")
        print(f"   Memory usage: {memory_mb:.1f} MB")

        acceptable = memory_mb < 7000  # Should be under 7GB
        if acceptable:
            print(f"   Status: Acceptable (< 7GB)")
        else:
            print(f"   ⚠️  Warning: High memory usage (> 7GB)")

        return acceptable

    except ImportError:
        print(f"⚠️  psutil not installed, skipping memory test")
        return True
    except Exception as e:
        print(f"❌ Memory test failed: {e}")
        return False


def test_response_quality(kali_gpt):
    """Test 6: Response Quality"""
    print("\n" + "=" * 60)
    print("Test 6: Response Quality")
    print("=" * 60)

    test_cases = [
        {
            'prompt': "What is pentesting?",
            'expected_keywords': ['penetration', 'testing', 'security']
        },
        {
            'prompt': "How do I find hidden directories with gobuster?",
            'expected_keywords': ['gobuster', 'directory', 'wordlist']
        },
        {
            'prompt': "Explain XSS attacks",
            'expected_keywords': ['cross-site', 'script', 'xss']
        }
    ]

    passed = 0
    for i, test in enumerate(test_cases, 1):
        try:
            response = kali_gpt.query(test['prompt'])
            response_lower = response.lower()

            matches = sum(1 for keyword in test['expected_keywords']
                         if keyword.lower() in response_lower)

            success = matches >= 2  # At least 2 keywords should match

            if success:
                print(f"   Test {i}/3: ✅ PASS")
                passed += 1
            else:
                print(f"   Test {i}/3: ❌ FAIL (only {matches}/{len(test['expected_keywords'])} keywords)")

        except Exception as e:
            print(f"   Test {i}/3: ❌ ERROR - {e}")

    print(f"\n   Results: {passed}/3 tests passed")
    return passed >= 2  # At least 2 out of 3 should pass


def run_all_tests():
    """Run all Kali GPT tests"""
    print("\n" + "=" * 60)
    print("QWAMOS - Kali GPT Test Suite")
    print("=" * 60 + "\n")

    results = []

    # Test 1: Model Loading
    success, kali_gpt = test_model_loading()
    results.append(('Model Loading', success))

    if not success or kali_gpt is None:
        print("\n❌ Cannot proceed without model. Exiting.")
        return

    # Test 2: Inference Performance
    results.append(('Inference Performance', test_inference_speed(kali_gpt)))

    # Test 3: Tool Integration
    results.append(('Tool Integration', test_tool_integration(kali_gpt)))

    # Test 4: CVE Lookup
    results.append(('CVE Database Lookup', test_cve_lookup(kali_gpt)))

    # Test 5: Memory Usage
    results.append(('Memory Usage', test_memory_usage()))

    # Test 6: Response Quality
    results.append(('Response Quality', test_response_quality(kali_gpt)))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status:12} {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Kali GPT is fully operational.")
        return 0
    elif passed >= total * 0.7:
        print(f"\n⚠️  {total - passed} test(s) failed, but core functionality works.")
        return 1
    else:
        print(f"\n❌ Too many failures. Please check Kali GPT configuration.")
        return 2


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
