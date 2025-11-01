package com.samourai.wallet.bip47;

import static com.samourai.wallet.util.tech.LogUtil.info;
import static org.apache.commons.lang3.StringUtils.isBlank;
import static org.apache.commons.lang3.StringUtils.isNotBlank;
import static java.util.Objects.isNull;
import static java.util.Objects.nonNull;

import android.content.Context;
import android.util.Log;

import com.google.common.collect.Lists;
import com.google.common.collect.Maps;
import com.google.common.collect.Sets;
import com.samourai.wallet.SamouraiWallet;
import com.samourai.wallet.bip47.rpc.PaymentCode;

import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.tuple.Pair;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

public class BIP47Meta {

    private static final String TAG = "BIP47Meta";

    public static final String ashigaruDonationPcodeMainnet = "PM8TJUhHJzVgoxaay8njgTDdNVE8i6PuFbgsJEiKpfbX7umkVHQ9bamF1pZgEYWAmkecLt81Mcg6ybKbDW4PN41GsskGXLV89fb5ARF3ZexopEgDBs3v";
    public static final String ashigaruDonationPcodeTestnet = "PM8TJQuX14xb5VhpYUFM165WjbYHTnQvH2zdyrTJijnjYrfGM8u5tTiQ3qCFAoESb1xDnLXaqD4iqR6zFUFy3Yi1C1nN4F3hLMp7LJngjgB4gvumHnc3";
    public static final String strSamouraiDonationPCode = SamouraiWallet.getInstance().isTestNet() ? ashigaruDonationPcodeTestnet : ashigaruDonationPcodeMainnet;//    public static final String strSamouraiDonationMeta = "?title=Samourai Donations&desc=Donate to help fund development of Samourai Bitcoin Wallet&user=K6tS2X8";
    public static final String getStrSamouraiMixingPcodeMainnet = SamouraiWallet.SAAS_PCODE_MAINNET;
    public static final String getStrSamouraiMixingPcodeTestnet = SamouraiWallet.SAAS_PCODE_TESTNET;
    public static final int INCOMING_LOOKAHEAD = 3;
//    public static final int OUTGOING_LOOKAHEAD = 3;

    public static final int STATUS_NOT_SENT = -1;
    public static final int STATUS_SENT_NO_CFM = 0;
    public static final int STATUS_SENT_CFM = 1;
    public boolean  requiredRefresh=  false;

    private static Map<String, String> pcodeNames = null;
    private static Map<String, String> pcodeLabels = null;
    private static Map<String, String> notFoundPcodeLabels = null; // useful to keep the pcode from backup on sync task
    private static Map<String, String> labelsPcode = null;
    private static Map<String, Boolean> followings = null;
    private static Map<String, Boolean> pcodeArchived = null;
    private static Map<String, Map<String,Integer>> pcodeUnspentIdxs = null; // unused => could be removed
    private static Map<String, String> addr2pcode = null;
    private static Map<String, Integer> addr2idx = null;
    private static Map<String, Integer> pcodeOutgoingIdxs = null;
    private static Map<String, Integer> pcodeIncomingIdxs = null;
    private static Map<String, Pair<String, Integer>> pcodeOutgoingStatus = null;
    private static Map<String, List<Integer>> pcodeIncomingUnspent = null;
    private static Map<String, String> pcodeIncomingStatus = null;
    private static Map<String, String> pcodeLatestEvent = null;
    private static Map<String, Boolean> pcodeSegwit = null;

    private static BIP47Meta instance = null;

    private BIP47Meta() {}

    public static BIP47Meta getInstance() {

        if(isNull(instance)) {
            pcodeNames = new ConcurrentHashMap<>();
            pcodeLabels = new ConcurrentHashMap<>();
            notFoundPcodeLabels = new ConcurrentHashMap<>();
            labelsPcode = new ConcurrentHashMap<>();
            followings = new ConcurrentHashMap<>();
            pcodeArchived = new ConcurrentHashMap<>();
            pcodeUnspentIdxs = new ConcurrentHashMap<>();
            addr2pcode = new ConcurrentHashMap<>();
            addr2idx = new ConcurrentHashMap<>();
            pcodeOutgoingIdxs = new ConcurrentHashMap<>();
            pcodeIncomingIdxs = new ConcurrentHashMap<>();
            pcodeOutgoingStatus = new ConcurrentHashMap<>();
            pcodeIncomingUnspent = new ConcurrentHashMap<>();
            pcodeIncomingStatus = new ConcurrentHashMap<>();
            pcodeLatestEvent = new ConcurrentHashMap<>();
            pcodeSegwit = new ConcurrentHashMap<>();

            instance = new BIP47Meta();
        }

        return instance;
    }

