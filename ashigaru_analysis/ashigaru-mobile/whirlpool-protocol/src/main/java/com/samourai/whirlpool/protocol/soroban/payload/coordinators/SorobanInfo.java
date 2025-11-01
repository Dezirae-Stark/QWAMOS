package com.samourai.whirlpool.protocol.soroban.payload.coordinators;

import java.util.Collection;

public class SorobanInfo {
  public Collection<String> urlsClear;
  public Collection<String> urlsOnion;

  public SorobanInfo() {}

  public SorobanInfo(Collection<String> urlsClear, Collection<String> urlsOnion) {
    this.urlsClear = urlsClear;
    this.urlsOnion = urlsOnion;
  }
}
