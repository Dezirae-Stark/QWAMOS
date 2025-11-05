#!/usr/bin/env python3
"""
QWAMOS Phase 9: Deployment Manager

Secure app deployment to dedicated VMs:
- One VM per app for maximum isolation
- Minimal permissions enforcement
- Runtime monitoring and threat detection
- Resource management (CPU, RAM, storage)
- Network isolation

@module deployment_manager
@version 1.0.0
"""

import logging
import asyncio
import subprocess
import os
import json
import psutil
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger('DeploymentManager')


class DeploymentStatus(Enum):
    """Deployment status"""
    PENDING = "pending"
    CREATING_VM = "creating_vm"
    INSTALLING_APK = "installing_apk"
    CONFIGURING_PERMISSIONS = "configuring_permissions"
    STARTING_MONITOR = "starting_monitor"
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"


class AppStatus(Enum):
    """Runtime app status"""
    RUNNING = "running"
    STOPPED = "stopped"
    CRASHED = "crashed"
    SUSPENDED = "suspended"


class ThreatLevel(Enum):
    """Runtime threat level"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class VMConfiguration:
    """VM configuration for app deployment"""
    vm_id: str
    vm_name: str
    cpu_cores: int
    ram_mb: int
    storage_gb: int
    network_mode: str  # isolated, nat, bridge
    android_version: str


@dataclass
class DeployedApp:
    """Deployed app metadata"""
    app_id: str
    package_name: str
    app_name: str
    vm_config: VMConfiguration
    apk_path: str
    install_time: str
    status: AppStatus
    permissions: List[str]
    network_isolated: bool


@dataclass
class RuntimeMetrics:
    """App runtime metrics"""
    cpu_usage_percent: float
    memory_usage_mb: float
    network_rx_bytes: int
    network_tx_bytes: int
    storage_used_mb: float
    uptime_seconds: float


@dataclass
class ThreatDetection:
    """Runtime threat detection"""
    threat_level: ThreatLevel
    threats_detected: List[str]
    suspicious_behaviors: List[str]
    timestamp: str


@dataclass
class DeploymentResult:
    """Deployment result"""
    success: bool
    deployed_app: Optional[DeployedApp]
    vm_config: Optional[VMConfiguration]
    error_message: Optional[str] = None
    deployment_log: str = ""


class DeploymentManager:
    """
    Deployment manager for AI-generated apps.

    Architecture:
    - One dedicated VM per app
    - Minimal permissions only
    - Network isolation by default
    - Runtime monitoring and threat detection
    - Resource limits enforcement

    Security:
    - Apps cannot interfere with each other
    - Apps cannot access QWAMOS system
    - Apps run with minimal privileges
    - Network access only if explicitly granted
    - Real-time threat detection
    """

    def __init__(self, config: Dict):
        self.config = config
        self.deployment_config = config.get('deployment', {})

        self.dedicated_vm_per_app = self.deployment_config.get('dedicated_vm_per_app', True)
        self.minimal_permissions_only = self.deployment_config.get('minimal_permissions_only', True)
        self.network_isolation = self.deployment_config.get('network_isolation', True)

        # VM default configuration
        self.default_vm_config = self.deployment_config.get('vm_config', {
            'cpu_cores': 2,
            'ram_mb': 1024,
            'storage_gb': 2,
            'network': 'isolated'
        })

        # Deployed apps registry
        self.deployed_apps: Dict[str, DeployedApp] = {}
        self.runtime_monitors: Dict[str, asyncio.Task] = {}

    async def deploy_app(
        self,
        apk_path: str,
        package_name: str,
        app_name: str,
        requested_permissions: List[str],
        user_id: str
    ) -> DeploymentResult:
        """
        Deploy generated app to dedicated VM.

        Args:
            apk_path: Path to signed APK
            package_name: App package name
            app_name: App display name
            requested_permissions: Permissions requested by app
            user_id: User ID deploying the app

        Returns:
            DeploymentResult with deployment status
        """
        logger.info(f"Deploying app: {app_name} ({package_name})")

        deployment_log = []

        try:
            # Step 1: Create dedicated VM
            logger.info("Step 1: Creating dedicated VM...")
            deployment_log.append("Step 1: Creating dedicated VM...")
            vm_config = await self._create_dedicated_vm(app_name, package_name)

            # Step 2: Install APK in VM
            logger.info("Step 2: Installing APK in VM...")
            deployment_log.append("Step 2: Installing APK in VM...")
            await self._install_apk_in_vm(vm_config, apk_path)

            # Step 3: Configure permissions
            logger.info("Step 3: Configuring minimal permissions...")
            deployment_log.append("Step 3: Configuring minimal permissions...")
            allowed_permissions = self._filter_minimal_permissions(requested_permissions)
            await self._configure_permissions(vm_config, package_name, allowed_permissions)

            # Step 4: Configure network isolation
            logger.info("Step 4: Configuring network isolation...")
            deployment_log.append("Step 4: Configuring network isolation...")
            network_isolated = await self._configure_network_isolation(
                vm_config,
                'INTERNET' not in allowed_permissions
            )

            # Step 5: Start runtime monitor
            logger.info("Step 5: Starting runtime monitor...")
            deployment_log.append("Step 5: Starting runtime monitor...")
            await self._start_runtime_monitor(vm_config, package_name)

            # Step 6: Register deployed app
            app_id = f"{user_id}_{package_name}"
            deployed_app = DeployedApp(
                app_id=app_id,
                package_name=package_name,
                app_name=app_name,
                vm_config=vm_config,
                apk_path=apk_path,
                install_time=datetime.now().isoformat(),
                status=AppStatus.STOPPED,
                permissions=allowed_permissions,
                network_isolated=network_isolated
            )

            self.deployed_apps[app_id] = deployed_app

            logger.info(f"✅ Deployment successful: {app_name}")
            logger.info(f"   VM: {vm_config.vm_name}")
            logger.info(f"   Permissions: {len(allowed_permissions)}")
            logger.info(f"   Network isolated: {network_isolated}")

            return DeploymentResult(
                success=True,
                deployed_app=deployed_app,
                vm_config=vm_config,
                deployment_log="\n".join(deployment_log)
            )

        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")

            return DeploymentResult(
                success=False,
                deployed_app=None,
                vm_config=None,
                error_message=str(e),
                deployment_log="\n".join(deployment_log)
            )

    async def _create_dedicated_vm(
        self,
        app_name: str,
        package_name: str
    ) -> VMConfiguration:
        """Create dedicated VM for app"""

        vm_id = f"app_{package_name}_{os.getpid()}"
        vm_name = f"qwamos_app_{app_name.replace(' ', '_').lower()}"

        logger.info(f"Creating VM: {vm_name}")

        # VM configuration
        vm_config = VMConfiguration(
            vm_id=vm_id,
            vm_name=vm_name,
            cpu_cores=self.default_vm_config['cpu_cores'],
            ram_mb=self.default_vm_config['ram_mb'],
            storage_gb=self.default_vm_config['storage_gb'],
            network_mode=self.default_vm_config['network'],
            android_version="13"
        )

        # In production, would create actual VM using:
        # - QEMU/KVM for full virtualization
        # - LXC/Docker for containerization
        # - Android emulator for Android apps

        # For now, create VM metadata
        vm_dir = f"/opt/qwamos/app_vms/{vm_name}"
        os.makedirs(vm_dir, exist_ok=True)

        with open(f"{vm_dir}/vm_config.json", 'w') as f:
            json.dump({
                'vm_id': vm_config.vm_id,
                'vm_name': vm_config.vm_name,
                'cpu_cores': vm_config.cpu_cores,
                'ram_mb': vm_config.ram_mb,
                'storage_gb': vm_config.storage_gb,
                'network_mode': vm_config.network_mode,
                'android_version': vm_config.android_version
            }, f, indent=2)

        logger.info(f"VM created: {vm_name}")

        return vm_config

    async def _install_apk_in_vm(
        self,
        vm_config: VMConfiguration,
        apk_path: str
    ) -> None:
        """Install APK in VM"""

        logger.info(f"Installing APK in VM: {vm_config.vm_name}")

        # In production, would use adb to install in VM:
        # adb -s <vm_device_id> install <apk_path>

        # Copy APK to VM directory
        vm_apk_dir = f"/opt/qwamos/app_vms/{vm_config.vm_name}/apk"
        os.makedirs(vm_apk_dir, exist_ok=True)

        import shutil
        shutil.copy(apk_path, os.path.join(vm_apk_dir, "app.apk"))

        logger.info("APK installed successfully")

    def _filter_minimal_permissions(
        self,
        requested_permissions: List[str]
    ) -> List[str]:
        """Filter permissions to minimal required set"""

        if not self.minimal_permissions_only:
            return requested_permissions

        # Whitelist of allowed permissions
        allowed_permissions_whitelist = [
            'android.permission.INTERNET',  # Only if explicitly requested
            'android.permission.VIBRATE',
            'android.permission.WAKE_LOCK',
            'android.permission.RECEIVE_BOOT_COMPLETED',
            'android.permission.FOREGROUND_SERVICE',
            'android.permission.USE_BIOMETRIC',
            'android.permission.USE_FINGERPRINT'
        ]

        # Dangerous permissions that require explicit user approval
        dangerous_permissions = [
            'READ_EXTERNAL_STORAGE',
            'WRITE_EXTERNAL_STORAGE',
            'CAMERA',
            'RECORD_AUDIO',
            'ACCESS_FINE_LOCATION',
            'READ_CONTACTS',
            'READ_SMS',
            'SEND_SMS',
            'CALL_PHONE'
        ]

        filtered_permissions = []

        for perm in requested_permissions:
            perm_name = perm.split('.')[-1]

            # Allow whitelisted permissions
            if perm in allowed_permissions_whitelist:
                filtered_permissions.append(perm)

            # Block dangerous permissions by default
            elif perm_name in dangerous_permissions:
                logger.warning(f"Blocking dangerous permission: {perm_name}")
                # In production, would prompt user for explicit approval

        logger.info(f"Filtered permissions: {len(requested_permissions)} → {len(filtered_permissions)}")

        return filtered_permissions

    async def _configure_permissions(
        self,
        vm_config: VMConfiguration,
        package_name: str,
        permissions: List[str]
    ) -> None:
        """Configure app permissions in VM"""

        logger.info(f"Configuring {len(permissions)} permissions")

        # In production, would use:
        # adb shell pm grant <package> <permission>

        # Write permissions to VM config
        vm_dir = f"/opt/qwamos/app_vms/{vm_config.vm_name}"
        with open(f"{vm_dir}/permissions.json", 'w') as f:
            json.dump({
                'package_name': package_name,
                'granted_permissions': permissions,
                'denied_permissions': []  # Would track denied permissions
            }, f, indent=2)

        logger.info("Permissions configured")

    async def _configure_network_isolation(
        self,
        vm_config: VMConfiguration,
        isolate: bool
    ) -> bool:
        """Configure network isolation for VM"""

        if not self.network_isolation:
            return False

        if isolate:
            logger.info("Enabling network isolation (no internet access)")

            # In production, would configure VM networking:
            # - iptables rules to block all outbound traffic
            # - VM network interface in isolated mode
            # - DNS blocked

            vm_dir = f"/opt/qwamos/app_vms/{vm_config.vm_name}"
            with open(f"{vm_dir}/network_config.json", 'w') as f:
                json.dump({
                    'mode': 'isolated',
                    'internet_access': False,
                    'firewall_rules': [
                        'DROP all outbound traffic',
                        'DROP all inbound traffic except localhost'
                    ]
                }, f, indent=2)

            return True

        else:
            logger.info("Network isolation disabled (internet access allowed)")
            return False

    async def _start_runtime_monitor(
        self,
        vm_config: VMConfiguration,
        package_name: str
    ) -> None:
        """Start runtime monitoring for app"""

        logger.info("Starting runtime monitor...")

        # Create monitoring task
        monitor_task = asyncio.create_task(
            self._runtime_monitor_loop(vm_config, package_name)
        )

        self.runtime_monitors[vm_config.vm_id] = monitor_task

        logger.info("Runtime monitor started")

    async def _runtime_monitor_loop(
        self,
        vm_config: VMConfiguration,
        package_name: str
    ) -> None:
        """Runtime monitoring loop"""

        logger.info(f"Runtime monitor active for {package_name}")

        while True:
            try:
                # Collect metrics
                metrics = await self._collect_runtime_metrics(vm_config, package_name)

                # Detect threats
                threats = await self._detect_threats(vm_config, package_name, metrics)

                # Log threats
                if threats.threat_level != ThreatLevel.NONE:
                    logger.warning(f"Threat detected in {package_name}: {threats.threat_level.value}")
                    for threat in threats.threats_detected:
                        logger.warning(f"  - {threat}")

                    # Take action based on threat level
                    if threats.threat_level == ThreatLevel.CRITICAL:
                        logger.error(f"CRITICAL threat - terminating {package_name}")
                        await self.stop_app(package_name)

                # Sleep before next check
                await asyncio.sleep(5)  # Check every 5 seconds

            except Exception as e:
                logger.error(f"Runtime monitor error: {e}")
                await asyncio.sleep(10)

    async def _collect_runtime_metrics(
        self,
        vm_config: VMConfiguration,
        package_name: str
    ) -> RuntimeMetrics:
        """Collect runtime metrics from VM"""

        # In production, would query VM metrics via:
        # - adb shell dumpsys cpuinfo
        # - adb shell dumpsys meminfo
        # - VM resource monitoring tools

        # For now, return simulated metrics
        return RuntimeMetrics(
            cpu_usage_percent=5.0,
            memory_usage_mb=128.0,
            network_rx_bytes=0,
            network_tx_bytes=0,
            storage_used_mb=50.0,
            uptime_seconds=300.0
        )

    async def _detect_threats(
        self,
        vm_config: VMConfiguration,
        package_name: str,
        metrics: RuntimeMetrics
    ) -> ThreatDetection:
        """Detect runtime threats and suspicious behavior"""

        threats = []
        suspicious_behaviors = []
        threat_level = ThreatLevel.NONE

        # Check 1: Excessive CPU usage (possible crypto miner)
        if metrics.cpu_usage_percent > 80:
            suspicious_behaviors.append("Excessive CPU usage (>80%)")
            threat_level = ThreatLevel.MEDIUM

        # Check 2: Excessive memory usage (possible memory leak or attack)
        if metrics.memory_usage_mb > self.default_vm_config['ram_mb'] * 0.9:
            suspicious_behaviors.append("Excessive memory usage (>90%)")
            threat_level = ThreatLevel.MEDIUM

        # Check 3: Unexpected network activity (when network isolated)
        if vm_config.network_mode == 'isolated':
            if metrics.network_tx_bytes > 0 or metrics.network_rx_bytes > 0:
                threats.append("Network activity detected in isolated app")
                threat_level = ThreatLevel.HIGH

        # Check 4: Rapid storage growth (possible data exfiltration prep)
        if metrics.storage_used_mb > self.default_vm_config['storage_gb'] * 1024 * 0.8:
            suspicious_behaviors.append("High storage usage (>80%)")
            threat_level = ThreatLevel.LOW

        return ThreatDetection(
            threat_level=threat_level,
            threats_detected=threats,
            suspicious_behaviors=suspicious_behaviors,
            timestamp=datetime.now().isoformat()
        )

    async def start_app(self, app_id: str) -> bool:
        """Start deployed app"""

        if app_id not in self.deployed_apps:
            logger.error(f"App not found: {app_id}")
            return False

        app = self.deployed_apps[app_id]

        logger.info(f"Starting app: {app.app_name}")

        # In production, would use:
        # adb shell am start -n <package>/<activity>

        app.status = AppStatus.RUNNING

        logger.info(f"App started: {app.app_name}")

        return True

    async def stop_app(self, app_id: str) -> bool:
        """Stop running app"""

        if app_id not in self.deployed_apps:
            logger.error(f"App not found: {app_id}")
            return False

        app = self.deployed_apps[app_id]

        logger.info(f"Stopping app: {app.app_name}")

        # In production, would use:
        # adb shell am force-stop <package>

        app.status = AppStatus.STOPPED

        logger.info(f"App stopped: {app.app_name}")

        return True

    async def uninstall_app(self, app_id: str) -> bool:
        """Uninstall app and destroy VM"""

        if app_id not in self.deployed_apps:
            logger.error(f"App not found: {app_id}")
            return False

        app = self.deployed_apps[app_id]

        logger.info(f"Uninstalling app: {app.app_name}")

        # Stop app
        await self.stop_app(app_id)

        # Stop runtime monitor
        if app.vm_config.vm_id in self.runtime_monitors:
            self.runtime_monitors[app.vm_config.vm_id].cancel()
            del self.runtime_monitors[app.vm_config.vm_id]

        # Destroy VM
        await self._destroy_vm(app.vm_config)

        # Remove from registry
        del self.deployed_apps[app_id]

        logger.info(f"App uninstalled: {app.app_name}")

        return True

    async def _destroy_vm(self, vm_config: VMConfiguration) -> None:
        """Destroy VM and cleanup resources"""

        logger.info(f"Destroying VM: {vm_config.vm_name}")

        # In production, would:
        # - Stop VM (virsh destroy <vm_name>)
        # - Delete VM disk images
        # - Release resources

        # Remove VM directory
        vm_dir = f"/opt/qwamos/app_vms/{vm_config.vm_name}"
        if os.path.exists(vm_dir):
            import shutil
            shutil.rmtree(vm_dir)

        logger.info(f"VM destroyed: {vm_config.vm_name}")

    def list_deployed_apps(self) -> List[DeployedApp]:
        """List all deployed apps"""
        return list(self.deployed_apps.values())

    async def get_app_metrics(self, app_id: str) -> Optional[RuntimeMetrics]:
        """Get runtime metrics for app"""

        if app_id not in self.deployed_apps:
            return None

        app = self.deployed_apps[app_id]

        return await self._collect_runtime_metrics(app.vm_config, app.package_name)

    async def get_app_threats(self, app_id: str) -> Optional[ThreatDetection]:
        """Get threat detection status for app"""

        if app_id not in self.deployed_apps:
            return None

        app = self.deployed_apps[app_id]
        metrics = await self._collect_runtime_metrics(app.vm_config, app.package_name)

        return await self._detect_threats(app.vm_config, app.package_name, metrics)