    public void clear() {
        pcodeNames.clear();
        pcodeLabels.clear();
        notFoundPcodeLabels.clear();
        labelsPcode.clear();
        followings.clear();
        pcodeArchived.clear();
        pcodeUnspentIdxs.clear();
        addr2pcode.clear();
        addr2idx.clear();
        pcodeOutgoingIdxs.clear();
        pcodeIncomingIdxs.clear();
        pcodeOutgoingStatus.clear();
        pcodeIncomingUnspent.clear();
        pcodeIncomingStatus.clear();
        pcodeLatestEvent.clear();
        pcodeSegwit.clear();
    }

    public void partialClearOnRestoringWallet() {
        pcodeNames.clear();
        pcodeLabels.clear();
        labelsPcode.clear();
        followings.clear();
        pcodeSegwit.clear();
        pcodeUnspentIdxs.clear();
    }

    public String getPcodeFromLabel(final String label)   {
        if (isBlank(label)) return null;
        if (StringUtils.equals(label, "Ashigaru as mixing partner")) {
            return getMixingPartnerCode();
        }
        return labelsPcode.get(label);
    }

    public String getName(final String pcode) {
        return pcodeNames.getOrDefault(pcode, "");
    }

    public String getLabel(final String pcode)   {
        if(pcode == null) {
            return "";
        }
        if(pcode.equals(getMixingPartnerCode())){
            return "Ashigaru as mixing partner";
        }
        if(!pcodeLabels.containsKey(pcode))    {
            return "";
        } else {
            return pcodeLabels.get(pcode);
        }
    }

    public boolean isFollowing(final String pcode) {
        return followings.getOrDefault(pcode, false);
    }

    public Set<String> getFollowings() {
        final Set<String> followingsFound = Sets.newHashSet();
        for (final String pcode : followings.keySet()) {
            if (isFollowing(pcode)) {
                followingsFound.add(pcode);
            }
        }
        return followingsFound;
    }

    synchronized public void setFollowings(final Collection<String> pcodes) {
        followings.clear();
        for (final String pcode : pcodes) {
            followings.put(pcode, true);
        }
    }

    public void setFollowing(final String pcode, final boolean isFollowing) {
        followings.put(pcode, isFollowing);
    }

    public String getDisplayLabel(final String pcode)   {
        String label = getLabel(pcode);
        if(label.length() == 0 || pcode.equals(label))    {
            label = getAbbreviatedPcode(pcode);
        }
        return label;
    }

    public String getAbbreviatedPcode(final String pcode)   {
        return pcode.substring(0, 12) + "..." + pcode.substring(pcode.length() - 5, pcode.length());
    }

    public void setName(final String pcode, final String name)   {
        pcodeNames.put(pcode, name);
    }

    public void setLabel(final String pcode, final String label) {
        if (StringUtils.isBlank(label) && pcodeNames.containsKey(pcode)) {
            return;
        }
        pcodeLabels.put(pcode, label);
        labelsPcode.put(label, pcode);
    }

    public void putNotFoundPcodes(final String pcode, final String label) {
        notFoundPcodeLabels.put(pcode, label);
    }

    public Set<String> getPcodes()    {
        return pcodeLabels.keySet();
    }

    public Map<String, String> getCopyOfPcodeLabels() {
        return Maps.newHashMap(pcodeLabels);
    }

