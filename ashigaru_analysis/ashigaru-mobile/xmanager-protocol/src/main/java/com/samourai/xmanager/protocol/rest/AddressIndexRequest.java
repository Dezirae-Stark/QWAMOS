package com.samourai.xmanager.protocol.rest;

import javax.validation.constraints.NotEmpty;

public class AddressIndexRequest {
  @NotEmpty public String id;

  public AddressIndexRequest() {}

  public AddressIndexRequest(String id) {
    this.id = id;
  }
}
