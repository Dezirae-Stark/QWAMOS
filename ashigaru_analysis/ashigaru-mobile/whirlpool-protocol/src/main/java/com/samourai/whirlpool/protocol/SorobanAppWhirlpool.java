package com.samourai.whirlpool.protocol;

import com.samourai.soroban.client.endpoint.SorobanApp;
import com.samourai.soroban.client.endpoint.meta.typed.SorobanEndpointTyped;
import com.samourai.soroban.client.endpoint.meta.wrapper.SorobanWrapperMetaAuthWithSamouraiSender;
import com.samourai.soroban.client.endpoint.meta.wrapper.SorobanWrapperMetaFilterSender;
import com.samourai.soroban.client.endpoint.meta.wrapper.SorobanWrapperMetaNonce;
import com.samourai.soroban.client.endpoint.meta.wrapper.SorobanWrapperMetaSignWithSender;
import com.samourai.soroban.client.endpoint.wrapper.SorobanWrapper;
import com.samourai.soroban.client.rpc.RpcMode;
import com.samourai.soroban.protocol.payload.AckResponse;
import com.samourai.wallet.bip47.rpc.PaymentCode;
import com.samourai.wallet.constants.SamouraiNetwork;
import com.samourai.whirlpool.protocol.soroban.payload.coordinators.CoordinatorMessage;
import com.samourai.whirlpool.protocol.soroban.payload.mix.*;
import com.samourai.whirlpool.protocol.soroban.payload.registerInput.RegisterInputRequest;
import com.samourai.whirlpool.protocol.soroban.payload.registerInput.RegisterInputResponse;
import com.samourai.whirlpool.protocol.soroban.payload.tx0.*;
import com.samourai.whirlpool.protocol.soroban.payload.upStatus.UpStatusMessage;

public class SorobanAppWhirlpool extends SorobanApp {
  private static final String APP_ID = "WHIRLPOOL";
  public static final String APP_VERSION = "1.0";
  private static final String DIR_COORDINATOR_TX0 = "TX0";
  private static final String DIR_COORDINATOR_REGISTER_INPUT = "REGISTER_INPUT";
  private static final String DIR_COORDINATORS = "COORDINATORS";
  private static final String DIR_MIX_STATUS = "MIX/STATUS";
  private static final String DIR_MIX_CONFIRM_INPUT = "MIX/CONFIRM_INPUT";
  private static final String DIR_MIX_REGISTER_OUTPUT = "MIX/REGISTER_OUTPUT";
  private static final String DIR_MIX_REVEAL_OUTPUT = "MIX/REVEAL_OUTPUT";
  private static final String DIR_MIX_SIGNING = "MIX/SIGNING";
  private static final String DIR_MIX_RESULT = "MIX/RESULT";
  private static final String DIR_UPSTATUS = "UPSTATUS";

  private String senderSignedBySigningAddress;

  // for client
  public SorobanAppWhirlpool(SamouraiNetwork samouraiNetwork) {
    this(samouraiNetwork, null);
  }

  // for coordinator
  public SorobanAppWhirlpool(SamouraiNetwork samouraiNetwork, String senderSignedBySigningAddress) {
    super(samouraiNetwork, APP_ID, APP_VERSION);
    this.senderSignedBySigningAddress = senderSignedBySigningAddress;
  }

  // for tests
  public SorobanAppWhirlpool(
      SamouraiNetwork samouraiNetwork, String senderSignedBySigningAddress, String appVersion) {
    super(samouraiNetwork, APP_ID, appVersion);
    this.senderSignedBySigningAddress = senderSignedBySigningAddress;
  }

  public SorobanEndpointTyped getEndpointTx0(PaymentCode paymentCodeCoordinator, String poolId) {
    String dir = getDir(DIR_COORDINATOR_TX0 + "/" + poolId);
    return new SorobanEndpointTyped(
            dir,
            RpcMode.FAST,
            new SorobanWrapper[] {new SorobanWrapperMetaNonce()},
            new Class[] {Tx0DataRequest.class, Tx0PushRequest.class},
            new Class[] {
              Tx0DataResponse.class, Tx0PushResponseSuccess.class, Tx0PushResponseError.class
            })
        .setEncryptToWithSender(paymentCodeCoordinator);
  }

  public SorobanEndpointTyped getEndpointRegisterInput(
      PaymentCode paymentCodeCoordinator, String poolId, boolean liquidity) {
    String dir = getDir(DIR_COORDINATOR_REGISTER_INPUT + "/" + poolId + "/" + liquidity);
    SorobanEndpointTyped endpoint =
        new SorobanEndpointTyped(
                dir,
                RpcMode.SHORT, // we want inputs to expire quickly
                new SorobanWrapper[] {new SorobanWrapperMetaNonce()},
                new Class[] {RegisterInputRequest.class},
                new Class[] {RegisterInputResponse.class})
            .setEncryptToWithSender(paymentCodeCoordinator);
    return endpoint;
  }

