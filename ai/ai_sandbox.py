#!/usr/bin/env python3
"""
QWAMOS AI Sandbox - Process Isolation for AI Services

CRITICAL FIX #22: Implements container-based isolation for AI processes.

This module provides sandboxing for AI assistants (Kali GPT, Claude API, ChatGPT API)
to prevent potential security issues from compromised AI services.

Security features:
- Separate network namespace (optional)
- Filesystem restrictions (read-only system)
- Resource limits via cgroups
- Capability dropping
- Seccomp filtering

Author: QWAMOS Security Team
"""

import os
import sys
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('AISandbox')


class SandboxMode(Enum):
    """Sandbox isolation levels."""
    NONE = "none"  # No sandboxing (unsafe!)
    BASIC = "basic"  # Basic process isolation
    STRICT = "strict"  # Full container isolation
    NETWORK_ISOLATED = "network-isolated"  # Strict + no network


class AISandbox:
    """
    Sandbox wrapper for AI process execution.

    CRITICAL FIX #22: Provides container-based isolation for AI services.
    """

    def __init__(self,
                 ai_service: str,
                 mode: SandboxMode = SandboxMode.STRICT,
                 config_dir: str = "/opt/qwamos/ai"):
        """
        Initialize AI sandbox.

        Args:
            ai_service: Name of AI service (kali_gpt, chatgpt, claude)
            mode: Sandbox isolation mode
            config_dir: AI configuration directory
        """
        self.ai_service = ai_service
        self.mode = mode
        self.config_dir = Path(config_dir)
        self.service_dir = self.config_dir / ai_service

        # Sandbox directories
        self.sandbox_root = Path("/var/lib/qwamos/ai-sandbox") / ai_service
        self.sandbox_home = self.sandbox_root / "home"
        self.sandbox_tmp = self.sandbox_root / "tmp"
        self.sandbox_config = self.sandbox_root / "config"

        logger.info(f"AI Sandbox initialized: {ai_service} (mode: {mode.value})")

    def setup_sandbox(self):
        """
        Set up sandbox environment.

        Creates isolated directories and sets permissions.
        """
        if self.mode == SandboxMode.NONE:
            logger.warning("⚠️  Sandbox mode NONE - no isolation applied!")
            return

        # Create sandbox directories
        for directory in [self.sandbox_root, self.sandbox_home,
                         self.sandbox_tmp, self.sandbox_config]:
            directory.mkdir(parents=True, exist_ok=True)

        # Set restrictive permissions
        os.chmod(self.sandbox_root, 0o700)
        os.chmod(self.sandbox_home, 0o700)
        os.chmod(self.sandbox_tmp, 0o700)

        logger.info(f"✓ Sandbox environment created at {self.sandbox_root}")

    def run_isolated(self,
                     command: List[str],
                     env: Optional[Dict[str, str]] = None,
                     allow_network: bool = True) -> subprocess.CompletedProcess:
        """
        Run command in isolated sandbox.

        Args:
            command: Command and arguments to execute
            env: Environment variables
            allow_network: Whether to allow network access

        Returns:
            CompletedProcess result
        """
        if self.mode == SandboxMode.NONE:
            # No sandboxing - run directly (UNSAFE!)
            logger.warning("⚠️  Running AI process WITHOUT sandbox isolation!")
            return subprocess.run(command, env=env, capture_output=True, text=True)

        # Build sandbox command
        sandbox_cmd = self._build_sandbox_command(command, allow_network)

        # Merge environment
        sandbox_env = os.environ.copy()
        if env:
            sandbox_env.update(env)

        # Add sandbox-specific environment
        sandbox_env['QWAMOS_SANDBOXED'] = '1'
        sandbox_env['QWAMOS_AI_SERVICE'] = self.ai_service

        logger.info(f"Running {self.ai_service} in {self.mode.value} sandbox")
        logger.debug(f"Command: {' '.join(sandbox_cmd)}")

        # Execute in sandbox
        try:
            result = subprocess.run(
                sandbox_cmd,
                env=sandbox_env,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            return result
        except subprocess.TimeoutExpired:
            logger.error(f"AI process timeout after 300s")
            raise
        except Exception as e:
            logger.error(f"Sandbox execution failed: {e}")
            raise

    def _build_sandbox_command(self,
                               command: List[str],
                               allow_network: bool) -> List[str]:
        """
        Build sandboxed command using available isolation tools.

        Tries in order:
        1. firejail (if available) - easiest, most features
        2. bwrap (bubblewrap) - good alternative
        3. unshare - basic namespace isolation

        Args:
            command: Original command
            allow_network: Whether to allow network

        Returns:
            Sandboxed command with wrapper
        """
        # Try firejail first (recommended)
        if self._command_exists('firejail'):
            return self._build_firejail_command(command, allow_network)

        # Try bubblewrap
        if self._command_exists('bwrap'):
            return self._build_bubblewrap_command(command, allow_network)

        # Fallback to unshare (basic)
        if self._command_exists('unshare'):
            return self._build_unshare_command(command, allow_network)

        # No sandbox tools available
        logger.error("⚠️  No sandbox tools available (firejail, bwrap, unshare)")
        logger.error("   Running AI process WITHOUT isolation - SECURITY RISK!")
        return command

    def _build_firejail_command(self,
                               command: List[str],
                               allow_network: bool) -> List[str]:
        """Build command using firejail sandbox."""
        firejail_cmd = ['firejail']

        # Basic isolation
        firejail_cmd.extend([
            '--quiet',  # Less verbose
            '--private=' + str(self.sandbox_home),  # Private home dir
            '--private-tmp',  # Private /tmp
            '--private-dev',  # Private /dev
            '--read-only=/etc',  # Read-only /etc
            '--read-only=/usr',  # Read-only /usr
            '--read-only=/bin',  # Read-only /bin
            '--read-only=/lib',  # Read-only /lib
            '--read-only=/lib64',  # Read-only /lib64 (if exists)
        ])

        # Network isolation
        if not allow_network or self.mode == SandboxMode.NETWORK_ISOLATED:
            firejail_cmd.append('--net=none')

        # Capabilities - drop all except necessary
        firejail_cmd.extend([
            '--caps.drop=all',
            '--nonewprivs',
            '--noroot',
        ])

        # Seccomp filter (restrict syscalls)
        firejail_cmd.append('--seccomp')

        # Resource limits
        firejail_cmd.extend([
            '--rlimit-as=2147483648',  # 2GB virtual memory
            '--rlimit-cpu=600',  # 10 minutes CPU time
        ])

        # Add original command
        firejail_cmd.append('--')
        firejail_cmd.extend(command)

        logger.info("✓ Using firejail sandbox (recommended)")
        return firejail_cmd

    def _build_bubblewrap_command(self,
                                  command: List[str],
                                  allow_network: bool) -> List[str]:
        """Build command using bubblewrap (bwrap) sandbox."""
        bwrap_cmd = ['bwrap']

        # Bind read-only system directories
        for dir in ['/usr', '/bin', '/lib', '/lib64', '/etc']:
            if Path(dir).exists():
                bwrap_cmd.extend(['--ro-bind', dir, dir])

        # Private directories
        bwrap_cmd.extend([
            '--tmpfs', '/tmp',
            '--tmpfs', '/var',
            '--tmpfs', '/home',
            '--bind', str(self.sandbox_home), '/home/ai',
            '--chdir', '/home/ai',
        ])

        # Proc and dev
        bwrap_cmd.extend([
            '--proc', '/proc',
            '--dev', '/dev',
        ])

        # Network
        if not allow_network or self.mode == SandboxMode.NETWORK_ISOLATED:
            bwrap_cmd.append('--unshare-net')

        # User namespace
        bwrap_cmd.extend([
            '--unshare-user',
            '--unshare-pid',
            '--unshare-ipc',
        ])

        # Add command
        bwrap_cmd.extend(command)

        logger.info("✓ Using bubblewrap sandbox")
        return bwrap_cmd

    def _build_unshare_command(self,
                               command: List[str],
                               allow_network: bool) -> List[str]:
        """Build command using unshare (basic namespace isolation)."""
        unshare_cmd = ['unshare']

        # Unshare namespaces
        unshare_cmd.extend([
            '--pid',  # PID namespace
            '--fork',  # Fork before exec
            '--mount',  # Mount namespace
            '--uts',  # UTS namespace (hostname)
            '--ipc',  # IPC namespace
        ])

        # Network namespace (if isolated)
        if not allow_network or self.mode == SandboxMode.NETWORK_ISOLATED:
            unshare_cmd.append('--net')

        # Add command
        unshare_cmd.extend(command)

        logger.warning("⚠️  Using basic unshare isolation (limited security)")
        logger.warning("   Install firejail for better protection")
        return unshare_cmd

    def _command_exists(self, cmd: str) -> bool:
        """Check if command exists in PATH."""
        return subprocess.run(
            ['which', cmd],
            capture_output=True
        ).returncode == 0

    def cleanup(self):
        """Clean up sandbox environment."""
        if self.mode == SandboxMode.NONE:
            return

        try:
            # Clean temporary files
            if self.sandbox_tmp.exists():
                subprocess.run(['rm', '-rf', str(self.sandbox_tmp)], check=False)
                self.sandbox_tmp.mkdir(exist_ok=True)

            logger.info("✓ Sandbox cleaned up")
        except Exception as e:
            logger.warning(f"Sandbox cleanup failed: {e}")


# Convenience function
def run_ai_sandboxed(ai_service: str,
                     command: List[str],
                     mode: SandboxMode = SandboxMode.STRICT,
                     allow_network: bool = True) -> subprocess.CompletedProcess:
    """
    Run AI service command in sandbox.

    Args:
        ai_service: AI service name
        command: Command to run
        mode: Sandbox mode
        allow_network: Allow network access

    Returns:
        CompletedProcess result
    """
    sandbox = AISandbox(ai_service, mode)
    sandbox.setup_sandbox()

    try:
        return sandbox.run_isolated(command, allow_network=allow_network)
    finally:
        sandbox.cleanup()


if __name__ == "__main__":
    # Test sandbox
    print("=== QWAMOS AI Sandbox Test ===\n")

    # Test with simple command
    result = run_ai_sandboxed(
        ai_service="test",
        command=["echo", "Hello from sandbox"],
        mode=SandboxMode.STRICT
    )

    print(f"Exit code: {result.returncode}")
    print(f"Output: {result.stdout}")

    if result.returncode == 0:
        print("\n✓ Sandbox test successful")
    else:
        print(f"\n✗ Sandbox test failed: {result.stderr}")
