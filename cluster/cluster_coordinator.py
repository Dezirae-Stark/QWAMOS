#!/usr/bin/env python3
"""
QWAMOS Cluster Coordinator
Phase XVI: Secure Cluster Mode

Cluster coordination and management:
- Cluster-wide resource management
- VM placement decisions
- Load balancing
- Failover coordination
- State synchronization

Author: QWAMOS Project
License: MIT
"""

import time
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Add cluster to path
sys.path.insert(0, str(Path(__file__).parent))

from cluster_node import ClusterNode, NodeRole, NodeStatus, PeerNode


class PlacementStrategy(Enum):
    """VM placement strategies."""
    LEAST_LOADED = "least_loaded"  # Place on node with most free resources
    ROUND_ROBIN = "round_robin"  # Rotate placements
    AFFINITY = "affinity"  # Keep related VMs together
    ANTI_AFFINITY = "anti_affinity"  # Spread VMs across nodes


@dataclass
class VMPlacement:
    """VM placement decision."""
    vm_name: str
    node_id: str
    reason: str


class ClusterCoordinator:
    """
    Coordinates cluster-wide operations.

    Features:
    - Resource-aware VM placement
    - Load balancing
    - Failover management
    - Cluster state synchronization
    """

    def __init__(self, node: ClusterNode):
        """
        Initialize cluster coordinator.

        Args:
            node: ClusterNode instance (should be coordinator role)
        """
        self.node = node

        if self.node.identity.role != NodeRole.COORDINATOR:
            raise ValueError("Node must have COORDINATOR role")

        # VM placements
        self.vm_placements: Dict[str, VMPlacement] = {}

        # Placement strategy
        self.placement_strategy = PlacementStrategy.LEAST_LOADED

        # Round-robin counter
        self.rr_counter = 0

    def place_vm(self, vm_name: str, required_cpu: int = 2,
                required_memory_mb: int = 1024,
                required_storage_gb: int = 10,
                strategy: Optional[PlacementStrategy] = None) -> VMPlacement:
        """
        Determine optimal node for VM placement.

        Args:
            vm_name: VM name
            required_cpu: Required CPU cores
            required_memory_mb: Required memory in MB
            required_storage_gb: Required storage in GB
            strategy: Placement strategy (uses default if None)

        Returns:
            VMPlacement decision
        """
        if strategy is None:
            strategy = self.placement_strategy

        # Get all online nodes (including self)
        candidates = [self.node]
        for peer in self.node.list_peers():
            if peer.status == NodeStatus.ONLINE:
                candidates.append(peer)

        if not candidates:
            # No nodes available, place on self
            placement = VMPlacement(
                vm_name=vm_name,
                node_id=self.node.identity.node_id,
                reason="No other nodes available"
            )
            self.vm_placements[vm_name] = placement
            return placement

        # Select node based on strategy
        if strategy == PlacementStrategy.LEAST_LOADED:
            selected_node = self._select_least_loaded(candidates, required_cpu,
                                                     required_memory_mb, required_storage_gb)
        elif strategy == PlacementStrategy.ROUND_ROBIN:
            selected_node = self._select_round_robin(candidates)
        else:
            # Default to least loaded
            selected_node = self._select_least_loaded(candidates, required_cpu,
                                                     required_memory_mb, required_storage_gb)

        # Get node ID
        if isinstance(selected_node, ClusterNode):
            node_id = selected_node.identity.node_id
            node_hostname = selected_node.identity.hostname
        else:  # PeerNode
            node_id = selected_node.identity.node_id
            node_hostname = selected_node.identity.hostname

        placement = VMPlacement(
            vm_name=vm_name,
            node_id=node_id,
            reason=f"Placed on {node_hostname} using {strategy.value} strategy"
        )

        self.vm_placements[vm_name] = placement
        return placement

    def _select_least_loaded(self, candidates: List, required_cpu: int,
                            required_memory_mb: int, required_storage_gb: int):
        """
        Select node with most available resources.

        Args:
            candidates: List of nodes
            required_cpu: Required CPU
            required_memory_mb: Required memory
            required_storage_gb: Required storage

        Returns:
            Selected node
        """
        best_node = None
        best_score = -1

        for candidate in candidates:
            # Get resources
            if isinstance(candidate, ClusterNode):
                resources = candidate.resources
            else:  # PeerNode
                resources = candidate.resources

            # Check if resources sufficient
            if (resources.cpu_cores >= required_cpu and
                resources.memory_mb >= required_memory_mb and
                resources.storage_gb >= required_storage_gb):

                # Calculate available resources score
                score = (resources.cpu_cores * 1000 +
                        resources.memory_mb +
                        resources.storage_gb * 100)

                if score > best_score:
                    best_score = score
                    best_node = candidate

        if best_node is None:
            # No node meets requirements, use first candidate
            return candidates[0]

        return best_node

    def _select_round_robin(self, candidates: List):
        """
        Select node using round-robin.

        Args:
            candidates: List of nodes

        Returns:
            Selected node
        """
        selected = candidates[self.rr_counter % len(candidates)]
        self.rr_counter += 1
        return selected

    def migrate_vm(self, vm_name: str, target_node_id: str) -> bool:
        """
        Migrate VM to target node.

        Args:
            vm_name: VM name
            target_node_id: Target node ID

        Returns:
            True if migration initiated
        """
        # Check if VM exists in placements
        if vm_name not in self.vm_placements:
            print(f"❌ VM {vm_name} not found in cluster")
            return False

        current_placement = self.vm_placements[vm_name]

        # Check if target node exists and is online
        target_node = None
        if target_node_id == self.node.identity.node_id:
            target_node = self.node
        else:
            peer = self.node.get_peer(target_node_id)
            if peer and peer.status == NodeStatus.ONLINE:
                target_node = peer

        if target_node is None:
            print(f"❌ Target node {target_node_id} not available")
            return False

        # Update placement
        print(f"🔄 Migrating {vm_name} from {current_placement.node_id} to {target_node_id}")

        new_placement = VMPlacement(
            vm_name=vm_name,
            node_id=target_node_id,
            reason=f"Manual migration from {current_placement.node_id}"
        )

        self.vm_placements[vm_name] = new_placement

        print(f"✅ VM migration initiated")
        return True

    def balance_load(self):
        """Rebalance VMs across cluster nodes."""
        print("🔄 Balancing cluster load...")

        # Get all VMs
        vms = list(self.vm_placements.keys())

        # Recalculate placements
        for vm_name in vms:
            new_placement = self.place_vm(
                vm_name,
                strategy=PlacementStrategy.LEAST_LOADED
            )

            old_placement = self.vm_placements.get(vm_name)
            if old_placement and new_placement.node_id != old_placement.node_id:
                print(f"  Moving {vm_name}: {old_placement.node_id} → {new_placement.node_id}")

        print("✅ Load balancing complete")

    def handle_node_failure(self, failed_node_id: str):
        """
        Handle node failure by migrating its VMs.

        Args:
            failed_node_id: ID of failed node
        """
        print(f"⚠️  Handling failure of node {failed_node_id}")

        # Find VMs on failed node
        affected_vms = [
            vm_name for vm_name, placement in self.vm_placements.items()
            if placement.node_id == failed_node_id
        ]

        if not affected_vms:
            print("   No VMs affected")
            return

        print(f"   Migrating {len(affected_vms)} VMs...")

        # Migrate VMs to other nodes
        for vm_name in affected_vms:
            new_placement = self.place_vm(vm_name)
            print(f"   ✅ {vm_name} → {new_placement.node_id}")

        print("✅ Failover complete")

    def get_cluster_load(self) -> Dict:
        """
        Get cluster load distribution.

        Returns:
            Dictionary with load information
        """
        load_by_node = {}

        # Count VMs per node
        for placement in self.vm_placements.values():
            node_id = placement.node_id
            load_by_node[node_id] = load_by_node.get(node_id, 0) + 1

        return load_by_node

    def print_cluster_state(self):
        """Print cluster state."""
        print(f"\n{'='*70}")
        print(f"Cluster State")
        print(f"{'='*70}")

        summary = self.node.get_cluster_summary()
        print(f"Cluster ID:     {summary['cluster_id']}")
        print(f"Total Nodes:    {summary['total_nodes']} ({summary['online_nodes']} online)")
        print(f"Coordinator:    {self.node.identity.node_id}")

        print(f"\nVM Placements ({len(self.vm_placements)}):")
        if self.vm_placements:
            for vm_name, placement in self.vm_placements.items():
                print(f"  {vm_name} → {placement.node_id}")
                print(f"    Reason: {placement.reason}")
        else:
            print("  No VMs placed")

        load = self.get_cluster_load()
        if load:
            print(f"\nLoad Distribution:")
            for node_id, vm_count in load.items():
                print(f"  {node_id}: {vm_count} VMs")

        print(f"{'='*70}\n")