  public SorobanEndpointTyped getEndpointMixConfirmInput(
      String mixId, PaymentCode paymentCodeCoordinator) {
    String dir = getDir(DIR_MIX_CONFIRM_INPUT + "/" + mixId);
    return new SorobanEndpointTyped(
            dir,
            RpcMode.FAST,
            new SorobanWrapper[] {new SorobanWrapperMetaNonce()},
            new Class[] {ConfirmInputRequest.class},
            new Class[] {ConfirmInputResponse.class})
        .setEncryptToWithSender(paymentCodeCoordinator);
  }

  public SorobanEndpointTyped getEndpointMixRegisterOutput(
      String inputsHash, PaymentCode paymentCodeCoordinator) {
    String dir = getDir(DIR_MIX_REGISTER_OUTPUT + "/" + inputsHash);
    return new SorobanEndpointTyped(
            dir,
            RpcMode.FAST,
            new SorobanWrapper[] {new SorobanWrapperMetaNonce()},
            new Class[] {RegisterOutputRequest.class},
            new Class[] {AckResponse.class})
        .setEncryptToWithSender(paymentCodeCoordinator);
  }

  public SorobanEndpointTyped getEndpointMixSigning(
      String mixId, PaymentCode paymentCodeCoordinator) {
    String dir = getDir(DIR_MIX_SIGNING + "/" + mixId);
    return new SorobanEndpointTyped(
            dir,
            RpcMode.FAST,
            new SorobanWrapper[] {new SorobanWrapperMetaNonce()},
            new Class[] {SigningRequest.class},
            new Class[] {AckResponse.class})
        .setEncryptToWithSender(paymentCodeCoordinator);
  }

  public SorobanEndpointTyped getEndpointMixRevealOutput(
      String mixId, PaymentCode paymentCodeCoordinator) {
    String dir = getDir(DIR_MIX_REVEAL_OUTPUT + "/" + mixId);
    return new SorobanEndpointTyped(
            dir,
            RpcMode.FAST,
            new SorobanWrapper[] {new SorobanWrapperMetaNonce()},
            new Class[] {RevealOutputRequest.class},
            new Class[] {AckResponse.class})
        .setEncryptToWithSender(paymentCodeCoordinator);
  }

  public SorobanEndpointTyped getEndpointMixStatus(
      String mixId, PaymentCode paymentCodeCoordinator) {
    String dir = getDir(DIR_MIX_STATUS + "/" + mixId);
    return new SorobanEndpointTyped(
            dir,
            RpcMode.FAST,
            new SorobanWrapper[] {new SorobanWrapperMetaNonce()},
            new Class[] {MixStatusRequest.class},
            new Class[] {
              MixStatusResponseConfirmInput.class,
              MixStatusResponseRegisterOutput.class,
              MixStatusResponseSigning.class,
              MixStatusResponseRevealOutput.class,
              MixStatusResponseFail.class,
              MixStatusResponseSuccess.class,
            })
        .setEncryptToWithSender(paymentCodeCoordinator);
  }

  public SorobanEndpointTyped getEndpointMixResult(
      String mixId, PaymentCode paymentCodeCoordinator) {
    String dir = getDir(DIR_MIX_RESULT + "/" + mixId);
    return new SorobanEndpointTyped(
        dir,
        RpcMode.SHORT,
        new SorobanWrapper[] {
          new SorobanWrapperMetaSignWithSender(),
          new SorobanWrapperMetaFilterSender(paymentCodeCoordinator)
        },
        new Class[] {MixStatusResponseSuccess.class, MixStatusResponseFail.class},
        new Class[] {});
  }

  public SorobanEndpointTyped getEndpointCoordinators() {
    SorobanWrapperMetaAuthWithSamouraiSender authWrapper;
    if (senderSignedBySigningAddress != null) {
      // coordinator authenticates with samourai key
      authWrapper =
          new SorobanWrapperMetaAuthWithSamouraiSender(
              samouraiNetwork, senderSignedBySigningAddress);
    } else {
      // client validates auth against samourai address
      authWrapper = new SorobanWrapperMetaAuthWithSamouraiSender(samouraiNetwork);
    }
    String dir = getDir(DIR_COORDINATORS);
    SorobanEndpointTyped endpoint =
        new SorobanEndpointTyped(
            dir,
            RpcMode.NORMAL,
            new SorobanWrapper[] {
              authWrapper, new SorobanWrapperMetaSignWithSender(), new SorobanWrapperMetaNonce()
            },
            new Class[] {CoordinatorMessage.class});
    endpoint.setNoReplay(false);
    return endpoint;
  }

  // only used by coordinator
  public SorobanEndpointTyped getEndpointUpStatus(
      PaymentCode paymentCodeCoordinator, Long checkId) {
    String dir = getDir(DIR_UPSTATUS + "/" + paymentCodeCoordinator.toString() + "/" + checkId);
    return new SorobanEndpointTyped(
        dir,
        RpcMode.SHORT,
        new SorobanWrapper[] {
          new SorobanWrapperMetaNonce(), new SorobanWrapperMetaSignWithSender()
        },
        new Class[] {UpStatusMessage.class});
  }
}
