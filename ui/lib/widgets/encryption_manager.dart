import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/colors.dart';
import '../theme/typography.dart';
import '../theme/glow_effects.dart';

class EncryptionManagerWidget extends StatefulWidget {
  const EncryptionManagerWidget({super.key});

  @override
  State<EncryptionManagerWidget> createState() => _EncryptionManagerWidgetState();
}

class _EncryptionManagerWidgetState extends State<EncryptionManagerWidget> {
  String _selectedAlgorithm = 'KYBER-1024';
  String _selectedHash = 'CHACHA20-POLY1305';

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: GlowEffects.neonGlow(
        glowColor: QwamosColors.neonGreen,
        borderRadius: 12,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.vpn_key,
                color: QwamosColors.neonGreen,
                size: 24,
              ),
              const SizedBox(width: 12),
              Text(
                'ENCRYPTION MANAGER',
                style: QwamosTypography.h5.copyWith(
                  color: QwamosColors.neonGreen,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          // Algorithm Selector
          Text(
            'ALGORITHM',
            style: QwamosTypography.labelSmall,
          ),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            decoration: BoxDecoration(
              color: QwamosColors.background,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: QwamosColors.neonGreen.withOpacity(0.3),
                width: 1.5,
              ),
            ),
            child: DropdownButton<String>(
              value: _selectedAlgorithm,
              isExpanded: true,
              underline: const SizedBox(),
              dropdownColor: QwamosColors.surface,
              style: QwamosTypography.mono.copyWith(
                color: QwamosColors.neonGreen,
              ),
              items: [
                'KYBER-1024',
                'KYBER-768',
                'KYBER-512',
                'DILITHIUM-5',
              ].map((String value) {
                return DropdownMenuItem<String>(
                  value: value,
                  child: Text(value),
                );
              }).toList(),
              onChanged: (String? newValue) {
                if (newValue != null) {
                  setState(() {
                    _selectedAlgorithm = newValue;
                  });
                }
              },
            ),
          ),
          const SizedBox(height: 16),
          // Hash Selector
          Text(
            'HASH FUNCTION',
            style: QwamosTypography.labelSmall,
          ),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            decoration: BoxDecoration(
              color: QwamosColors.background,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: QwamosColors.neonGreen.withOpacity(0.3),
                width: 1.5,
              ),
            ),
            child: DropdownButton<String>(
              value: _selectedHash,
              isExpanded: true,
              underline: const SizedBox(),
              dropdownColor: QwamosColors.surface,
              style: QwamosTypography.mono.copyWith(
                color: QwamosColors.neonGreen,
              ),
              items: [
                'CHACHA20-POLY1305',
                'AES-256-GCM',
                'SERPENT-256',
              ].map((String value) {
                return DropdownMenuItem<String>(
                  value: value,
                  child: Text(value),
                );
              }).toList(),
              onChanged: (String? newValue) {
                if (newValue != null) {
                  setState(() {
                    _selectedHash = newValue;
                  });
                }
              },
            ),
          ),
          const SizedBox(height: 16),
          // Build Button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () {},
              style: ElevatedButton.styleFrom(
                backgroundColor: QwamosColors.neonGreen,
                foregroundColor: QwamosColors.background,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: Text(
                'BUILD KEY',
                style: QwamosTypography.button.copyWith(
                  color: QwamosColors.background,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        ],
      ),
    )
        .animate()
        .fadeIn(duration: 300.ms, curve: Curves.easeInOutCubic)
        .slideY(
          begin: 0.1,
          end: 0,
          duration: 300.ms,
          curve: Curves.easeInOutCubic,
        );
  }
}
