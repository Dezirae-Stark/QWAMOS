package com.samourai.wallet.util.func;

import static com.samourai.wallet.constants.SamouraiAccountIndex.DEPOSIT;
import static com.samourai.wallet.constants.SamouraiAccountIndex.POSTMIX;
import static com.samourai.wallet.util.func.EnumAddressType.BIP84_SEGWIT_NATIVE;

import android.content.Context;

import com.google.common.collect.Maps;
import com.samourai.wallet.R;
import com.samourai.wallet.constants.WALLET_INDEX;
import com.samourai.wallet.tools.AddressCalculatorViewModel;
import com.samourai.wallet.tools.AddressDetailsModel;

import org.apache.commons.lang3.StringUtils;

import java.util.Map;

import static java.lang.Math.max;
import static java.util.Objects.isNull;

public class AddressHelper {

    private AddressHelper() {}

    public static int searchAddressIndex(
            final String addressToLook,
            final String addressTypeAsString,
            final boolean isExternal,
            final int startIndex,
            final int endIndex,
            final Context context) {

        for (int index = startIndex; index < endIndex; ++index) {
            final AddressDetailsModel model = AddressCalculatorViewModel.Companion.addressDetailsModel(
                    addressTypeAsString,
                    isExternal,
                    index,
                    context);
            final String pubKey = model.getPubKey();
            if (StringUtils.equals(pubKey, addressToLook)) return index;
        }
        return Integer.MIN_VALUE;
    }

    public static AddressInfo isMyDepositOrPostmixAddress(
            final Context context,
            final String address,
            final int scanIndexMargin) {

        final AddressFactory addressFactory = AddressFactory.getInstance(context);

        final EnumAddressType addressType = EnumAddressType.fromAddress(address);
        final String[] types = context.getResources().getStringArray(R.array.account_types);
        final String addrTypeAsString;
        final Map<Boolean, Integer> currentIndex = Maps.newHashMap();
        switch (addressType) {
            case BIP49_SEGWIT_COMPAT:
                addrTypeAsString = types[0];
                currentIndex.put(true, addressFactory.getIndex(WALLET_INDEX.BIP49_RECEIVE));
                currentIndex.put(false, addressFactory.getIndex(WALLET_INDEX.BIP49_CHANGE));
                break;
            case BIP84_SEGWIT_NATIVE:
                addrTypeAsString = types[1];
                currentIndex.put(true, addressFactory.getIndex(WALLET_INDEX.BIP84_RECEIVE));
                currentIndex.put(false, addressFactory.getIndex(WALLET_INDEX.BIP84_CHANGE));
                break;
            case BIP44_LEGACY:
                addrTypeAsString = types[2];
                currentIndex.put(true, addressFactory.getIndex(WALLET_INDEX.BIP44_RECEIVE));
                currentIndex.put(false, addressFactory.getIndex(WALLET_INDEX.BIP44_CHANGE));
                break;
            default:
                addrTypeAsString = null;
                currentIndex.put(true, Integer.MIN_VALUE);
                currentIndex.put(false, Integer.MIN_VALUE);
                break;
        }

        if (isNull(addrTypeAsString)) {
            return AddressInfo.createAddressInfo(
                    address,
                    false,
                    null,
                    null,
                    null,
                    addressType.getType());
        }

        boolean isExternal = true;
        int startIdx = max(0, currentIndex.get(isExternal) - scanIndexMargin);
        int endIdx = currentIndex.get(isExternal)  + scanIndexMargin;

        int indexFound = searchAddressIndex(
                address,
                addrTypeAsString,
                isExternal,
                startIdx,
                endIdx,
                context);
        if (indexFound < endIdx && indexFound >= startIdx) {
            return AddressInfo.createAddressInfo(
                    address,
                    true,
                    indexFound,
                    isExternal ? 0 : 1,
                    DEPOSIT,
                    addressType.getType());
        }

        isExternal = false;
        startIdx = max(0, currentIndex.get(isExternal) - scanIndexMargin);
        endIdx = currentIndex.get(isExternal)  + scanIndexMargin;

        indexFound = searchAddressIndex(
                address,
                addrTypeAsString,
                isExternal,
                startIdx,
                endIdx,
                context);
        if (indexFound < endIdx && indexFound >= startIdx) {
            return AddressInfo.createAddressInfo(
                    address,
                    true,
                    indexFound,
                    isExternal ? 0 : 1,
                    DEPOSIT,
                    addressType.getType());
        }

        if (addressType == BIP84_SEGWIT_NATIVE) {
            int index = addressFactory.getIndex(WALLET_INDEX.POSTMIX_RECEIVE);
            startIdx = max(0, index - scanIndexMargin);
            endIdx = index  + scanIndexMargin;
            indexFound = searchAddressIndex(
                    address,
                    types[5], // postmix account
                    true,
                    startIdx,
                    endIdx,
                    context);

            if (indexFound < endIdx && indexFound >= startIdx) {
                return AddressInfo.createAddressInfo(
                        address,
                        true,
                        indexFound,
                        0,
                        POSTMIX,
                        addressType.getType());
            }

            index = addressFactory.getIndex(WALLET_INDEX.POSTMIX_CHANGE);
            startIdx = max(0, index - scanIndexMargin);
            endIdx = index  + scanIndexMargin;
            indexFound = searchAddressIndex(
                    address,
                    types[5], // postmix account
                    false,
                    startIdx,
                    endIdx,
                    context);

            if (indexFound < endIdx && indexFound >= startIdx) {
                return AddressInfo.createAddressInfo(
                        address,
                        true,
                        indexFound,
                        1,
                        POSTMIX,
                        addressType.getType());
            }
        }

        return AddressInfo.createAddressInfo(
                address,
                false,
                null,
                null,
                null,
                addressType.getType());
    }

    public static class AddressInfo {
        private String addr;
        private boolean found;
        private Integer index;
        private Integer chain;
        private Integer addrType;
        private Integer accountIdx;

        public static AddressInfo createAddressInfo(
                final String addr,
                final boolean found,
                final Integer index,
                final Integer chain,
                final Integer accountIdx,
                final Integer addrType
        ) {
            final AddressInfo addressInfo = new AddressInfo();
            addressInfo.addr = addr;
            addressInfo.found = found;
            addressInfo.index = index;
            addressInfo.chain = chain;
            addressInfo.accountIdx = accountIdx;
            addressInfo.addrType = addrType;
            return addressInfo;
        }

        public String getAddr() {
            return addr;
        }

        public boolean isFound() {
            return found;
        }

        public Integer getIndex() {
            return index;
        }

        public Integer getChain() {
            return chain;
        }

        public Integer getAccountIdx() {
            return accountIdx;
        }

        public Integer getAddrType() {
            return addrType;
        }
    }
}
