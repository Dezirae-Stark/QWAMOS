package com.samourai.xmanager.protocol;

public enum XManagerService {
  WHIRLPOOL(
      "bc1qxya59zn6fgenfls0pedt0xqkagd33fcfc5s04n", "tb1q6m3urxjc8j2l8fltqj93jarmzn0975nnxuymnx"),
  WHIRLPOOL_SPARROW(
      "bc1qctv9kxux6r3reu4uj0glh5gwne2hewy0pfpv79", "tb1qh4w64gvlkpfrhre503ed8unzzstd5vyl9x0am9"),
  WHIRLPOOL_FREESIDE(
      "bc1qent9f0wlphtmgp5t9x3wzt440mq5rlup6htv8r", "tb1qx79uw4m79ecwwr2s70wvj66svskzaqckd4w96m"),
  WHIRLPOOL_HEXA(
      "bc1q56p8t7pfahvffzumkmsd7r6ex5746a0yna9nax", "tb1q2dtjt9f9qvj2gctu0qk28w7mlkvglu8p6ghaqx"),
  WHIRLPOOL_FOUNDATION(
      "bc1qyzfg4565lf4wcqvt4hahza47ednt5j4jdl0dh2", "tb1qjxdy8v7kl6d363x690teag9ag5ms90mlgnqh7y"),
  WHIRLPOOL_STACKWALLET(
      "bc1q7a7ddlvpta2kxzl6aqfu7wuccc05y4f2qfanpu", "tb1q7j34f30cmqu6fxamr6vauym7hrludgyz7tmx0k"),
  SAAS("bc1qsnefhrmd8gs6a4j7fzxfy4ay52j78agl6rsw36", "tb1q6y29zmgw2ajgmqrnpqrf0ejtyrqsh3ehd6wjlk"),
  RICOCHET(
      "bc1qptv26ag03um6dhvcrfjh29wlez64mdufw77z8g", "tb1q6y29zmgw2ajgmqrnpqrf0ejtyrqsh3ehd6wjlk"),
  BIP47("bc1quq8h89h6j9f6nv5fyqjjav2auzah799lq2j9fa", "tb1q6y29zmgw2ajgmqrnpqrf0ejtyrqsh3ehd6wjlk"),
  OXT_RESEARCH(
      "bc1qj2sac3nvaettzz5egmtnk223vjrey2hxyx9j9k", "tb1q6y29zmgw2ajgmqrnpqrf0ejtyrqsh3ehd6wjlk"),
  STONEWALL(
      "bc1q9fz5u4g28zh5lv43hf5v642pl8a4d3e8t7gz0f", "tb1qgecrwnq4mek745xxmy3sc3404wrnay3f5p3uuh");

  private String defaultAddressMainnet;
  private String defaultAddressTestnet;

  private XManagerService(String defaultAddressMainnet, String defaultAddressTestnet) {
    this.defaultAddressMainnet = defaultAddressMainnet;
    this.defaultAddressTestnet = defaultAddressTestnet;
  }

  public String getDefaultAddressMainnet() {
    return defaultAddressMainnet;
  }

  public String getDefaultAddressTestnet() {
    return defaultAddressTestnet;
  }

  public String getDefaultAddress(boolean testnet) {
    return testnet ? defaultAddressTestnet : defaultAddressMainnet;
  }
}
