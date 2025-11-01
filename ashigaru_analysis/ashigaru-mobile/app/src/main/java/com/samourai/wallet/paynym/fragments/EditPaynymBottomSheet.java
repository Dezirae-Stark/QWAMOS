package com.samourai.wallet.paynym.fragments;

import android.os.Bundle;

import com.google.android.material.bottomsheet.BottomSheetDialogFragment;

import androidx.core.content.FileProvider;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;

import com.google.android.material.button.MaterialButton;
import com.google.android.material.textfield.TextInputEditText;
import com.samourai.wallet.R;

public class EditPaynymBottomSheet extends BottomSheetDialogFragment {


    public enum type {EDIT, SAVE}

    private String pcode;
    private String label;
    private String buttonText;


    private TextInputEditText labelEdt;
    private MaterialButton saveButton;
    private MaterialButton removeNickBtn;
    private View.OnClickListener onClickListener;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.bottomsheet_edit_paynym, null);

        pcode = getArguments().getString("pcode");
        label = getArguments().getString("label");
        if(label.contains("(not followed)")){
            label = label.replace("(not followed)", "");
        }
        if(label.contains("(not confirmed)")){
            label =      label.replace("(not confirmed)", "");
        }
        buttonText = getArguments().getString("buttonText");

        labelEdt = view.findViewById(R.id.paynym_label);
        saveButton = view.findViewById(R.id.edit_paynym_button);
        removeNickBtn = view.findViewById(R.id.remove_nickname_button);

        labelEdt.setText(label);
        saveButton.setText(buttonText);
        removeNickBtn.setText("Delete nickname and save");
        if (getArguments().getString("nymName").equals(label))
            removeNickBtn.setVisibility(View.GONE);
        saveButton.setOnClickListener(button -> {
            this.dismiss();
            if (onClickListener != null) {
                onClickListener.onClick(button);
            }
        });

        removeNickBtn.setOnClickListener(button -> {
            labelEdt.setText(getArguments().getString("nymName"));
            this.dismiss();
            if (onClickListener != null) {
                onClickListener.onClick(button);
            }
        });
        return view;
    }

    public String getPcode() {
        return pcode;
    }

    public String getLabel() {
        return labelEdt.getText().toString();
    }

    public void setSaveButtonListener(View.OnClickListener listener) {
        onClickListener = listener;
    }
}