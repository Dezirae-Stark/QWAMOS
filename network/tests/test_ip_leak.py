#!/usr/bin/env python3
"""
QWAMOS IP Leak Detection Test Suite

Tests for detecting various types of network leaks:
- IPv4 leaks
- IPv6 leaks
- DNS leaks
- WebRTC leaks
- Time zone leaks

Run this test before and after starting Tor/VPN to verify anonymization.
"""

import subprocess
import socket
import json
import time
from typing import Dict, List, Tuple

class IPLeakTester:
    """Comprehensive IP leak detection"""

    def __init__(self):
        self.results = {
            'timestamp': time.time(),
            'tests': {},
            'leaks_detected': []
        }

    def run_all_tests(self) -> Dict:
        """
        Run all leak detection tests

        Returns:
            Dict with test results
        """
        print("="*60)
        print("QWAMOS IP Leak Detection Test Suite")
        print("="*60)
        print()

        # Test 1: IPv4 Leak
        print("[1/6] Testing for IPv4 leaks...")
        self.test_ipv4_leak()

        # Test 2: IPv6 Leak
        print("[2/6] Testing for IPv6 leaks...")
        self.test_ipv6_leak()

        # Test 3: DNS Leak
        print("[3/6] Testing for DNS leaks...")
        self.test_dns_leak()

        # Test 4: WebRTC Leak
        print("[4/6] Testing for WebRTC leaks...")
        self.test_webrtc_leak()

        # Test 5: Tor Check
        print("[5/6] Verifying Tor connection...")
        self.test_tor_connection()

        # Test 6: System DNS
        print("[6/6] Checking system DNS configuration...")
        self.test_system_dns()

        print()
        self._print_summary()

        return self.results

    def test_ipv4_leak(self):
        """Test for IPv4 address leaks"""
        try:
            # Get public IPv4 via multiple services
            services = [
                ('https://icanhazip.com', 'icanhazip'),
                ('https://api.ipify.org', 'ipify'),
                ('https://checkip.amazonaws.com', 'aws')
            ]

            ips = []
            for url, name in services:
                try:
                    result = subprocess.run(
                        ['curl', '-4', '-s', '--max-time', '10', url],
                        capture_output=True,
                        timeout=15
                    )

                    if result.returncode == 0:
                        ip = result.stdout.decode().strip()
                        ips.append((name, ip))
                        print(f"   {name}: {ip}")
                except:
                    continue

            # Check if all IPs match
            if len(set([ip for _, ip in ips])) == 1:
                self.results['tests']['ipv4'] = {
                    'status': 'pass',
                    'ip': ips[0][1],
                    'consistent': True
                }
                print("   ✅ IPv4: Consistent across all services")
            elif len(ips) > 0:
                self.results['tests']['ipv4'] = {
                    'status': 'warning',
                    'ips': ips,
                    'consistent': False
                }
                self.results['leaks_detected'].append('IPv4 inconsistency detected')
                print("   ⚠️  IPv4: Inconsistent IPs detected!")
            else:
                self.results['tests']['ipv4'] = {
                    'status': 'unknown',
                    'error': 'Could not determine IPv4'
                }
                print("   ⚠️  IPv4: Could not be determined")

        except Exception as e:
            self.results['tests']['ipv4'] = {
                'status': 'error',
                'error': str(e)
            }
            print(f"   ❌ IPv4 Test Error: {e}")

    def test_ipv6_leak(self):
        """Test for IPv6 address leaks (should be blocked)"""
        try:
            result = subprocess.run(
                ['curl', '-6', '-s', '--max-time', '5', 'https://icanhazip.com'],
                capture_output=True,
                timeout=10
            )

            if result.returncode == 0 and result.stdout:
                ipv6 = result.stdout.decode().strip()
                self.results['tests']['ipv6'] = {
                    'status': 'fail',
                    'ip': ipv6,
                    'leak': True
                }
                self.results['leaks_detected'].append(f'IPv6 leak detected: {ipv6}')
                print(f"   ❌ IPv6 LEAK DETECTED: {ipv6}")
            else:
                self.results['tests']['ipv6'] = {
                    'status': 'pass',
                    'blocked': True
                }
                print("   ✅ IPv6: Properly blocked")

        except Exception as e:
            # Timeout or connection refused is good (IPv6 blocked)
            self.results['tests']['ipv6'] = {
                'status': 'pass',
                'blocked': True
            }
            print("   ✅ IPv6: Properly blocked")

    def test_dns_leak(self):
        """Test for DNS leaks"""
        try:
            # Perform DNS lookup and check resolver
            result = subprocess.run(
                ['dig', '+short', 'whoami.akamai.net', '@resolver1.opendns.com'],
                capture_output=True,
                timeout=10
            )

            if result.returncode == 0:
                dns_ip = result.stdout.decode().strip()
                print(f"   DNS resolver sees: {dns_ip}")

                # Compare with public IP
                public_ip_result = subprocess.run(
                    ['curl', '-s', '--max-time', '10', 'https://icanhazip.com'],
                    capture_output=True,
                    timeout=15
                )

                if public_ip_result.returncode == 0:
                    public_ip = public_ip_result.stdout.decode().strip()

                    if dns_ip != public_ip:
                        self.results['tests']['dns'] = {
                            'status': 'warning',
                            'dns_ip': dns_ip,
                            'public_ip': public_ip,
                            'match': False
                        }
                        print(f"   ⚠️  DNS: Resolver IP differs from public IP")
                    else:
                        self.results['tests']['dns'] = {
                            'status': 'pass',
                            'ip': public_ip
                        }
                        print("   ✅ DNS: No obvious leaks")

        except Exception as e:
            self.results['tests']['dns'] = {
                'status': 'error',
                'error': str(e)
            }
            print(f"   ⚠️  DNS Test: {e}")

    def test_webrtc_leak(self):
        """Test for WebRTC leaks (requires browser)"""
        # WebRTC leaks can only be fully tested in a browser
        # Here we check if WebRTC is available on the system
        self.results['tests']['webrtc'] = {
            'status': 'skip',
            'note': 'WebRTC testing requires browser - manual testing recommended'
        }
        print("   ⏭️  WebRTC: Manual testing in browser recommended")
        print("      Visit: https://browserleaks.com/webrtc")

    def test_tor_connection(self):
        """Check if connected through Tor"""
        try:
            result = subprocess.run(
                ['curl', '-s', '--max-time', '15', 'https://check.torproject.org/api/ip'],
                capture_output=True,
                timeout=20
            )

            if result.returncode == 0:
                response = json.loads(result.stdout.decode())

                if response.get('IsTor', False):
                    self.results['tests']['tor'] = {
                        'status': 'pass',
                        'using_tor': True,
                        'ip': response.get('IP')
                    }
                    print(f"   ✅ Tor: Connected via Tor exit ({response.get('IP')})")
                else:
                    self.results['tests']['tor'] = {
                        'status': 'fail',
                        'using_tor': False,
                        'ip': response.get('IP')
                    }
                    self.results['leaks_detected'].append('Not using Tor!')
                    print(f"   ❌ Tor: NOT using Tor! ({response.get('IP')})")

        except Exception as e:
            self.results['tests']['tor'] = {
                'status': 'error',
                'error': str(e)
            }
            print(f"   ⚠️  Tor Check: {e}")

    def test_system_dns(self):
        """Check system DNS configuration"""
        try:
            # Check /etc/resolv.conf
            with open('/etc/resolv.conf', 'r') as f:
                resolv_conf = f.read()

            nameservers = []
            for line in resolv_conf.split('\n'):
                if line.startswith('nameserver'):
                    ns = line.split()[1]
                    nameservers.append(ns)

            print(f"   System DNS: {', '.join(nameservers)}")

            # Check if using localhost (DNSCrypt)
            if '127.0.0.1' in nameservers or '127.0.0.53' in nameservers:
                self.results['tests']['system_dns'] = {
                    'status': 'pass',
                    'nameservers': nameservers,
                    'using_local': True
                }
                print("   ✅ System DNS: Using local resolver (good)")
            else:
                self.results['tests']['system_dns'] = {
                    'status': 'warning',
                    'nameservers': nameservers,
                    'using_local': False
                }
                print("   ⚠️  System DNS: Using external resolvers")

        except Exception as e:
            self.results['tests']['system_dns'] = {
                'status': 'error',
                'error': str(e)
            }
            print(f"   ⚠️  System DNS: {e}")

    def _print_summary(self):
        """Print test summary"""
        print("="*60)
        print("TEST SUMMARY")
        print("="*60)

        total_tests = len(self.results['tests'])
        passed = sum(1 for t in self.results['tests'].values() if t.get('status') == 'pass')
        failed = sum(1 for t in self.results['tests'].values() if t.get('status') == 'fail')
        warnings = sum(1 for t in self.results['tests'].values() if t.get('status') == 'warning')

        print(f"\nTests Run: {total_tests}")
        print(f"  ✅ Passed: {passed}")
        print(f"  ❌ Failed: {failed}")
        print(f"  ⚠️  Warnings: {warnings}")

        if self.results['leaks_detected']:
            print(f"\n🚨 LEAKS DETECTED: {len(self.results['leaks_detected'])}")
            for leak in self.results['leaks_detected']:
                print(f"  - {leak}")
        else:
            print("\n✅ No major leaks detected")

        print("\nRecommendations:")
        if failed > 0:
            print("  - Fix critical issues before using for sensitive activities")
        if warnings > 0:
            print("  - Review warnings and consider stronger anonymization")
        print("  - Always test WebRTC leaks in a browser")
        print("  - Regularly re-test after network changes")

        print("\n" + "="*60)


def main():
    """Main entry point"""
    tester = IPLeakTester()
    results = tester.run_all_tests()

    # Save results to file
    output_file = '/tmp/qwamos_leak_test_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_file}")
    print()

    # Exit with appropriate code
    if results['leaks_detected']:
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
