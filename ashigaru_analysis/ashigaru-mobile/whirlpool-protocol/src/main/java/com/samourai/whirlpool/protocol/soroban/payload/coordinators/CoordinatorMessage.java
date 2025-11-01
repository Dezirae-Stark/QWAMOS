package com.samourai.whirlpool.protocol.soroban.payload.coordinators;

import com.samourai.soroban.client.AbstractSorobanPayloadable;
import java.util.Collection;

public class CoordinatorMessage extends AbstractSorobanPayloadable {
  public CoordinatorInfo coordinator;
  public Collection<PoolInfo> pools;
  public SorobanInfo sorobanInfo;

  public CoordinatorMessage() {}

  public CoordinatorMessage(
      CoordinatorInfo coordinator, Collection<PoolInfo> pools, SorobanInfo sorobanInfo) {
    this.coordinator = coordinator;
    this.pools = pools;
    this.sorobanInfo = sorobanInfo;
  }
}
