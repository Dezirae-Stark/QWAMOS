package com.samourai.xmanager.protocol.rest;

import javax.validation.constraints.NotEmpty;

public class AddressRequest {
  @NotEmpty public String id;

  public AddressRequest() {}

  public AddressRequest(String id) {
    this.id = id;
  }
}
