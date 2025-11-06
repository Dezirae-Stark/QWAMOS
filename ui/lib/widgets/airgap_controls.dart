import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/colors.dart';
import '../theme/typography.dart';
import '../theme/glow_effects.dart';

class AirgapControlsWidget extends StatefulWidget {
  const AirgapControlsWidget({super.key});

  @override
  State<AirgapControlsWidget> createState() => _AirgapControlsWidgetState();
}

class _AirgapControlsWidgetState extends State<AirgapControlsWidget> {
  bool _airgapEnabled = true;
  bool _usbBlocked = true;
  bool _bluetoothBlocked = true;
  bool _nfcBlocked = false;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: QwamosColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: QwamosColors.cyberViolet.withOpacity(0.3),
          width: 1.5,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.wifi_off,
                color: QwamosColors.cyberViolet,
                size: 24,
              ),
              const SizedBox(width: 12),
              Text(
                'AIRGAP CONTROLS',
                style: QwamosTypography.h5.copyWith(
                  color: QwamosColors.cyberViolet,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          // Main Airgap Toggle
          _buildToggleRow(
            'AIRGAP ENABLED',
            _airgapEnabled,
            QwamosColors.cyberViolet,
            (value) {
              setState(() {
                _airgapEnabled = value;
              });
            },
          ),
          const Divider(height: 24, color: Color(0xFF1A1F2E)),
          // Individual Controls
          _buildToggleRow(
            'Block USB',
            _usbBlocked,
            QwamosColors.neonGreen,
            (value) {
              setState(() {
                _usbBlocked = value;
              });
            },
          ),
          const SizedBox(height: 12),
          _buildToggleRow(
            'Block Bluetooth',
            _bluetoothBlocked,
            QwamosColors.neonGreen,
            (value) {
              setState(() {
                _bluetoothBlocked = value;
              });
            },
          ),
          const SizedBox(height: 12),
          _buildToggleRow(
            'Block NFC',
            _nfcBlocked,
            QwamosColors.textSecondary,
            (value) {
              setState(() {
                _nfcBlocked = value;
              });
            },
          ),
          const SizedBox(height: 16),
          // Configure Button
          SizedBox(
            width: double.infinity,
            child: OutlinedButton(
              onPressed: () {},
              style: OutlinedButton.styleFrom(
                foregroundColor: QwamosColors.cyberViolet,
                side: BorderSide(
                  color: QwamosColors.cyberViolet.withOpacity(0.5),
                  width: 1.5,
                ),
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: Text(
                'CONFIGURE BACKUP POLICIES',
                style: QwamosTypography.button.copyWith(
                  color: QwamosColors.cyberViolet,
                ),
              ),
            ),
          ),
        ],
      ),
    )
        .animate()
        .fadeIn(duration: 300.ms, curve: Curves.easeInOutCubic)
        .slideX(
          begin: 0.1,
          end: 0,
          duration: 300.ms,
          curve: Curves.easeInOutCubic,
        );
  }

  Widget _buildToggleRow(
    String label,
    bool value,
    Color activeColor,
    ValueChanged<bool> onChanged,
  ) {
    return Row(
      children: [
        Expanded(
          child: Text(
            label,
            style: QwamosTypography.body.copyWith(
              color: value ? QwamosColors.textPrimary : QwamosColors.textSecondary,
            ),
          ),
        ),
        Switch(
          value: value,
          onChanged: onChanged,
          activeColor: activeColor,
          activeTrackColor: activeColor.withOpacity(0.3),
          inactiveThumbColor: QwamosColors.textSecondary,
          inactiveTrackColor: QwamosColors.background,
        ),
      ],
    );
  }
}