    public Set<String> getSortedByLabels(final boolean includeArchived) {

        if(includeArchived) {
            return valueSortByComparator(pcodeLabels, true).keySet();
        } else {
            final Map<String, String> labels = new ConcurrentHashMap<>();
            for(String key : pcodeLabels.keySet()) {
                if(!BIP47Meta.getInstance().getArchived(key)) {
                    labels.put(key, pcodeLabels.get(key));
                }
            }
            return valueSortByComparator(labels, true).keySet();
        }
    }

    public boolean exists(final String pcode, final boolean includeArchived) {
        return getSortedByLabels(includeArchived).contains(pcode);
    }

    public Set<String> getSortedByLabels(final boolean includeArchived, final boolean confirmed) {

        if(includeArchived) {
            return valueSortByComparator(pcodeLabels, true).keySet();
        } else {
            final Map<String, String> labels = new ConcurrentHashMap<>();
            for(final String key : pcodeLabels.keySet()) {
                final int outgoingStatus = getOutgoingStatus(key);
                if(!BIP47Meta.getInstance().getArchived(key)
                        && (!confirmed || outgoingStatus == BIP47Meta.STATUS_SENT_CFM)) {
                    labels.put(key, pcodeLabels.get(key));
                }
            }
            return valueSortByComparator(labels, true).keySet();
        }
    }

    private static Map<String, String> valueSortByComparator(
            final Map<String, String> unsortMap,
            final boolean order)  {

        final List<Map.Entry<String, String>> list = new LinkedList<>(unsortMap.entrySet());

        // Sorting the list based on values
        Collections.sort(list, (o1, o2) -> {

            if(o1.getValue() == null || o1.getValue().length() == 0)    {
                o1.setValue(o1.getKey());
            }
            if(o2.getValue() == null || o2.getValue().length() == 0)    {
                o2.setValue(o2.getKey());
            }

            if(order) {
                return o1.getValue().compareTo(o2.getValue());
            }
            else {
                return o2.getValue().compareTo(o1.getValue());

            }
        });

        // Maintaining insertion order with the help of LinkedList
        final Map<String, String> sortedMap = new LinkedHashMap<>();
        for (final Map.Entry<String, String> entry : list) {
            sortedMap.put(entry.getKey(), entry.getValue());
        }

        return sortedMap;
    }

    public boolean getArchived(final String pcode) {
        return pcodeArchived.getOrDefault(pcode, false);
    }

    public void setArchived(final String pcode, final boolean archived)   {
        pcodeArchived.put(pcode, archived);
    }

    public boolean getSegwit(final String pcode)   {
        if(!pcodeSegwit.containsKey(pcode))    {
            pcodeSegwit.put(pcode, false);
            return false;
        }
        else    {
            return pcodeSegwit.get(pcode);
        }
    }

    public void setSegwit(final String pcode, final boolean segwit)   {
        pcodeSegwit.put(pcode, segwit);
    }

    public int getIncomingIdx(final String pcode)   {
        if(!pcodeIncomingIdxs.containsKey(pcode))    {
            return 0;
        } else {
            return pcodeIncomingIdxs.get(pcode);
        }
    }

    public void setIncomingIdx(final String pcode, final int idx)   {
        pcodeIncomingIdxs.put(pcode, idx);
    }

    public void incOutgoingIdx(final String pcode)   {
        if(!pcodeOutgoingIdxs.containsKey(pcode))    {
            pcodeOutgoingIdxs.put(pcode, 1);
        }
        else    {
            pcodeOutgoingIdxs.put(pcode, pcodeOutgoingIdxs.get(pcode) + 1);
        }
    }

    public int getOutgoingIdx(final String pcode)   {
        if(!pcodeOutgoingIdxs.containsKey(pcode))    {
            return 0;
        } else {
            return pcodeOutgoingIdxs.get(pcode);
        }
    }

    public void setOutgoingIdx(final String pcode, final int idx)   {
        pcodeOutgoingIdxs.put(pcode, idx);
    }

    public String[] getIncomingAddresses(final boolean includeArchived)  {

        final List<String> addrs = new ArrayList<>();
        for (final String pcode : pcodeIncomingIdxs.keySet())   {
            if(!includeArchived && getArchived(pcode)) continue;
            if(isNull(pcodeUnspentIdxs.get(pcode))) continue;
            addrs.addAll(pcodeUnspentIdxs.get(pcode).keySet());
        }
        return addrs.toArray(new String[addrs.size()]);
    }