def main():
    """Demo and testing."""
    print("="*70)
    print("QWAMOS Cluster Coordinator - Demo")
    print("="*70)

    # Create coordinator
    print("\n1. Creating cluster coordinator...")
    node = ClusterNode(
        cluster_id="qwamos-demo-cluster",
        role=NodeRole.COORDINATOR
    )

    coordinator = ClusterCoordinator(node)

    # Add some peer nodes
    print("\n2. Adding peer nodes...")
    from cluster_node import NodeIdentity, NodeResources

    for i in range(3):
        peer_identity = NodeIdentity(
            node_id=f"node-worker{i:02d}",
            hostname=f"qwamos-worker-{i}",
            ip_address=f"192.168.1.{101+i}",
            public_key=b"mock_key",
            role=NodeRole.WORKER,
            cluster_id="qwamos-demo-cluster"
        )

        peer_resources = NodeResources(
            cpu_cores=8,
            memory_mb=8192,
            storage_gb=128,
            gpu_available=True,
            network_bandwidth_mbps=1000
        )

        node.add_peer(peer_identity, peer_resources)

    # Place some VMs
    print("\n3. Placing VMs on cluster...")
    vms = [
        ("web-server-vm", 2, 2048, 20),
        ("database-vm", 4, 4096, 100),
        ("app-vm", 2, 1024, 10),
        ("cache-vm", 1, 512, 5)
    ]

    for vm_name, cpu, mem, storage in vms:
        placement = coordinator.place_vm(vm_name, cpu, mem, storage)
        print(f"  ✅ {vm_name} placed on {placement.node_id}")

    # Show cluster state
    coordinator.print_cluster_state()

    # Simulate node failure
    print("\n4. Simulating node failure...")
    failed_node = "node-worker00"
    coordinator.handle_node_failure(failed_node)

    coordinator.print_cluster_state()

    print("\n" + "="*70)
    print("✅ Cluster coordinator operational")
    print("="*70)


if __name__ == "__main__":
    main()
