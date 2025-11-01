package com.samourai.wallet.send.boost;

import static java.lang.Math.max;
import static java.util.Objects.isNull;
import static java.util.Objects.nonNull;

import android.util.Log;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import com.samourai.wallet.R;
import com.samourai.wallet.SamouraiActivity;
import com.samourai.wallet.SamouraiWallet;
import com.samourai.wallet.api.APIFactory;
import com.samourai.wallet.bip47.BIP47Meta;
import com.samourai.wallet.bip69.BIP69OutputComparator;
import com.samourai.wallet.constants.SamouraiAccountIndex;
import com.samourai.wallet.hd.HD_WalletFactory;
import com.samourai.wallet.segwit.BIP49Util;
import com.samourai.wallet.segwit.bech32.Bech32Util;
import com.samourai.wallet.send.FeeUtil;
import com.samourai.wallet.send.MyTransactionInput;
import com.samourai.wallet.send.MyTransactionOutPoint;
import com.samourai.wallet.send.RBFSpend;
import com.samourai.wallet.send.RBFUtil;
import com.samourai.wallet.send.SendFactory;
import com.samourai.wallet.send.SuggestedFee;
import com.samourai.wallet.send.UTXO;
import com.samourai.wallet.util.PrefsUtil;
import com.samourai.wallet.util.func.AddressFactory;
import com.samourai.wallet.util.func.FormatsUtil;

import org.apache.commons.lang3.tuple.Triple;
import org.bitcoinj.core.Address;
import org.bitcoinj.core.Coin;
import org.bitcoinj.core.NetworkParameters;
import org.bitcoinj.core.Transaction;
import org.bitcoinj.core.TransactionInput;
import org.bitcoinj.core.TransactionOutput;
import org.bitcoinj.script.Script;
import org.bitcoinj.script.ScriptBuilder;
import org.bouncycastle.util.encoders.Hex;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.math.BigInteger;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Vector;
import java.util.concurrent.Callable;
import java.util.concurrent.atomic.AtomicInteger;

public class RBFPreProcessing implements Callable<String> {

    private static final String TAG = RBFPreProcessing.class.getSimpleName();
    private final SamouraiActivity activity;
    private final String txHash;
    private List<UTXO> utxos;
    private RBFSpend rbf;
    private boolean feeWarning = false;
    private Transaction transaction;
    private final Map<String, Long> inputValues = new LinkedHashMap<>();

    //useful in RBFProcessing for postmix account to determine how to compute private key for new utxo in tx
    private final Map<String, String> extraInputs = new LinkedHashMap();
    private long remainingFee;

    public String getTxHash() {
        return txHash;
    }

    public RBFSpend getRbf() {
        return rbf;
    }

    public boolean isFeeWarning() {
        return feeWarning;
    }

    public Transaction getTransaction() {
        return transaction;
    }

    public Map<String, Long> getInputValues() {
        return inputValues;
    }

    public Map<String, String> getExtraInputs() {
        return extraInputs;
    }

    public long getRemainingFee() {
        return remainingFee;
    }

    private RBFPreProcessing(final SamouraiActivity activity, final String txHash) {
        
        this.activity = activity;
        this.txHash = txHash;
        if (activity.getAccount() == SamouraiAccountIndex.POSTMIX) {
            utxos = APIFactory.getInstance(activity).getUtxosPostMix(true);
        } else {
            utxos = APIFactory.getInstance(activity).getUtxos(true);
        }
    }
    
    public static RBFPreProcessing create(final SamouraiActivity activity, final String txHash) {
        return new RBFPreProcessing(activity, txHash);
    }
    
    @Override
    public String call() throws Exception {
        return preProcessRBF();
    }

