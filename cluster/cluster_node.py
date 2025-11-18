#!/usr/bin/env python3
"""
QWAMOS Cluster Node
Phase XVI: Secure Cluster Mode

Cluster node management for distributed QWAMOS deployment:
- Node identity and authentication
- Peer discovery and management
- Secure communication
- Resource advertisement
- Cluster state synchronization

Author: QWAMOS Project
License: MIT
"""

import os
import socket
import json
import time
import secrets
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib


class NodeRole(Enum):
    """Cluster node roles."""
    COORDINATOR = "coordinator"  # Cluster coordinator
    WORKER = "worker"  # Worker node
    STANDBY = "standby"  # Standby node (backup coordinator)


class NodeStatus(Enum):
    """Node status."""
    ONLINE = "online"
    OFFLINE = "offline"
    SYNCING = "syncing"
    DEGRADED = "degraded"


@dataclass
class NodeIdentity:
    """Node identity information."""
    node_id: str  # Unique node identifier
    hostname: str
    ip_address: str
    public_key: bytes  # Kyber-1024 public key (or ECDH for now)
    role: NodeRole
    cluster_id: str  # Cluster membership


@dataclass
class NodeResources:
    """Node resource capabilities."""
    cpu_cores: int
    memory_mb: int
    storage_gb: int
    gpu_available: bool
    network_bandwidth_mbps: int


@dataclass
class PeerNode:
    """Information about a peer node."""
    identity: NodeIdentity
    resources: NodeResources
    status: NodeStatus
    last_seen: float  # Timestamp
    latency_ms: float  # Network latency


