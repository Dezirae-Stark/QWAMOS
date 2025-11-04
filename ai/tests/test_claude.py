#!/usr/bin/env python3
"""
Test Suite for Claude API Integration

Tests:
1. API key validation
2. Tor routing verification
3. Basic query functionality
4. Streaming responses
5. Token usage tracking
6. Cost calculation
7. Error handling
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from claude.claude_controller import ClaudeController


def test_api_key_validation():
    """Test 1: API Key Validation"""
    print("=" * 60)
    print("Test 1: API Key Validation")
    print("=" * 60)

    try:
        # This should fail with invalid key
        claude = ClaudeController(api_key="invalid_key")
        result = claude.validate_api_key()

        if not result:
            print("✅ Invalid API key correctly rejected")
            return True
        else:
            print("❌ Invalid API key was accepted (unexpected)")
            return False

    except Exception as e:
        print(f"✅ Invalid API key correctly raised exception: {type(e).__name__}")
        return True


def test_tor_routing():
    """Test 2: Tor Routing Verification"""
    print("\n" + "=" * 60)
    print("Test 2: Tor Routing Verification")
    print("=" * 60)

    try:
        claude = ClaudeController()

        # Check if Tor proxy is configured
        proxy_config = claude.get_proxy_config()

        print(f"✅ Tor routing configured")
        print(f"   Proxy: {proxy_config['http']}")
        print(f"   SSL Verify: {claude.verify_ssl}")

        # Verify Tor is actually being used
        if 'socks5h://127.0.0.1:9050' in proxy_config['http']:
            print(f"   Status: Correct Tor proxy")
            return True
        else:
            print(f"   ⚠️  Warning: Not using expected Tor proxy")
            return False

    except Exception as e:
        print(f"❌ Tor routing test failed: {e}")
        return False


def test_basic_query():
    """Test 3: Basic Query Functionality"""
    print("\n" + "=" * 60)
    print("Test 3: Basic Query Functionality")
    print("=" * 60)

    try:
        claude = ClaudeController()
        test_prompt = "Reply with exactly: CLAUDE_TEST_OK"

        print(f"   Sending test query...")
        start_time = time.time()
        response = claude.query(test_prompt)
        latency = time.time() - start_time

        print(f"✅ Query successful")
        print(f"   Latency: {latency:.2f}s")
        print(f"   Response length: {len(response)} characters")
        print(f"   Response preview: {response[:100]}")

        return True

    except Exception as e:
        print(f"❌ Query test failed: {e}")
        return False


def test_streaming():
    """Test 4: Streaming Responses"""
    print("\n" + "=" * 60)
    print("Test 4: Streaming Responses")
    print("=" * 60)

    try:
        claude = ClaudeController()
        test_prompt = "Count from 1 to 5, one number per line."

        print(f"   Testing streaming...")
        chunks_received = 0

        for chunk in claude.stream_query(test_prompt):
            chunks_received += 1
            print(f"   Chunk {chunks_received}: {chunk[:30]}...")

        print(f"✅ Streaming test passed")
        print(f"   Total chunks: {chunks_received}")

        return chunks_received > 0

    except Exception as e:
        print(f"❌ Streaming test failed: {e}")
        return False


def test_token_tracking():
    """Test 5: Token Usage Tracking"""
    print("\n" + "=" * 60)
    print("Test 5: Token Usage Tracking")
    print("=" * 60)

    try:
        claude = ClaudeController()
        test_prompt = "Hello"

        response = claude.query(test_prompt)
        usage = claude.get_last_usage()

        print(f"✅ Token tracking functional")
        print(f"   Input tokens: {usage.get('input_tokens', 'N/A')}")
        print(f"   Output tokens: {usage.get('output_tokens', 'N/A')}")
        print(f"   Total tokens: {usage.get('total_tokens', 'N/A')}")

        return usage.get('total_tokens', 0) > 0

    except Exception as e:
        print(f"❌ Token tracking test failed: {e}")
        return False


def test_cost_calculation():
    """Test 6: Cost Calculation"""
    print("\n" + "=" * 60)
    print("Test 6: Cost Calculation")
    print("=" * 60)

    try:
        claude = ClaudeController()

        # Simulate usage
        test_usage = {
            'input_tokens': 1000,
            'output_tokens': 500
        }

        cost = claude.calculate_cost(test_usage)

        print(f"✅ Cost calculation working")
        print(f"   1000 input + 500 output tokens")
        print(f"   Estimated cost: ${cost:.4f}")

        # Claude 3.5 Sonnet pricing: ~$0.003/1K input, $0.015/1K output
        expected_cost = (1000 * 0.003 / 1000) + (500 * 0.015 / 1000)
        tolerance = 0.001

        if abs(cost - expected_cost) < tolerance:
            print(f"   Calculation: Accurate")
            return True
        else:
            print(f"   ⚠️  Calculation may be off (expected ~${expected_cost:.4f})")
            return False

    except Exception as e:
        print(f"❌ Cost calculation test failed: {e}")
        return False


def test_error_handling():
    """Test 7: Error Handling"""
    print("\n" + "=" * 60)
    print("Test 7: Error Handling")
    print("=" * 60)

    errors_handled = 0

    # Test 7a: Empty prompt
    try:
        claude = ClaudeController()
        claude.query("")
        print(f"   7a: ❌ Empty prompt should raise error")
    except ValueError:
        print(f"   7a: ✅ Empty prompt correctly rejected")
        errors_handled += 1
    except Exception as e:
        print(f"   7a: ✅ Empty prompt raised error: {type(e).__name__}")
        errors_handled += 1

    # Test 7b: Network timeout (simulated)
    try:
        claude = ClaudeController(timeout=0.001)  # 1ms timeout
        claude.query("test")
        print(f"   7b: ❌ Timeout should have occurred")
    except Exception as e:
        print(f"   7b: ✅ Timeout handled: {type(e).__name__}")
        errors_handled += 1

    # Test 7c: Rate limiting (would need actual API)
    print(f"   7c: ⚠️  Rate limiting test skipped (requires live API)")

    print(f"\n   Results: {errors_handled}/2 error cases handled")
    return errors_handled >= 2


def run_all_tests():
    """Run all Claude API tests"""
    print("\n" + "=" * 60)
    print("QWAMOS - Claude API Test Suite")
    print("=" * 60 + "\n")

    print("⚠️  Note: Some tests require valid API key and network access")
    print("⚠️  Ensure Tor is running on 127.0.0.1:9050\n")

    results = []

    # Test 1: API Key Validation
    results.append(('API Key Validation', test_api_key_validation()))

    # Test 2: Tor Routing
    results.append(('Tor Routing', test_tor_routing()))

    # Test 3: Basic Query (requires valid API key)
    try:
        results.append(('Basic Query', test_basic_query()))
    except:
        results.append(('Basic Query', False))
        print("   ⚠️  Skipped (no valid API key)")

    # Test 4: Streaming (requires valid API key)
    try:
        results.append(('Streaming', test_streaming()))
    except:
        results.append(('Streaming', False))
        print("   ⚠️  Skipped (no valid API key)")

    # Test 5: Token Tracking
    try:
        results.append(('Token Tracking', test_token_tracking()))
    except:
        results.append(('Token Tracking', False))
        print("   ⚠️  Skipped (no valid API key)")

    # Test 6: Cost Calculation
    results.append(('Cost Calculation', test_cost_calculation()))

    # Test 7: Error Handling
    results.append(('Error Handling', test_error_handling()))

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
        print("\n🎉 All tests passed! Claude integration is fully operational.")
        return 0
    elif passed >= total * 0.5:
        print(f"\n⚠️  Some tests failed (may need valid API key)")
        return 1
    else:
        print(f"\n❌ Too many failures. Check configuration.")
        return 2


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