    private String preProcessRBF() {

        Log.d("RBF", "hash:" + txHash);

        rbf = RBFUtil.getInstance().get(txHash);
        Log.d("RBF", "rbf:" + rbf.toJSON().toString());

        final Transaction tx = new Transaction(
                SamouraiWallet.getInstance().getCurrentNetworkParams(),
                Hex.decode(rbf.getSerializedTx()));

        Log.d("RBF", "tx serialized:" + rbf.getSerializedTx());
        Log.d("RBF", "tx inputs:" + tx.getInputs().size());
        Log.d("RBF", "tx outputs:" + tx.getOutputs().size());

        final JSONObject txObj = APIFactory.getInstance(activity).getTxInfo(txHash);
        if (isNull(txObj) || !txObj.has("inputs") || !txObj.has("outputs")) {
            return activity.getString(R.string.cpfp_cannot_retrieve_tx);
        }

        final SuggestedFee keepCurrentSuggestedFee = FeeUtil.getInstance().getSuggestedFee();
        try {
            return preProcessRBFUnsafe(txObj, tx);
        } catch (final Exception e) {
            return "rbf:" + e.getMessage();
        } finally {
            FeeUtil.getInstance().setSuggestedFee(keepCurrentSuggestedFee);
        }
    }

    @Nullable
    private String preProcessRBFUnsafe(final JSONObject txObj, final Transaction tx)
            throws JSONException {

        final JSONArray inputs = txObj.getJSONArray("inputs");
        final JSONArray outputs = txObj.getJSONArray("outputs");

        final Map<String, AtomicInteger> addrFormatCount = computeAddrFormatCount(inputs);
        FeeUtil.getInstance().setSuggestedFee(FeeUtil.getInstance().getHighFee());
        final BigInteger estimatedInitialFee = FeeUtil.getInstance().estimatedFeeSegwit(
                addrFormatCount.get("p2pkh").get(),
                addrFormatCount.get("p2sh_p2wpkh").get(),
                addrFormatCount.get("p2wpkh").get(),
                outputs.length());

        final long total_inputs = computeTotalInputs(inputs);
        final Triple<Long, Long, Collection<String>> outputTotalResults = computeTotalOutput(outputs);

        final long total_outputs = outputTotalResults.getLeft();
        final long total_change = outputTotalResults.getMiddle();
        final Collection<String> outAddresses = outputTotalResults.getRight();
        final long currentFee = total_inputs - total_outputs;
        if (currentFee > estimatedInitialFee.longValue()) {
            feeWarning = true;
        }

        remainingFee = (estimatedInitialFee.longValue() > currentFee)
                ? max(estimatedInitialFee.longValue() - currentFee, SamouraiWallet.minAdditionalFeesToRelayRBF.longValue())
                : 0L;

        Log.d("RBF", "total inputs:" + total_inputs);
        Log.d("RBF", "total outputs:" + total_outputs);
        Log.d("RBF", "total change:" + total_change);
        Log.d("RBF", "fee:" + currentFee);
        Log.d("RBF", "estimated fee:" + estimatedInitialFee.longValue());
        Log.d("RBF", "fee warning:" + feeWarning);
        Log.d("RBF", "remaining fee:" + remainingFee);

        final List<TransactionOutput> txOutputs = Lists.newArrayList(tx.getOutputs());
        final long remainder = computeRemainderFee(total_change, txOutputs);

        //
        // original inputs are not modified
        //
        final List<MyTransactionInput> _inputs = generateTransactionInputs(tx);
        if (remainder > 0L) {

            Collections.sort(utxos, new UTXO.UTXOComparator());
            final Triple<Long, Long, List<UTXO>> selectedUtxoResult = computeSelectedUtxo(
                    remainder,
                    outAddresses,
                    outputs,
                    estimatedInitialFee,
                    addrFormatCount);

            final List<UTXO> selectedUTXO = selectedUtxoResult.getRight();
            long selectedAmount = selectedUtxoResult.getLeft();
            long adjRemainingFee = selectedUtxoResult.getMiddle();

            if (selectedAmount < (adjRemainingFee + SamouraiWallet.bDust.longValue())) {
                return activity.getString(R.string.insufficient_funds);
            }

            final long extraChangeAmount = selectedAmount - adjRemainingFee;
            Log.d("RBF", "extra change:" + extraChangeAmount);

            final boolean addedChangeOutput = addExtraChangeInOutput(
                    extraChangeAmount,
                    outputs,
                    txOutputs);

            // sanity check
            if (extraChangeAmount > 0L && !addedChangeOutput) {
                return activity.getString(R.string.cannot_create_change_output);
            }

            //
            // update keyBag w/ any new paths
            //
            //final HashMap<String, String> keyBag = rbf.getKeyBag();
            updateInputsAndRBFKeyBags(selectedUTXO, _inputs);
        }

        //
        // BIP69 sort of outputs/inputs
        //

        buildTransaction(txOutputs, _inputs);

        return null;
    }