    public synchronized String[] getIncomingLookAhead(Context ctx)  {

        final Set<String> pcodes = pcodeIncomingIdxs.keySet();
        final Iterator<String> it = pcodes.iterator();
        final List<String> addrs = new ArrayList<>();

        while(it.hasNext())   {
            final String pcode = it.next();
            if(getArchived(pcode))    {
                continue;
            }
            final int idx = getIncomingIdx(pcode);

//            info("APIFactory", "idx:" + idx + " , " + pcode);

            for(int i = idx; i < (idx + INCOMING_LOOKAHEAD); i++)   {
                try {
                    info("APIFactory", "receive from " + i + ":" + BIP47Util.getInstance(ctx).getReceivePubKey(new PaymentCode(pcode), i));
                    BIP47Meta.getInstance().getIdx4AddrLookup().put(BIP47Util.getInstance(ctx).getReceivePubKey(new PaymentCode(pcode), i), i);
                    BIP47Meta.getInstance().getPCode4AddrLookup().put(BIP47Util.getInstance(ctx).getReceivePubKey(new PaymentCode(pcode), i), pcode.toString());
                    addrs.add(BIP47Util.getInstance(ctx).getReceivePubKey(new PaymentCode(pcode), i));
                } catch(final Exception e) {
                    Log.e(TAG, e.getMessage(), e);
                }
            }

        }

        final String[] s = addrs.toArray(new String[addrs.size()]);

        return s;
    }

    public String getPCode4Addr(final String addr)  {
        return addr2pcode.get(addr);
    }

    public Integer getIdx4Addr(final String addr)  {
        return addr2idx.get(addr);
    }

    public Map<String,String> getPCode4AddrLookup() {
        return addr2pcode;
    }

    public Map<String,Integer> getIdx4AddrLookup() {
        return addr2idx;
    }

    public void setUnspentIdx(final String pcode, final int idx, final String addr)   {

        if(!pcodeUnspentIdxs.containsKey(pcode))    {
            ConcurrentHashMap<String, Integer> addrIdx = new ConcurrentHashMap<>();
            addrIdx.put(addr, idx);
            pcodeUnspentIdxs.put(pcode, addrIdx);
        }
        else    {
            pcodeUnspentIdxs.get(pcode).put(addr, idx);
        }
    }

    public boolean incomingExists(final String pcode) {
        return pcodeIncomingIdxs.containsKey(pcode);
    }

    public int getOutgoingStatus(final String pcode)   {
        if(!pcodeOutgoingStatus.containsKey(pcode))    {
            return STATUS_NOT_SENT;
        }
        else    {
            return pcodeOutgoingStatus.get(pcode).getRight();
        }
    }

    public boolean isOutgoingStatusSent(final String pcode) {
        final Pair<String, Integer> txAndStatus = pcodeOutgoingStatus.get(pcode);
        if (isNull(txAndStatus)) return false;
        return txAndStatus.getValue() == STATUS_SENT_CFM ||
                txAndStatus.getValue() == STATUS_SENT_NO_CFM;
    }

    synchronized public void setOutgoingStatus(final String pcode, final int status)   {
        final String _tx = pcodeOutgoingStatus.get(pcode).getLeft();
        pcodeOutgoingStatus.put(pcode, Pair.of(_tx, status));
    }

    public void setOutgoingStatus(final String pcode, final String tx, final int status) {
        pcodeOutgoingStatus.put(pcode, Pair.of(tx, status));
    }

    public List<Pair<String, String>> getOutgoingUnconfirmed()   {

        final List<Pair<String, String>> ret = Lists.newArrayList();

        for(final Map.Entry<String, Pair<String, Integer>> pcodeToTxInfo : pcodeOutgoingStatus.entrySet()) {
            final Pair<String, Integer> txInfo = pcodeToTxInfo.getValue();
            final Integer confirmedStatus = nonNull(txInfo.getRight()) ? txInfo.getRight() : STATUS_NOT_SENT;
            final String txHash = txInfo.getLeft();
            if (confirmedStatus == STATUS_SENT_NO_CFM && isNotBlank(txHash)) {
                final String pcode = pcodeToTxInfo.getKey();
                ret.add(Pair.of(pcode, txHash));
            }
        }

        return ret;
    }

