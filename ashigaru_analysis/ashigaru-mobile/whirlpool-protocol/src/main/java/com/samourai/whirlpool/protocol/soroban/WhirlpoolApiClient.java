package com.samourai.whirlpool.protocol.soroban;

import com.samourai.soroban.client.endpoint.meta.typed.SorobanEndpointTyped;
import com.samourai.soroban.client.endpoint.meta.typed.SorobanItemTyped;
import com.samourai.soroban.client.endpoint.meta.wrapper.SorobanWrapperMetaSender;
import com.samourai.soroban.client.rpc.RpcSession;
import com.samourai.soroban.client.rpc.RpcSessionApi;
import com.samourai.soroban.client.rpc.RpcWalletImpl;
import com.samourai.wallet.bip47.rpc.PaymentCode;
import com.samourai.wallet.util.AsyncUtil;
import com.samourai.wallet.util.Pair;
import com.samourai.whirlpool.protocol.SorobanAppWhirlpool;
import com.samourai.whirlpool.protocol.soroban.exception.PushTxErrorException;
import com.samourai.whirlpool.protocol.soroban.payload.beans.MixStatus;
import com.samourai.whirlpool.protocol.soroban.payload.coordinators.CoordinatorMessage;
import com.samourai.whirlpool.protocol.soroban.payload.mix.*;
import com.samourai.whirlpool.protocol.soroban.payload.registerInput.RegisterInputRequest;
import com.samourai.whirlpool.protocol.soroban.payload.registerInput.RegisterInputResponse;
import com.samourai.whirlpool.protocol.soroban.payload.tx0.*;
import java.lang.invoke.MethodHandles;
import java.util.LinkedList;
import java.util.List;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class WhirlpoolApiClient extends RpcSessionApi {
  private static final Logger log = LoggerFactory.getLogger(MethodHandles.lookup().lookupClass());
  private static final AsyncUtil asyncUtil = AsyncUtil.getInstance();

  // inputs are disconnected from mix when lastSeen > TIMEOUT_MIX_STATUS
  public static final int TIMEOUT_MIX_STATUS = 90000; // 1min30

  // also used for coordinator's adding confirming input frequency
  public static final int REGISTER_INPUT_POLLING_FREQUENCY_MS = 20000; // 20s

  private SorobanAppWhirlpool app;

  public WhirlpoolApiClient(RpcSession rpcSession, SorobanAppWhirlpool app) {
    super(rpcSession);
    this.app = app;
  }

  public WhirlpoolApiClientMix createWhirlpoolApiClientMix(
      String mixId, PaymentCode coordinatorPaymentCode) {
    return new WhirlpoolApiClientMix(rpcSession, app, mixId, coordinatorPaymentCode);
  }

  public WhirlpoolApiClient createNewIdentity() throws Exception {
    RpcWalletImpl rpcWalletNew =
        (RpcWalletImpl) rpcSession.getRpcWallet().createNewIdentity(); // TODO cast
    RpcSession rpcSessionNew = rpcWalletNew.createRpcSession();
    return new WhirlpoolApiClient(rpcSessionNew, app);
  }

  public List<Pair<CoordinatorMessage, PaymentCode>> coordinatorsFetch() throws Exception {
    SorobanEndpointTyped endpoint = app.getEndpointCoordinators();
    List<Pair<CoordinatorMessage, PaymentCode>> result =
        rpcSession.withSorobanClient(
            sorobanClient ->
                asyncUtil.blockingGet(
                    endpoint
                        .getListObjectsWithMetadata(
                            sorobanClient,
                            CoordinatorMessage.class,
                            // keep last message from each coordinator
                            f -> f.distinctBySenderWithLastNonce())
                        // build list of Pair(message,sender)
                        .map(
                            list ->
                                list.stream()
                                    .map(
                                        pair ->
                                            Pair.of(
                                                pair.getLeft(),
                                                SorobanWrapperMetaSender.getSender(
                                                    pair.getRight())))
                                    .collect(Collectors.toList()))));
    if (!result.isEmpty()) {
      return result;
    }
    // no coordinator found :(
    return new LinkedList<>();
  }

  // MIX

  public RegisterInputResponse registerInput(
      RegisterInputRequest request,
      String poolId,
      boolean liquidity,
      PaymentCode paymentCodeCoordinator,
      int timeoutMs)
      throws Exception {
    if (log.isDebugEnabled()) {
      log.debug(
          "=> registerInput: "
              + request.utxoHash
              + ":"
              + request.utxoIndex
              + ", poolId="
              + poolId
              + ", liquidity="
              + liquidity
              + ", blockHeight="
              + request.blockHeight);
    }
    SorobanEndpointTyped endpoint =
        app.getEndpointRegisterInput(paymentCodeCoordinator, poolId, liquidity);

    // no need for fast resend: resend request after expiration (60s)
    endpoint.setResendFrequencyWhenNoReplyMs(endpoint.getExpirationMs());
    // no need for fast polling frequency as no InputResponse is expected quickly (10s)
    endpoint.setPollingFrequencyMs(REGISTER_INPUT_POLLING_FREQUENCY_MS / 2);

    // endpoint.resendFrequencyWhenNoReplyMs was adjusted to endpoint.expirationMs
    return endpoint.loopSendAndWaitReplyObject(
        rpcSession, request, RegisterInputResponse.class, timeoutMs);
  }

  public void registerOutput(
      RegisterOutputRequest request, String inputsHash, PaymentCode paymentCodeCoordinator)
      throws Exception {
    if (log.isDebugEnabled()) {
      log.debug("[" + inputsHash + "] => registerOutput: " + request.receiveAddress);
    }
    SorobanEndpointTyped endpoint =
        app.getEndpointMixRegisterOutput(inputsHash, paymentCodeCoordinator);
    endpoint.loopSendAndWaitReplyAck(rpcSession, request, MixStatus.REGISTER_OUTPUT.getTimeoutMs());
  }

  // TX0

  public Tx0DataResponse tx0FetchData(
      Tx0DataRequest request, PaymentCode paymentCodeCoordinator, String poolId) throws Exception {
    if (log.isDebugEnabled()) {
      log.debug("=> tx0Data");
    }
    SorobanEndpointTyped endpoint = app.getEndpointTx0(paymentCodeCoordinator, poolId);

    return endpoint.sendAndWaitReplyObject(rpcSession, request, Tx0DataResponse.class);
  }

  // throws PushTxErrorException
  public Tx0PushResponseSuccess tx0Push(Tx0PushRequest request, PaymentCode paymentCodeCoordinator)
      throws Exception {
    if (log.isDebugEnabled()) {
      log.debug("=> pushTx0");
    }
    SorobanEndpointTyped endpoint = app.getEndpointTx0(paymentCodeCoordinator, request.poolId);
    SorobanItemTyped response =
        endpoint.sendAndWaitReply(
            rpcSession,
            request,
            f -> f.filterByType(Tx0PushResponseSuccess.class, Tx0PushResponseError.class));

    if (response.isTyped(Tx0PushResponseSuccess.class)) {
      return response.read(Tx0PushResponseSuccess.class);
    }
    throw new PushTxErrorException(response.read(Tx0PushResponseError.class).pushTxError);
  }

  public SorobanAppWhirlpool getSorobanApp() {
    return app;
  }
}