    private void buildTransaction(
            final List<TransactionOutput> txOutputs,
            final List<MyTransactionInput> _inputs) {

        transaction = new Transaction(SamouraiWallet.getInstance().getCurrentNetworkParams());
        final List<TransactionOutput> _txOutputs = Lists.newArrayList(txOutputs);
        Collections.sort(_txOutputs, new BIP69OutputComparator());
        for (final TransactionOutput to : _txOutputs) {
            // zero value outputs discarded here
            if (to.getValue().longValue() > 0L) {
                transaction.addOutput(to);
            }
        }

        final List<MyTransactionInput> __inputs = Lists.newArrayList(_inputs);
        Collections.sort(__inputs, new SendFactory.BIP69InputComparator());
        for (final TransactionInput input : __inputs) {
            transaction.addInput(input);
        }
    }

    private void updateInputsAndRBFKeyBags(
            final List<UTXO> selectedUTXO,
            final List<MyTransactionInput> _inputs) {

        final NetworkParameters netParams = SamouraiWallet.getInstance().getCurrentNetworkParams();

        for (final UTXO _utxo : selectedUTXO) {

            for (final MyTransactionOutPoint outpoint : _utxo.getOutpoints()) {

                final MyTransactionInput _input = new MyTransactionInput(
                        netParams,
                        null,
                        new byte[0],
                        outpoint,
                        outpoint.getTxHash().toString(),
                        outpoint.getTxOutputN());

                _input.setSequenceNumber(SamouraiWallet.RBF_SEQUENCE_VAL.longValue());
                _inputs.add(_input);
                _input.setValue(BigInteger.valueOf(outpoint.getValue().getValue()));
                inputValues.put(_input.getOutpoint().toString(), outpoint.getValue().getValue());
                extraInputs.put(outpoint.toString(), getAddress(outpoint.getConnectedOutput()));
                Log.d("RBF", "add selected outpoint:" + _input.getOutpoint().toString());

                final String path = APIFactory.getInstance(activity).getUnspentPaths().get(outpoint.getAddress());
                if (nonNull(path)) {
                    if (FormatsUtil.getInstance().isValidBech32(outpoint.getAddress())) {
                        rbf.addKey(outpoint.toString(), path + "/84");
                    } else if (nonNull(Address.fromBase58(netParams, outpoint.getAddress())) &&
                            Address.fromBase58(netParams, outpoint.getAddress()).isP2SHAddress()) {
                        rbf.addKey(outpoint.toString(), path + "/49");
                    } else {
                        rbf.addKey(outpoint.toString(), path);
                    }
                    Log.d("RBF", "outpoint address:" + outpoint.getAddress());
                } else {

                    final String pcode = BIP47Meta.getInstance().getPCode4Addr(outpoint.getAddress());
                    final int idx = BIP47Meta.getInstance().getIdx4Addr(outpoint.getAddress());

                    if (FormatsUtil.getInstance().isValidBech32(outpoint.getAddress())) {
                        rbf.addKey(outpoint.toString(), "PCODE/" + pcode + "/" + idx + "/84");
                    } else if (nonNull(Address.fromBase58(netParams, outpoint.getAddress())) &&
                            Address.fromBase58(netParams, outpoint.getAddress()).isP2SHAddress()) {
                        rbf.addKey(outpoint.toString(), "PCODE/" + pcode + "/" + idx + "/49");
                    } else {
                        rbf.addKey(outpoint.toString(), "PCODE/" + pcode + "/" + idx);
                    }
                }
            }
        }
        //rbf.setKeyBag(keyBag);
    }

