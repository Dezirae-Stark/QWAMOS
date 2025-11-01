package com.samourai.whirlpool.protocol.soroban;

import com.samourai.soroban.client.endpoint.meta.typed.SorobanEndpointTyped;
import com.samourai.soroban.client.endpoint.meta.typed.SorobanItemTyped;
import com.samourai.soroban.client.rpc.RpcSession;
import com.samourai.soroban.client.rpc.RpcSessionApi;
import com.samourai.wallet.bip47.rpc.PaymentCode;
import com.samourai.wallet.util.AsyncUtil;
import com.samourai.whirlpool.protocol.SorobanAppWhirlpool;
import com.samourai.whirlpool.protocol.soroban.payload.beans.MixStatus;
import com.samourai.whirlpool.protocol.soroban.payload.mix.*;
import java.lang.invoke.MethodHandles;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class WhirlpoolApiClientMix extends RpcSessionApi {
  private static final Logger log = LoggerFactory.getLogger(MethodHandles.lookup().lookupClass());
  private static final AsyncUtil asyncUtil = AsyncUtil.getInstance();

  private String mixId;
  private SorobanEndpointTyped endpointMixStatus;
  private SorobanEndpointTyped endpointMixResult;
  private SorobanEndpointTyped endpointMixConfirmInput;
  private SorobanEndpointTyped endpointMixSigning;
  private SorobanEndpointTyped endpointMixRevealOutput;

  public WhirlpoolApiClientMix(
      RpcSession rpcSession,
      SorobanAppWhirlpool app,
      String mixId,
      PaymentCode paymentCodeCoordinator) {
    super(rpcSession);
    this.mixId = mixId;

    // keep endpoint instances all-over-the-mix for noReplay
    this.endpointMixStatus = app.getEndpointMixStatus(mixId, paymentCodeCoordinator);
    this.endpointMixResult = app.getEndpointMixResult(mixId, paymentCodeCoordinator);
    this.endpointMixConfirmInput = app.getEndpointMixConfirmInput(mixId, paymentCodeCoordinator);
    this.endpointMixSigning = app.getEndpointMixSigning(mixId, paymentCodeCoordinator);
    this.endpointMixRevealOutput = app.getEndpointMixRevealOutput(mixId, paymentCodeCoordinator);
  }

  public AbstractMixStatusResponse waitMixStatus() throws Exception {
    if (log.isDebugEnabled()) {
      log.debug("[mix " + mixId + "] => mixStatus");
    }

    // send request
    MixStatusRequest request = new MixStatusRequest();
    SorobanItemTyped response =
        endpointMixStatus.loopSendAndWaitReply(
            rpcSession, request, WhirlpoolApiClient.TIMEOUT_MIX_STATUS);

    // throw on SorobanErrorMessage response
    response.throwOnSorobanErrorMessage();

    return (AbstractMixStatusResponse) response.read(Class.forName(response.getType()));
  }

  public AbstractMixStatusResponse waitMixResult() throws Exception {
    if (log.isDebugEnabled()) {
      log.debug("[mix " + mixId + "] => mixResult");
    }

    // fetch mix result (wait up to SIGNING timeout)
    SorobanItemTyped response =
        endpointMixResult.loopWaitAny(rpcSession, MixStatus.SIGNING.getTimeoutMs());

    return (AbstractMixStatusResponse) response.read(Class.forName(response.getType()));
  }

  public Optional<AbstractMixStatusResponse> findMixResult() throws Exception {
    if (log.isDebugEnabled()) {
      log.debug("[mix " + mixId + "] => mixResult");
    }

    // fetch mix result
    Optional<SorobanItemTyped> mixResult =
        asyncUtil.blockingGet(
            rpcSession.withSorobanClient(
                sorobanClient -> endpointMixResult.findAny(sorobanClient)));
    if (!mixResult.isPresent()) {
      return Optional.empty();
    }
    return (Optional<AbstractMixStatusResponse>)
        mixResult.get().readOn(Class.forName(mixResult.get().getType()));
  }

  public ConfirmInputResponse confirmInput(ConfirmInputRequest request) throws Exception {
    if (log.isDebugEnabled()) {
      log.debug("[mix " + mixId + "] => confirmInput");
    }
    return endpointMixConfirmInput.loopSendAndWaitReplyObject(
        rpcSession, request, ConfirmInputResponse.class, MixStatus.CONFIRM_INPUT.getTimeoutMs());
  }

  public void signing(SigningRequest request) throws Exception {
    if (log.isDebugEnabled()) {
      log.debug("[mix " + mixId + "] => signing");
    }
    endpointMixSigning.loopSendAndWaitReplyAck(
        rpcSession, request, MixStatus.SIGNING.getTimeoutMs());
  }

  public void revealOutput(RevealOutputRequest request) throws Exception {
    if (log.isDebugEnabled()) {
      log.debug("[mix " + mixId + "] => revealing output");
    }
    endpointMixRevealOutput.loopSendAndWaitReplyAck(
        rpcSession, request, MixStatus.REVEAL_OUTPUT.getTimeoutMs());
  }
}
