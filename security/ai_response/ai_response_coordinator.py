#!/usr/bin/env python3
"""
QWAMOS AI Response Coordinator

Coordinates AI-powered responses to detected threats by:
1. Analyzing threats with Kali GPT
2. Developing strategies with Claude
3. Generating mitigations with ChatGPT
4. Requesting user permissions
5. Executing approved actions
6. Monitoring and adjusting responses

Integrates with QWAMOS AI Assistants (Phase 6)
"""

import asyncio
import sys
import os
import time
import json
import logging
from typing import Dict, List, Optional
from pathlib import Path

# Add QWAMOS AI to path
sys.path.insert(0, '/opt/qwamos/ai')
sys.path.insert(0, '/data/data/com.termux/files/home/QWAMOS/ai')

try:
    from ai_manager import AIManager
except ImportError:
    logger.warning("AI Manager not found, using mock")
    AIManager = None

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AIResponseCoordinator')


class AIResponseCoordinator:
    """
    Coordinates AI responses to detected threats
    """

    def __init__(self, config_path='/opt/qwamos/security/config/ai_response_config.json'):
        """
        Initialize AI Response Coordinator

        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()

        # Initialize AI Manager
        try:
            self.ai_manager = AIManager() if AIManager else None
            logger.info("AI Manager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize AI Manager: {e}")
            self.ai_manager = None

        # Action executor (imported later to avoid circular dependency)
        self.action_executor = None

        # Threat queue
        self.pending_threats = asyncio.Queue()
        self.active_responses = {}

        # User permissions
        self.user_permissions = self._load_permissions()

        # Statistics
        self.threats_handled = 0
        self.actions_executed = 0
        self.actions_denied = 0

        logger.info("AI Response Coordinator initialized")

    def _load_config(self) -> Dict:
        """Load configuration"""
        default_config = {
            'auto_response_severity': 'MEDIUM',  # Auto-respond up to this severity
            'require_permission_above': 'HIGH',   # Require permission for these
            'ai_timeout': 60,                      # AI query timeout (seconds)
            'max_concurrent_responses': 5,
            'alert_channels': ['log', 'ui', 'email'],
            'enable_auto_patching': True,
            'enable_network_isolation': True
        }

        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                return {**default_config, **config}
        except:
            return default_config

    def _load_permissions(self) -> Dict:
        """Load user permission settings"""
        default_permissions = {
            'auto_isolate_vm': True,
            'auto_block_ip': True,
            'auto_kill_process': False,
            'auto_patch': False,
            'auto_snapshot': True
        }

        try:
            with open('/opt/qwamos/security/config/permissions.json', 'r') as f:
                perms = json.load(f)
                return {**default_permissions, **perms}
        except:
            return default_permissions

    async def handle_threat(self, threat: Dict):
        """
        Main threat handling pipeline

        1. Classify and assess severity
        2. Query AI assistants for response strategy
        3. Generate mitigation actions
        4. Request user permission (if required)
        5. Execute actions
        6. Monitor and adjust
        """
        logger.info(f"[THREAT DETECTED] {threat['type']} - Severity: {threat.get('severity', 'UNKNOWN')}")

        self.threats_handled += 1

        # Add to active responses
        threat_id = f"threat_{int(time.time() * 1000)}"
        self.active_responses[threat_id] = {
            'threat': threat,
            'status': 'analyzing',
            'start_time': time.time()
        }

        try:
            # Step 1: Get immediate analysis from Kali GPT
            logger.info("[STEP 1] Analyzing threat with Kali GPT...")
            kali_analysis = await self._analyze_with_kali_gpt(threat)

            # Step 2: Get strategic response from Claude
            logger.info("[STEP 2] Developing strategy with Claude...")
            claude_strategy = await self._get_claude_strategy(threat, kali_analysis)

            # Step 3: Get tactical mitigation from ChatGPT
            logger.info("[STEP 3] Generating mitigation with ChatGPT...")
            chatgpt_mitigation = await self._get_chatgpt_mitigation(threat, claude_strategy)

            # Step 4: Combine responses into action plan
            logger.info("[STEP 4] Creating action plan...")
            action_plan = self._create_action_plan(
                threat, kali_analysis, claude_strategy, chatgpt_mitigation
            )

            self.active_responses[threat_id]['action_plan'] = action_plan
            self.active_responses[threat_id]['status'] = 'awaiting_permission'

            # Step 5: Check user permissions
            if self._requires_user_permission(action_plan):
                logger.info("[STEP 5] Requesting user permission...")
                permission_granted = await self._request_user_permission(action_plan)

                if not permission_granted:
                    logger.warning("[ACTION DENIED] User denied permission")
                    self.actions_denied += 1
                    self.active_responses[threat_id]['status'] = 'denied'
                    return
            else:
                logger.info("[STEP 5] Auto-approved based on severity")

            # Step 6: Execute actions
            logger.info("[STEP 6] Executing action plan...")
            self.active_responses[threat_id]['status'] = 'executing'
            await self._execute_action_plan(action_plan)

            # Step 7: Monitor results
            logger.info("[STEP 7] Monitoring results...")
            self.active_responses[threat_id]['status'] = 'monitoring'
            await self._monitor_and_adjust(action_plan)

            self.active_responses[threat_id]['status'] = 'completed'
            logger.info(f"[THREAT RESOLVED] {threat_id}")

        except Exception as e:
            logger.error(f"Error handling threat: {e}")
            self.active_responses[threat_id]['status'] = 'error'
            self.active_responses[threat_id]['error'] = str(e)

    async def _analyze_with_kali_gpt(self, threat: Dict) -> Dict:
        """Get technical analysis from Kali GPT"""
        if not self.ai_manager:
            return {'analysis': 'AI Manager not available', 'timestamp': time.time()}

        prompt = f"""
        Analyze this security threat:

        Type: {threat.get('type', 'UNKNOWN')}
        Severity: {threat.get('severity', 'UNKNOWN')}
        Details: {json.dumps(threat.get('details', {}), indent=2)}

        Provide:
        1. Attack classification (what type of attack is this?)
        2. Likely attack vector (how did the attack occur?)
        3. Potential impact (what damage could this cause?)
        4. Immediate containment steps (what should be done right now?)

        Be specific and actionable.
        """

        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.ai_manager.query,
                    'kali-gpt',
                    prompt
                ),
                timeout=self.config['ai_timeout']
            )

            return {
                'analysis': response,
                'timestamp': time.time()
            }
        except asyncio.TimeoutError:
            logger.error("Kali GPT query timed out")
            return {'analysis': 'Timeout', 'timestamp': time.time()}
        except Exception as e:
            logger.error(f"Kali GPT error: {e}")
            return {'analysis': str(e), 'timestamp': time.time()}

    async def _get_claude_strategy(self, threat: Dict, analysis: Dict) -> Dict:
        """Get strategic response from Claude"""
        if not self.ai_manager:
            return {'strategy': 'AI Manager not available', 'timestamp': time.time()}

        prompt = f"""
        Based on this threat analysis, develop a comprehensive response strategy:

        Threat Type: {threat.get('type')}
        Severity: {threat.get('severity')}

        Technical Analysis:
        {analysis.get('analysis', 'N/A')}

        Consider:
        1. Short-term containment (immediate actions to stop the threat)
        2. Long-term prevention (how to prevent this in the future)
        3. System hardening recommendations
        4. Patch requirements (if applicable)
        5. Data recovery considerations

        Provide a detailed, actionable strategy organized by priority.
        """

        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.ai_manager.query,
                    'claude',
                    prompt
                ),
                timeout=self.config['ai_timeout']
            )

            return {
                'strategy': response,
                'timestamp': time.time()
            }
        except asyncio.TimeoutError:
            logger.error("Claude query timed out")
            return {'strategy': 'Timeout', 'timestamp': time.time()}
        except Exception as e:
            logger.error(f"Claude error: {e}")
            return {'strategy': str(e), 'timestamp': time.time()}

    async def _get_chatgpt_mitigation(self, threat: Dict, strategy: Dict) -> Dict:
        """Get tactical mitigation steps from ChatGPT"""
        if not self.ai_manager:
            return {'mitigation': 'AI Manager not available', 'timestamp': time.time()}

        prompt = f"""
        Generate specific mitigation commands for this threat:

        Threat: {threat.get('type')}
        Strategy: {strategy.get('strategy', 'N/A')}

        Provide executable commands for:
        1. Firewall rules to add (nftables/iptables format)
        2. Processes to terminate (kill commands)
        3. Network isolation commands (IP blocking, interface shutdown)
        4. VM snapshot commands (QEMU snapshot)
        5. File quarantine commands (move suspicious files)

        Format as JSON with these fields:
        {{
            "firewall_rules": ["rule1", "rule2"],
            "process_kills": ["pid1", "pid2"],
            "network_isolation": ["cmd1", "cmd2"],
            "vm_snapshots": ["vm1", "vm2"],
            "file_quarantine": ["/path/to/file1", "/path/to/file2"]
        }}
        """

        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.ai_manager.query,
                    'chatgpt',
                    prompt
                ),
                timeout=self.config['ai_timeout']
            )

            # Try to parse as JSON
            try:
                if isinstance(response, str):
                    mitigation = json.loads(response)
                else:
                    mitigation = response
            except:
                mitigation = {'raw_response': response}

            return {
                'mitigation': mitigation,
                'timestamp': time.time()
            }
        except asyncio.TimeoutError:
            logger.error("ChatGPT query timed out")
            return {'mitigation': 'Timeout', 'timestamp': time.time()}
        except Exception as e:
            logger.error(f"ChatGPT error: {e}")
            return {'mitigation': str(e), 'timestamp': time.time()}

    def _create_action_plan(self,
                           threat: Dict,
                           kali_analysis: Dict,
                           claude_strategy: Dict,
                           chatgpt_mitigation: Dict) -> Dict:
        """Combine AI responses into unified action plan"""
        action_plan = {
            'threat_id': f"threat_{int(time.time() * 1000)}",
            'threat_type': threat.get('type'),
            'severity': threat.get('severity'),
            'timestamp': time.time(),
            'ai_analysis': {
                'kali_gpt': kali_analysis.get('analysis'),
                'claude': claude_strategy.get('strategy'),
                'chatgpt': chatgpt_mitigation.get('mitigation')
            },
            'actions': []
        }

        # Extract actions from ChatGPT mitigation
        mitigation = chatgpt_mitigation.get('mitigation', {})

        if isinstance(mitigation, dict):
            # Firewall rules
            if 'firewall_rules' in mitigation:
                for rule in mitigation['firewall_rules']:
                    action_plan['actions'].append({
                        'type': 'firewall',
                        'command': rule,
                        'priority': 1
                    })

            # Process kills
            if 'process_kills' in mitigation:
                for pid in mitigation['process_kills']:
                    action_plan['actions'].append({
                        'type': 'kill_process',
                        'pid': pid,
                        'priority': 1
                    })

            # Network isolation
            if 'network_isolation' in mitigation:
                for cmd in mitigation['network_isolation']:
                    action_plan['actions'].append({
                        'type': 'network_isolation',
                        'command': cmd,
                        'priority': 1
                    })

            # VM snapshots
            if 'vm_snapshots' in mitigation:
                for vm in mitigation['vm_snapshots']:
                    action_plan['actions'].append({
                        'type': 'vm_snapshot',
                        'vm': vm,
                        'priority': 2
                    })

            # File quarantine
            if 'file_quarantine' in mitigation:
                for file_path in mitigation['file_quarantine']:
                    action_plan['actions'].append({
                        'type': 'quarantine_file',
                        'file': file_path,
                        'priority': 2
                    })

        # Sort by priority
        action_plan['actions'].sort(key=lambda x: x.get('priority', 99))

        return action_plan

    def _requires_user_permission(self, action_plan: Dict) -> bool:
        """Check if action plan requires user permission"""
        severity = action_plan.get('severity', 'LOW')

        # High/Critical severity always requires permission
        if severity in ['HIGH', 'CRITICAL']:
            return True

        # Check if any actions require permission
        for action in action_plan.get('actions', []):
            action_type = action.get('type')

            if action_type == 'kill_process' and not self.user_permissions.get('auto_kill_process'):
                return True

            if action_type == 'network_isolation' and not self.user_permissions.get('auto_isolate_vm'):
                return True

        return False

    async def _request_user_permission(self, action_plan: Dict) -> bool:
        """Request user permission for action plan"""
        # In production, this would show UI dialog to user
        # For now, we'll use a simple prompt

        logger.warning("=" * 70)
        logger.warning("USER PERMISSION REQUIRED")
        logger.warning("=" * 70)
        logger.warning(f"Threat: {action_plan.get('threat_type')}")
        logger.warning(f"Severity: {action_plan.get('severity')}")
        logger.warning(f"Planned Actions ({len(action_plan.get('actions', []))}):")

        for i, action in enumerate(action_plan.get('actions', []), 1):
            logger.warning(f"  {i}. {action.get('type')}: {action.get('command', action.get('pid', action.get('file')))}")

        logger.warning("=" * 70)

        # TODO: Implement React Native UI permission dialog
        # For now, auto-approve LOW/MEDIUM, deny HIGH/CRITICAL
        severity = action_plan.get('severity', 'LOW')
        if severity in ['HIGH', 'CRITICAL']:
            logger.warning("AUTO-DENIED (HIGH/CRITICAL severity requires manual approval)")
            return False
        else:
            logger.warning("AUTO-APPROVED (LOW/MEDIUM severity)")
            return True

    async def _execute_action_plan(self, action_plan: Dict):
        """Execute approved action plan"""
        if not self.action_executor:
            # Lazy load to avoid circular dependency
            from security.actions.action_executor import ActionExecutor
            self.action_executor = ActionExecutor()

        logger.info(f"Executing {len(action_plan.get('actions', []))} actions...")

        for action in action_plan.get('actions', []):
            try:
                logger.info(f"Executing: {action.get('type')}")
                await self.action_executor.execute(action)
                self.actions_executed += 1
            except Exception as e:
                logger.error(f"Action execution failed: {e}")

    async def _monitor_and_adjust(self, action_plan: Dict):
        """Monitor action results and adjust if needed"""
        # Monitor for 60 seconds
        await asyncio.sleep(60)

        # TODO: Check if threat was successfully mitigated
        # If not, generate new action plan

        logger.info("Monitoring complete")

    def get_statistics(self) -> Dict:
        """Get coordinator statistics"""
        return {
            'threats_handled': self.threats_handled,
            'actions_executed': self.actions_executed,
            'actions_denied': self.actions_denied,
            'active_responses': len(self.active_responses),
            'pending_threats': self.pending_threats.qsize()
        }


# CLI Interface
if __name__ == "__main__":
    coordinator = AIResponseCoordinator()

    # Test threat
    test_threat = {
        'type': 'PORT_SCAN',
        'severity': 'MEDIUM',
        'details': {
            'source_ip': '192.168.1.100',
            'ports_scanned': 50,
            'timestamp': time.time()
        }
    }

    asyncio.run(coordinator.handle_threat(test_threat))