    private boolean addExtraChangeInOutput(
            final long extraChange,
            final JSONArray outputs,
            final List<TransactionOutput> txOutputs
    ) throws JSONException {

        boolean addedChangeOutput = false;
        if (extraChange > 0L) {
            // parent tx didn't have change output
            if (outputs.length() == 1) {

                final NetworkParameters netParams = SamouraiWallet.getInstance().getCurrentNetworkParams();

                final String addressFromTx = outputs.getJSONObject(0).getString("address");
                final boolean isSegwitChange = FormatsUtil.getInstance().isValidBech32(addressFromTx) ||
                        Address.fromBase58(netParams, addressFromTx).isP2SHAddress() ||
                        PrefsUtil.getInstance(activity).getValue(PrefsUtil.USE_LIKE_TYPED_CHANGE, true) == false;

                final String change_address;
                if (isSegwitChange) {
                    final int changeIdx = BIP49Util.getInstance(activity).getWallet().getAccount(activity.getAccount()).getChange().getAddrIdx();
                    change_address = BIP49Util.getInstance(activity).getAddressAt(AddressFactory.CHANGE_CHAIN, changeIdx).getAddressAsString();
                } else {
                    final int changeIdx = HD_WalletFactory.getInstance(activity).get().getAccount(activity.getAccount()).getChange().getAddrIdx();
                    change_address = HD_WalletFactory.getInstance(activity).get().getAccount(activity.getAccount()).getChange().getAddressAt(changeIdx).getAddressString();
                }

                final Script toOutputScript = ScriptBuilder.createOutputScript(Address.fromBase58(netParams, change_address));
                TransactionOutput output = new TransactionOutput(netParams, null, Coin.valueOf(extraChange), toOutputScript.getProgram());
                txOutputs.add(output);
                addedChangeOutput = true;

            } else { // parent tx had change output
                for (final TransactionOutput output : txOutputs) {
                    String _addr = getAddress(output);
                    Log.d("RBF", "checking for change:" + _addr);
                    if (rbf.containsChangeAddr(_addr)) {
                        final long amount = output.getValue().longValue();
                        Log.d("RBF", "before extra:" + amount);
                        output.setValue(Coin.valueOf(extraChange + amount));
                        Log.d("RBF", "after extra:" + output.getValue().longValue());
                        addedChangeOutput = true;
                        break;
                    }
                }
            }
        }
        return addedChangeOutput;
    }

    private Triple<Long, Long, List<UTXO>> computeSelectedUtxo(
            final long remainder,
            final Collection<String> outAddresses,
            final JSONArray outputs, BigInteger estimatedInitialFee,
            final Map<String, AtomicInteger> addrFormatCount) {

        int selectedCount = 0;
        final List<UTXO> selectedUTXO = Lists.newArrayList();
        long selectedAmount = 0L;
        long adjRemainingFee = remainder;

        for (final UTXO _utxo : utxos) {

            Log.d("RBF", "utxo value:" + _utxo.getValue());

            //
            // do not select utxo that are change outputs in current rbf tx
            //
            boolean isChange = false;
            boolean isSelf = false;
            final List<MyTransactionOutPoint> utxoOutpoints = _utxo.getOutpoints();
            for (final MyTransactionOutPoint utxoOutpoint : utxoOutpoints) {
                if (rbf.containsChangeAddr(utxoOutpoint.getAddress())) {
                    Log.d("RBF", "is change:" + utxoOutpoint.getAddress());
                    Log.d("RBF", "is change:" + utxoOutpoint.getValue().longValue());
                    isChange = true;
                    break;
                }
                if (outAddresses.contains(utxoOutpoint.getAddress())) {
                    Log.d("RBF", "is self:" + utxoOutpoint.getAddress());
                    Log.d("RBF", "is self:" + utxoOutpoint.getValue().longValue());
                    isSelf = true;
                    break;
                }
            }
            if (isChange || isSelf) {
                continue;
            }

            selectedUTXO.add(_utxo);
            selectedCount += utxoOutpoints.size();
            Log.d("RBF", "selected utxo:" + selectedCount);
            selectedAmount += _utxo.getValue();
            Log.d("RBF", "selected utxo value:" + _utxo.getValue());

            final Triple<Integer, Integer, Integer> outpointTypes = FeeUtil.getInstance().getOutpointCount(new Vector(utxoOutpoints));
            addrFormatCount.get("p2pkh").addAndGet(outpointTypes.getLeft());
            addrFormatCount.get("p2sh_p2wpkh").addAndGet(outpointTypes.getMiddle());
            addrFormatCount.get("p2wpkh").addAndGet(outpointTypes.getRight());

            final BigInteger actualizedEstFee = FeeUtil.getInstance().estimatedFeeSegwit(
                    addrFormatCount.get("p2pkh").get(),
                    addrFormatCount.get("p2sh_p2wpkh").get(),
                    addrFormatCount.get("p2wpkh").get(),
                    outputs.length() == 1 ? 2 : outputs.length());
            final BigInteger extraFee = actualizedEstFee.subtract(estimatedInitialFee);

            if (selectedAmount <= extraFee.longValue() + SamouraiWallet.bDust.longValue()) {
                break; // let's common, extraFee is bigger than amount of associated extra utxo...
            }

            adjRemainingFee = remainder + extraFee.longValue();
            Log.d("RBF", "_remaining fee:" + adjRemainingFee);
            if (selectedAmount >= (adjRemainingFee + SamouraiWallet.bDust.longValue())) {
                break;
            }
        }

        return Triple.of(selectedAmount, adjRemainingFee, selectedUTXO);
    }