    public void addUnspent(final String pcode, final int idx)    {

        final List<Integer> idxs = nonNull(pcodeIncomingUnspent.get(pcode))
                ? pcodeIncomingUnspent.get(pcode)
                : Lists.newArrayList();

        if(idxs.contains(idx))    {
            return;
        }

        idxs.add(idx);
        pcodeIncomingUnspent.put(pcode, idxs);
    }

    public void removeUnspent(final String pcode, final Integer idx)    {

        final List<Integer> idxs = pcodeIncomingUnspent.get(pcode);
        if(isNull(idxs)) return;
        if(idxs.contains(idx))    {
            idxs.remove(idx);
        }
        pcodeIncomingUnspent.put(pcode, idxs);
    }

    public Set<String> getUnspentProviders()    {
        return pcodeIncomingUnspent.keySet();
    }

    public List<Integer> getUnspent(final String pcode)    {
        return pcodeIncomingUnspent.get(pcode);
    }

    public List<String> getUnspentAddresses(final Context ctx, final String pcode)    {

        final List<String> ret = new ArrayList<>();

        try {
            final List<Integer> idxs = getUnspent(pcode);

            if(nonNull(idxs)) {
                for(int i = 0; i < idxs.size(); i++)   {
                    info("BIP47Meta", "address has unspents:" + BIP47Util.getInstance(ctx).getReceivePubKey(new PaymentCode(pcode), idxs.get(i)));
                    ret.add(BIP47Util.getInstance(ctx).getReceivePubKey(new PaymentCode(pcode), idxs.get(i)));
                }
            }
        } catch(final Exception e) {
            Log.e(TAG, e.getMessage(), e);
        }

        return ret;
    }

    public int getUnspentIdx(final String pcode)    {

        int ret = -1;

        try {
            final List<Integer> idxs = getUnspent(pcode);
            if(nonNull(idxs)) {
                for(int i = 0; i < idxs.size(); i++) {
                    if(idxs.get(i) > ret) {
                        ret = idxs.get(i);
                    }
                }
            }
        } catch(final Exception e) {
            Log.e(TAG, e.getMessage(), e);
        }

        return ret + 1;
    }

    synchronized public void remove(final String pcode) {
        pcodeNames.remove(pcode);
        final String label = pcodeLabels.remove(pcode);
        labelsPcode.remove(label);
        notFoundPcodeLabels.remove(pcode);
        followings.remove(pcode);
//        pcodeIncomingIdxs.remove(pcode);
        pcodeOutgoingIdxs.remove(pcode);
        pcodeOutgoingStatus.remove(pcode);
        pcodeIncomingUnspent.remove(pcode);
        pcodeIncomingStatus.remove(pcode);
        pcodeLatestEvent.remove(pcode);
    }

    public String getIncomingStatus(final String txHash)    {
        return pcodeIncomingStatus.get(txHash);
    }

    public void setIncomingStatus(final String txHash)    {
        pcodeIncomingStatus.put(txHash, "1");
    }

    public String getLatestEvent(final String pcode)    {
        return pcodeLatestEvent.get(pcode);
    }

    public void setLatestEvent(final String pcode, final String event)    {
        pcodeLatestEvent.put(pcode, event);
    }

    public boolean isRequiredRefresh() {
        return requiredRefresh;
    }

    public void setRequiredRefresh(final boolean requiredRefresh) {
        this.requiredRefresh = requiredRefresh;
    }