class ClusterNode:
    """
    Represents a node in the QWAMOS cluster.

    Features:
    - Node identity management
    - Peer discovery
    - Resource advertisement
    - Heartbeat mechanism
    - Secure communication (PQC-ready)
    """

    def __init__(self, cluster_id: str, role: NodeRole = NodeRole.WORKER,
                 config_dir: Optional[str] = None):
        """
        Initialize cluster node.

        Args:
            cluster_id: Cluster identifier
            role: Node role
            config_dir: Configuration directory
        """
        if config_dir is None:
            config_dir = os.path.expanduser("~/.qwamos/cluster")

        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Node identity
        self.identity = self._load_or_create_identity(cluster_id, role)

        # Peer nodes
        self.peers: Dict[str, PeerNode] = {}

        # Node resources
        self.resources = self._detect_node_resources()

        # Heartbeat interval
        self.heartbeat_interval = 10.0  # seconds

        # Last heartbeat time
        self.last_heartbeat = time.time()

    def _load_or_create_identity(self, cluster_id: str, role: NodeRole) -> NodeIdentity:
        """
        Load existing identity or create new one.

        Args:
            cluster_id: Cluster identifier
            role: Node role

        Returns:
            NodeIdentity
        """
        identity_file = self.config_dir / "node_identity.json"

        if identity_file.exists():
            with open(identity_file, 'r') as f:
                data = json.load(f)

            # Decode public key
            public_key = bytes.fromhex(data['public_key'])

            return NodeIdentity(
                node_id=data['node_id'],
                hostname=data['hostname'],
                ip_address=data['ip_address'],
                public_key=public_key,
                role=NodeRole(data['role']),
                cluster_id=data['cluster_id']
            )

        # Create new identity
        node_id = self._generate_node_id()
        hostname = socket.gethostname()
        ip_address = self._get_local_ip()

        # Generate key pair (using secrets for demo, would be Kyber-1024 in production)
        public_key, private_key = self._generate_keypair()

        identity = NodeIdentity(
            node_id=node_id,
            hostname=hostname,
            ip_address=ip_address,
            public_key=public_key,
            role=role,
            cluster_id=cluster_id
        )

        # Save identity
        self._save_identity(identity, private_key)

        return identity

    def _generate_node_id(self) -> str:
        """Generate unique node identifier."""
        return f"node-{secrets.token_hex(16)}"

    def _get_local_ip(self) -> str:
        """Get local IP address."""
        try:
            # Connect to external address to get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def _generate_keypair(self) -> Tuple[bytes, bytes]:
        """
        Generate key pair for node authentication.

        Returns:
            (public_key, private_key)
        """
        # In production, this would be Kyber-1024
        # For now, use ECDH (Curve25519) via secrets
        from Crypto.PublicKey import ECC

        private_key = ECC.generate(curve='curve25519')
        public_key = private_key.public_key()

        # Serialize
        private_bytes = private_key.export_key(format='PEM').encode('utf-8')
        public_bytes = public_key.export_key(format='PEM').encode('utf-8')

        return public_bytes, private_bytes

    def _save_identity(self, identity: NodeIdentity, private_key: bytes):
        """
        Save node identity to disk.

        Args:
            identity: NodeIdentity
            private_key: Private key bytes
        """
        identity_file = self.config_dir / "node_identity.json"
        private_key_file = self.config_dir / "node_private_key.pem"

        # Save identity
        data = {
            'node_id': identity.node_id,
            'hostname': identity.hostname,
            'ip_address': identity.ip_address,
            'public_key': identity.public_key.hex(),
            'role': identity.role.value,
            'cluster_id': identity.cluster_id
        }

        with open(identity_file, 'w') as f:
            json.dump(data, f, indent=2)

        # Save private key
        with open(private_key_file, 'wb') as f:
            f.write(private_key)

        # Set permissions
        os.chmod(identity_file, 0o600)
        os.chmod(private_key_file, 0o600)

    def _detect_node_resources(self) -> NodeResources:
        """
        Detect node resource capabilities.

        Returns:
            NodeResources
        """
        try:
            import psutil

            cpu_cores = psutil.cpu_count(logical=False) or 4
            memory_mb = psutil.virtual_memory().total // (1024 * 1024)

            # Estimate storage
            disk = psutil.disk_usage('/')
            storage_gb = disk.total // (1024 * 1024 * 1024)

        except:
            cpu_cores = 4
            memory_mb = 4096
            storage_gb = 64

        # Check for GPU
        gpu_available = False
        try:
            # Check if GPU manager is available
            import sys
            sys.path.insert(0, str(Path.home() / "QWAMOS" / "hypervisor"))
            from gpu_manager import GPUManager

            gpu_mgr = GPUManager()
            gpu_available = gpu_mgr.capabilities.vulkan_supported or \
                          gpu_mgr.capabilities.opengl_version is not None
        except:
            pass

        return NodeResources(
            cpu_cores=cpu_cores,
            memory_mb=memory_mb,
            storage_gb=storage_gb,
            gpu_available=gpu_available,
            network_bandwidth_mbps=1000  # Assume Gigabit
        )

    def add_peer(self, peer_identity: NodeIdentity, peer_resources: NodeResources):
        """
        Add a peer node to the cluster.

        Args:
            peer_identity: Peer node identity
            peer_resources: Peer node resources
        """
        peer = PeerNode(
            identity=peer_identity,
            resources=peer_resources,
            status=NodeStatus.ONLINE,
            last_seen=time.time(),
            latency_ms=0.0
        )

        self.peers[peer_identity.node_id] = peer

        print(f"✅ Added peer node: {peer_identity.node_id} ({peer_identity.hostname})")

    def remove_peer(self, node_id: str):
        """
        Remove a peer node.

        Args:
            node_id: Node ID to remove
        """
        if node_id in self.peers:
            del self.peers[node_id]
            print(f"Removed peer node: {node_id}")

    def get_peer(self, node_id: str) -> Optional[PeerNode]:
        """
        Get information about a peer node.

        Args:
            node_id: Node ID

        Returns:
            PeerNode or None
        """
        return self.peers.get(node_id)

    def list_peers(self) -> List[PeerNode]:
        """
        List all peer nodes.

        Returns:
            List of PeerNode
        """
        return list(self.peers.values())

    def send_heartbeat(self):
        """Send heartbeat to all peers."""
        current_time = time.time()

        if current_time - self.last_heartbeat >= self.heartbeat_interval:
            # Send heartbeat (would be over network in production)
            heartbeat_data = {
                'node_id': self.identity.node_id,
                'timestamp': current_time,
                'status': 'online',
                'resources': asdict(self.resources)
            }

            # Update last heartbeat time
            self.last_heartbeat = current_time

            return heartbeat_data

        return None

    def receive_heartbeat(self, node_id: str, heartbeat_data: dict):
        """
        Process heartbeat from a peer.

        Args:
            node_id: Node ID
            heartbeat_data: Heartbeat data
        """
        if node_id in self.peers:
            peer = self.peers[node_id]
            peer.last_seen = heartbeat_data['timestamp']
            peer.status = NodeStatus.ONLINE

    def check_peer_health(self):
        """Check health of all peers and mark offline if needed."""
        current_time = time.time()
        timeout = 30.0  # 30 seconds timeout

        for peer in self.peers.values():
            if current_time - peer.last_seen > timeout:
                if peer.status == NodeStatus.ONLINE:
                    peer.status = NodeStatus.OFFLINE
                    print(f"⚠️  Peer {peer.identity.node_id} marked offline")

    def get_cluster_summary(self) -> Dict:
        """
        Get cluster summary.

        Returns:
            Dictionary with cluster information
        """
        total_cpu = self.resources.cpu_cores
        total_memory = self.resources.memory_mb
        total_storage = self.resources.storage_gb
        online_peers = 0

        for peer in self.peers.values():
            total_cpu += peer.resources.cpu_cores
            total_memory += peer.resources.memory_mb
            total_storage += peer.resources.storage_gb

            if peer.status == NodeStatus.ONLINE:
                online_peers += 1

        return {
            'cluster_id': self.identity.cluster_id,
            'total_nodes': len(self.peers) + 1,
            'online_nodes': online_peers + 1,
            'coordinator': self.identity.node_id if self.identity.role == NodeRole.COORDINATOR else None,
            'total_resources': {
                'cpu_cores': total_cpu,
                'memory_mb': total_memory,
                'storage_gb': total_storage
            }
        }

    def print_cluster_status(self):
        """Print cluster status in human-readable format."""
        print(f"\n{'='*70}")
        print(f"QWAMOS Cluster Status")
        print(f"{'='*70}")
        print(f"Cluster ID:   {self.identity.cluster_id}")
        print(f"This Node:    {self.identity.node_id}")
        print(f"  Hostname:   {self.identity.hostname}")
        print(f"  IP:         {self.identity.ip_address}")
        print(f"  Role:       {self.identity.role.value.upper()}")
        print(f"\nNode Resources:")
        print(f"  CPU:        {self.resources.cpu_cores} cores")
        print(f"  Memory:     {self.resources.memory_mb} MB")
        print(f"  Storage:    {self.resources.storage_gb} GB")
        print(f"  GPU:        {'✅ Available' if self.resources.gpu_available else '❌ Not available'}")

        print(f"\nPeer Nodes ({len(self.peers)}):")
        if self.peers:
            for peer in self.peers.values():
                status_icon = "✅" if peer.status == NodeStatus.ONLINE else "❌"
                print(f"\n  {status_icon} {peer.identity.node_id}")
                print(f"     Hostname:  {peer.identity.hostname}")
                print(f"     IP:        {peer.identity.ip_address}")
                print(f"     Role:      {peer.identity.role.value}")
                print(f"     Status:    {peer.status.value}")
                print(f"     CPU:       {peer.resources.cpu_cores} cores")
                print(f"     Memory:    {peer.resources.memory_mb} MB")
        else:
            print("  No peer nodes")

        summary = self.get_cluster_summary()
        print(f"\nCluster Total:")
        print(f"  Nodes:      {summary['total_nodes']} ({summary['online_nodes']} online)")
        print(f"  CPU:        {summary['total_resources']['cpu_cores']} cores")
        print(f"  Memory:     {summary['total_resources']['memory_mb']} MB")
        print(f"  Storage:    {summary['total_resources']['storage_gb']} GB")
        print(f"{'='*70}\n")