    private static List<MyTransactionInput> generateTransactionInputs(final Transaction tx) {

        final NetworkParameters netParams = SamouraiWallet.getInstance().getCurrentNetworkParams();
        final List<MyTransactionInput> _inputs = Lists.newArrayList();

        for (final TransactionInput input : tx.getInputs()) {
            final MyTransactionInput _input = new MyTransactionInput(
                    netParams,
                    null,
                    new byte[0],
                    input.getOutpoint(),
                    input.getOutpoint().getHash().toString(),
                    (int) input.getOutpoint().getIndex());

            _input.setSequenceNumber(SamouraiWallet.RBF_SEQUENCE_VAL.longValue());
            _inputs.add(_input);
            Log.d("RBF", "add outpoint:" + _input.getOutpoint().toString());
        }
        return _inputs;
    }

    private Triple<Long, Long, Collection<String>> computeTotalOutput(JSONArray outputs) throws JSONException {
        long tot_outputs = 0L;
        long tot_change = 0L;
        final Collection<String> outAddr = Sets.newHashSet();
        for (int i = 0; i < outputs.length(); i++) {
            final JSONObject obj = outputs.getJSONObject(i);
            if (obj.has("value")) {
                final long amount = obj.getLong("value");
                tot_outputs += amount;

                final String _addr;
                if (obj.has("address")) {
                    _addr = obj.getString("address");
                } else {
                    _addr = null;
                }

                if (nonNull(_addr)) {
                    outAddr.add(_addr);
                    if (rbf.containsChangeAddr(_addr)) {
                        tot_change += amount;
                    }
                }
            }
        }
        return Triple.of(tot_outputs, tot_change, outAddr);
    }

    private long computeRemainderFee(
            final long total_change,
            final List<TransactionOutput> txOutputs) {

        if (total_change <= remainingFee) {
            return remainingFee;
        } else {

            final NetworkParameters netParams = SamouraiWallet.getInstance().getCurrentNetworkParams();
            long remainder = remainingFee;

            for (final TransactionOutput output : txOutputs) {
                final Script script = output.getScriptPubKey();
                final String scriptPubKey = Hex.toHexString(script.getProgram());
                final Address _p2sh = output.getAddressFromP2SH(netParams);
                final Address _p2pkh = output.getAddressFromP2PKHScript(netParams);
                try {
                    if ( (Bech32Util.getInstance().isBech32Script(scriptPubKey) && rbf.containsChangeAddr((Bech32Util.getInstance().getAddressFromScript(scriptPubKey))) ) ||
                            (_p2sh != null && rbf.containsChangeAddr(_p2sh.toString())) ||
                            (_p2pkh != null && rbf.containsChangeAddr(_p2pkh.toString()))) {

                        final long currentAmount = output.getValue().longValue();
                        if (currentAmount >= (remainder + SamouraiWallet.bDust.longValue())) {
                            output.setValue(Coin.valueOf(currentAmount - remainder)); // reduce existing change
                            remainder = 0L;
                            break;
                        } else {
                            remainder -= currentAmount;
                            output.setValue(Coin.valueOf(0L));      // output will be discarded later : remove change
                        }
                    }
                } catch (Exception e) {
                    ;
                }
            }
            return remainder;
        }
    }