    public synchronized void pruneIncoming() {

        for(final String pcode : getPcodes())   {

            final Map<String,Integer> incomingIdxs = pcodeUnspentIdxs.get(pcode);
            final List<Integer> unspentIdxs = getUnspent(pcode);
            int highestUnspentIdx = getUnspentIdx(pcode);
            boolean changed = false;

//            info("BIP47Meta", "highest idx:" + highestUnspentIdx + "," + pcode);

            if(incomingIdxs != null && incomingIdxs.size() > 0)    {
                for(String addr : incomingIdxs.keySet())   {
                    if(unspentIdxs != null && incomingIdxs != null &&
                            incomingIdxs.get(addr) != null &&
                            !unspentIdxs.contains(incomingIdxs.get(addr)) && (incomingIdxs.get(addr) < (highestUnspentIdx - 5)))    {
//                        info("BIP47Meta", "pruning:" + addr + "," + incomingIdxs.get(addr) + ","  + pcode);
                        incomingIdxs.remove(addr);
                        changed = true;
                    }
                }
            }

            if(changed)    {
                pcodeUnspentIdxs.put(pcode, incomingIdxs);
            }
        }
    }

    synchronized public JSONObject toJSON() {

        final JSONObject jsonPayload = new JSONObject();

        try {

            final JSONArray pcodes = new JSONArray();
            for(final String pcode : pcodeLabels.keySet()) {

                final JSONObject pobj = new JSONObject();

                pobj.put("payment_code", pcode);
                pobj.put("name", pcodeNames.get(pcode));
                pobj.put("label", pcodeLabels.get(pcode));
                pobj.put("archived", pcodeArchived.get(pcode));
                pobj.put("segwit", pcodeSegwit.get(pcode));
                pobj.put("following", followings.get(pcode));

                if(pcodeUnspentIdxs.containsKey(pcode))    {
                    final Map<String, Integer> incoming = pcodeUnspentIdxs.get(pcode);
                    final JSONArray _incoming = new JSONArray();
                    for(final String s : incoming.keySet())   {
                        JSONObject o = new JSONObject();
                        o.put("addr", s);
                        o.put("idx", incoming.get(s));
                        _incoming.put(o);
                    }
                    pobj.put("in_idx", _incoming);
                }

                // addr2pcode not save to JSON
                // addr2idx not save to JSON

                if(pcodeIncomingIdxs.get(pcode) != null)    {
                    pobj.put("_in_idx", pcodeIncomingIdxs.get(pcode));
                }
                else    {
                    pobj.put("_in_idx", 0);
                }

                if(pcodeOutgoingIdxs.get(pcode) != null)    {
                    pobj.put("out_idx", pcodeOutgoingIdxs.get(pcode));
                }
                else    {
                    pobj.put("out_idx", 0);
                }

                if(pcodeOutgoingStatus.get(pcode) != null)    {
                    pobj.put("out_status", pcodeOutgoingStatus.get(pcode).getRight());
                    pobj.put("out_tx", pcodeOutgoingStatus.get(pcode).getLeft());
                } else {
                    pobj.put("out_status", BIP47Meta.STATUS_NOT_SENT);
                    pobj.put("out_tx", "");
                }

                final List<Integer> idxs = pcodeIncomingUnspent.get(pcode);
                if(idxs != null)    {
                    final JSONArray _idxs = new JSONArray();
                    for(int idx : idxs) {
                        _idxs.put(idx);
                    }
                    pobj.put("in_utxo", _idxs);
                }

                String event = pcodeLatestEvent.get(pcode);
                if(event != null)    {
                    pobj.put("latest_event", event);
                }

                pcodes.put(pobj);
            }
            jsonPayload.put("pcodes", pcodes);

            final JSONArray notFoundPcodes = new JSONArray();
            for (final Map.Entry<String, String> pcodeLabel : notFoundPcodeLabels.entrySet()) {
                final JSONObject pobj = new JSONObject();
                pobj.put("payment_code", pcodeLabel.getKey());
                pobj.put("label", pcodeLabel.getValue());
                notFoundPcodes.put(pobj);
            }
            jsonPayload.put("not_found_pcodes", notFoundPcodes);

            final JSONArray hashes = new JSONArray();
            for(String hash : pcodeIncomingStatus.keySet())   {
                hashes.put(hash);
            }
            jsonPayload.put("incoming_notif_hashes", hashes);

        } catch(final JSONException je) {
            Log.e(TAG, je.getMessage(), je);
        }

//        info("BIP47Meta", jsonPayload.toString());

        return jsonPayload;
    }