def main():
    """Demo and testing."""
    print("="*70)
    print("QWAMOS Cluster Node - Demo")
    print("="*70)

    # Create a coordinator node
    print("\n1. Creating coordinator node...")
    coordinator = ClusterNode(
        cluster_id="qwamos-test-cluster",
        role=NodeRole.COORDINATOR
    )

    coordinator.print_cluster_status()

    # Simulate adding a peer node
    print("\n2. Simulating peer node join...")

    peer_identity = NodeIdentity(
        node_id="node-peer001",
        hostname="qwamos-worker-1",
        ip_address="192.168.1.101",
        public_key=b"mock_public_key",
        role=NodeRole.WORKER,
        cluster_id="qwamos-test-cluster"
    )

    peer_resources = NodeResources(
        cpu_cores=8,
        memory_mb=8192,
        storage_gb=128,
        gpu_available=True,
        network_bandwidth_mbps=1000
    )

    coordinator.add_peer(peer_identity, peer_resources)
    coordinator.print_cluster_status()

    # Simulate heartbeat
    print("\n3. Simulating heartbeat...")
    heartbeat = coordinator.send_heartbeat()
    if heartbeat:
        print(f"   Sent heartbeat: {heartbeat['node_id']} at {heartbeat['timestamp']}")

    print("\n" + "="*70)
    print("✅ Cluster node operational")
    print("="*70)


if __name__ == "__main__":
    main()