    private long computeTotalInputs(final JSONArray inputs) throws JSONException {
        long total_inputs = 0L;
        for (int i = 0; i < inputs.length(); i++) {
            final JSONObject obj = inputs.getJSONObject(i);
            if (obj.has("outpoint")) {
                JSONObject objPrev = obj.getJSONObject("outpoint");
                if (objPrev.has("value")) {
                    final long amount = objPrev.getLong("value");
                    total_inputs += amount;
                    final String key = objPrev.getString("txid") + ":" + objPrev.getLong("vout");
                    inputValues.put(key, objPrev.getLong("value"));
                }
            }
        }
        return total_inputs;
    }

    @NonNull
    private static Map<String, AtomicInteger> computeAddrFormatCount(final JSONArray inputs)
            throws JSONException {

        final Map<String, AtomicInteger> addrFormatCount = new HashMap<String, AtomicInteger>() {
            {
                // first format addr // Pay To Public Key Hash // starts with 1 or 2 // BIP44
                put("p2pkh", new AtomicInteger(0));

                // p2sh : starts with 3 BIP49
                // BIP49 segwit compatible
                put("p2sh_p2wpkh", new AtomicInteger(0));

                // ScriptPubKey segwit native // starts with bc1q // encoding Bech32 // BIP84
                put("p2wpkh", new AtomicInteger(0));
                // P2TR : Taproot // starts with bc1p
            }
        };

        final NetworkParameters netParams = SamouraiWallet.getInstance().getCurrentNetworkParams();

        for (int i = 0; i < inputs.length(); i++) {
            if (inputs.getJSONObject(i).has("outpoint") && inputs.getJSONObject(i).getJSONObject("outpoint").has("scriptpubkey")) {
                final String scriptpubkey = inputs.getJSONObject(i).getJSONObject("outpoint").getString("scriptpubkey");
                final Script script = new Script(Hex.decode(scriptpubkey));
                String address = null;
                if (Bech32Util.getInstance().isBech32Script(scriptpubkey)) {
                    try {
                        address = Bech32Util.getInstance().getAddressFromScript(scriptpubkey);
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                } else {
                    address = script.getToAddress(netParams).toString();
                }

                if (FormatsUtil.getInstance().isValidBech32(address)) {
                    addrFormatCount.get("p2wpkh").incrementAndGet();
                } else if (Address.fromBase58(netParams, address).isP2SHAddress()) {
                    addrFormatCount.get("p2sh_p2wpkh").incrementAndGet();
                } else {
                    addrFormatCount.get("p2pkh").incrementAndGet();
                }
            }
        }
        return addrFormatCount;
    }

    @Nullable
    private static String getAddress(final TransactionOutput output) {

        final NetworkParameters netParams = SamouraiWallet.getInstance().getCurrentNetworkParams();

        final Script script = output.getScriptPubKey();
        final String scriptPubKey = Hex.toHexString(script.getProgram());
        String _addr = null;
        if (Bech32Util.getInstance().isBech32Script(scriptPubKey)) {
            try {
                _addr = Bech32Util.getInstance().getAddressFromScript(scriptPubKey);
            } catch (Exception e) {
                ;
            }
        }
        if (isNull(_addr)) {
            Address _address = output.getAddressFromP2PKHScript(netParams);
            if (isNull(_address)) {
                _address = output.getAddressFromP2SH(netParams);
            }
            _addr = _address.toString();
        }
        return _addr;
    }

}
