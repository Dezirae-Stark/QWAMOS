package com.samourai.whirlpool.protocol.soroban;

import com.samourai.soroban.client.SorobanClient;
import com.samourai.soroban.client.endpoint.meta.typed.SorobanEndpointTyped;
import com.samourai.soroban.client.endpoint.meta.typed.SorobanItemTyped;
import com.samourai.soroban.client.rpc.RpcSession;
import com.samourai.soroban.client.rpc.RpcSessionApi;
import com.samourai.soroban.client.rpc.RpcWalletImpl;
import com.samourai.wallet.bip47.rpc.PaymentCode;
import com.samourai.whirlpool.protocol.SorobanAppWhirlpool;
import com.samourai.whirlpool.protocol.soroban.payload.coordinators.CoordinatorMessage;
import com.samourai.whirlpool.protocol.soroban.payload.mix.*;
import com.samourai.whirlpool.protocol.soroban.payload.upStatus.UpStatusMessage;
import io.reactivex.Completable;
import io.reactivex.Single;
import java.lang.invoke.MethodHandles;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class WhirlpoolApiCoordinator extends RpcSessionApi {
  private static final Logger log = LoggerFactory.getLogger(MethodHandles.lookup().lookupClass());
  private SorobanAppWhirlpool app;

  public WhirlpoolApiCoordinator(RpcSession rpcSession, SorobanAppWhirlpool app) {
    super(rpcSession);
    this.app = app;
  }

  public Completable coordinatorsRegister(CoordinatorMessage coordinatorMessage) throws Exception {
    SorobanEndpointTyped endpoint = app.getEndpointCoordinators();
    return rpcSession.withSorobanClient(
        sorobanClient -> endpoint.send(sorobanClient, coordinatorMessage));
  }

  public Single<List<SorobanItemTyped>> registerInputFetchRequests(String poolId, boolean liquidity)
      throws Exception {
    PaymentCode paymentCodeCoordinator = getPaymentCode();
    SorobanEndpointTyped endpoint =
        app.getEndpointRegisterInput(paymentCodeCoordinator, poolId, liquidity);
    // distinct latest by sender
    return rpcSession.withSorobanClient(
        sorobanClient -> endpoint.getList(sorobanClient, f -> f.distinctBySenderWithLastNonce()));
  }

  public Single<List<SorobanItemTyped>> tx0FetchRequests(String poolId) {
    PaymentCode paymentCodeCoordinator = getPaymentCode();
    SorobanEndpointTyped endpoint = app.getEndpointTx0(paymentCodeCoordinator, poolId);
    return rpcSession.withSorobanClientSingle(
        sorobanClient -> endpoint.getList(sorobanClient, f -> f.distinctByUniqueIdWithLastNonce()));
  }

  public Single<List<SorobanItemTyped>> mixFetchConfirmInput(String mixId) throws Exception {
    PaymentCode paymentCodeCoordinator = getPaymentCode();
    SorobanEndpointTyped endpoint = app.getEndpointMixConfirmInput(mixId, paymentCodeCoordinator);
    return rpcSession.withSorobanClient(
        sorobanClient -> endpoint.getList(sorobanClient, f -> f.distinctByUniqueIdWithLastNonce()));
  }

  public Single<List<SorobanItemTyped>> mixFetchRegisterOutput(String inputsHash) throws Exception {
    PaymentCode paymentCodeCoordinator = getPaymentCode();
    SorobanEndpointTyped endpoint =
        app.getEndpointMixRegisterOutput(inputsHash, paymentCodeCoordinator);
    return rpcSession.withSorobanClient(
        sorobanClient -> endpoint.getList(sorobanClient, f -> f.distinctByUniqueIdWithLastNonce()));
  }

  public Single<List<SorobanItemTyped>> mixFetchRevealOutput(String mixId) throws Exception {
    PaymentCode paymentCodeCoordinator = getPaymentCode();
    SorobanEndpointTyped endpoint = app.getEndpointMixRevealOutput(mixId, paymentCodeCoordinator);
    return rpcSession.withSorobanClient(
        sorobanClient -> endpoint.getList(sorobanClient, f -> f.distinctByUniqueIdWithLastNonce()));
  }

  public Single<List<SorobanItemTyped>> mixFetchSigning(String mixId) throws Exception {
    PaymentCode paymentCodeCoordinator = getPaymentCode();
    SorobanEndpointTyped endpoint = app.getEndpointMixSigning(mixId, paymentCodeCoordinator);
    return rpcSession.withSorobanClient(
        sorobanClient -> endpoint.getList(sorobanClient, f -> f.distinctByUniqueIdWithLastNonce()));
  }

  public Single<List<SorobanItemTyped>> mixFetchMixStatus(String mixId) throws Exception {
    PaymentCode paymentCodeCoordinator = getPaymentCode();
    SorobanEndpointTyped endpoint = app.getEndpointMixStatus(mixId, paymentCodeCoordinator);
    return rpcSession.withSorobanClient(
        sorobanClient -> endpoint.getList(sorobanClient, f -> f.distinctByUniqueIdWithLastNonce()));
  }

  public Completable mixResultSend(String mixId, AbstractMixStatusResponse mixStatusResponse)
      throws Exception {
    PaymentCode paymentCodeCoordinator = getPaymentCode();
    SorobanEndpointTyped endpoint = app.getEndpointMixResult(mixId, paymentCodeCoordinator);
    return rpcSession.withSorobanClient(
        sorobanClient -> endpoint.send(sorobanClient, mixStatusResponse));
  }

  public Single<List<SorobanItemTyped>> upStatusFetch(SorobanClient sorobanClient, long checkId) {
    PaymentCode paymentCodeCoordinator = getPaymentCode();
    SorobanEndpointTyped endpoint = app.getEndpointUpStatus(paymentCodeCoordinator, checkId);
    return endpoint.getList(sorobanClient, f -> f.filterBySender(paymentCodeCoordinator));
  }

  public Completable upStatusSend(SorobanClient sorobanClient, long checkId) {
    PaymentCode paymentCodeCoordinator = getPaymentCode();
    SorobanEndpointTyped endpoint = app.getEndpointUpStatus(paymentCodeCoordinator, checkId);
    String origin = sorobanClient.getRpcClient().getUrl();
    UpStatusMessage upStatusMessage = new UpStatusMessage(origin);
    return endpoint.send(sorobanClient, upStatusMessage);
  }

  public WhirlpoolApiCoordinator createNewIdentity() throws Exception {
    RpcWalletImpl rpcWalletNew =
        (RpcWalletImpl) rpcSession.getRpcWallet().createNewIdentity(); // TODO cast
    RpcSession rpcSessionNew = rpcWalletNew.createRpcSession();
    return new WhirlpoolApiCoordinator(rpcSessionNew, app);
  }

  public SorobanAppWhirlpool getSorobanApp() {
    return app;
  }
}