    public void fromJSON(JSONObject jsonPayload) {

//        info("BIP47Meta", jsonPayload.toString());

        try {

            final JSONArray pcodes = jsonPayload.has("pcodes")
                    ? jsonPayload.getJSONArray("pcodes")
                    : new JSONArray();

            for(int i = 0; i < pcodes.length(); i++) {

                final JSONObject obj = pcodes.getJSONObject(i);

                final String paymentCode = obj.getString("payment_code");
                final String label = obj.getString("label");
                pcodeLabels.put(paymentCode, label);
                labelsPcode.put(label, paymentCode);
                if (obj.has("name")) {
                    pcodeNames.put(paymentCode, obj.getString("name"));
                } else {
                    pcodeNames.put(paymentCode, label); // to manage old version
                }
                if (obj.has("following")) {
                    followings.put(paymentCode, obj.getBoolean("following"));
                }
                pcodeArchived.put(paymentCode, obj.has("archived") ? obj.getBoolean("archived") : false);
                pcodeSegwit.put(paymentCode, obj.has("segwit") ? obj.getBoolean("segwit") : false);

                if(obj.has("in_idx"))    {
                    ConcurrentHashMap<String,Integer> incoming = new ConcurrentHashMap<String,Integer>();
                    JSONArray _incoming = obj.getJSONArray("in_idx");
                    for(int j = 0; j < _incoming.length(); j++)   {
                        JSONObject o = _incoming.getJSONObject(j);
                        String addr = o.getString("addr");
                        int idx = o.getInt("idx");
                        incoming.put(addr, idx);
//                        info("BIP47Meta", addr);
//                        info("BIP47Meta", obj.getString("payment_code"));
//                        info("BIP47Meta", "" + idx);
                        addr2pcode.put(addr, paymentCode);
                        addr2idx.put(addr, idx);
                    }
                    pcodeUnspentIdxs.put(paymentCode, incoming);
                }

                if(obj.has("_in_idx"))    {
                    pcodeIncomingIdxs.put(paymentCode, obj.getInt("_in_idx"));
                }

                if(obj.has("out_idx"))    {
                    pcodeOutgoingIdxs.put(paymentCode, obj.getInt("out_idx"));
                }

                if(obj.has("out_tx") && obj.has("out_status"))    {
                    pcodeOutgoingStatus.put(paymentCode, Pair.of(obj.getString("out_tx"), obj.getInt("out_status")));
                }
                else    {
                    pcodeOutgoingStatus.put(paymentCode, Pair.of("", BIP47Meta.STATUS_NOT_SENT));
                }

                if(obj.has("in_utxo"))    {
                    JSONArray _idxs = obj.getJSONArray("in_utxo");
                    for(int k = 0; k < _idxs.length(); k++)   {
                        addUnspent(paymentCode, _idxs.getInt(k));
                    }
                }

                if(obj.has("latest_event"))    {
                    pcodeLatestEvent.put(paymentCode, obj.getString("latest_event"));
                }

            }

            if(jsonPayload.has("incoming_notif_hashes"))    {
                JSONArray hashes = jsonPayload.getJSONArray("incoming_notif_hashes");
                for(int i = 0; i < hashes.length(); i++) {
                    pcodeIncomingStatus.put(hashes.getString(i), "1");
                }
            }

            final JSONArray notFoundPcodes = jsonPayload.has("not_found_pcodes")
                    ? jsonPayload.getJSONArray("not_found_pcodes")
                    : new JSONArray();

            for(int i = 0; i < notFoundPcodes.length(); i++) {
                final JSONObject obj = notFoundPcodes.getJSONObject(i);
                final String paymentCode = obj.getString("payment_code");
                final String label = obj.getString("label");
                notFoundPcodeLabels.put(paymentCode, label);
            }

        } catch(final JSONException ex) {
            Log.e(TAG, ex.getMessage(), ex);
            throw new RuntimeException(ex);
        }
    }

    public static String getMixingPartnerCode() {
        if(SamouraiWallet.getInstance().isTestNet()){
            return getStrSamouraiMixingPcodeTestnet;
        }else{
            return getStrSamouraiMixingPcodeMainnet;
        }
    }
}
