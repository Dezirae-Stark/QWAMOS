package com.samourai.whirlpool.protocol.soroban.payload.coordinators;

public class CoordinatorInfo {
  public String name;
  public long priority;

  public CoordinatorInfo() {}

  public CoordinatorInfo(String name, long priority) {
    this.name = name;
    this.priority = priority;
  }
}
