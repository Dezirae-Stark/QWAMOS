import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/colors.dart';
import '../theme/typography.dart';

class SecureTypeKeyboardSettingsWidget extends StatefulWidget {
  const SecureTypeKeyboardSettingsWidget({super.key});

  @override
  State<SecureTypeKeyboardSettingsWidget> createState() => _SecureTypeKeyboardSettingsWidgetState();
}

class _SecureTypeKeyboardSettingsWidgetState extends State<SecureTypeKeyboardSettingsWidget> {
  String _mode = 'Standard';
  bool _mlAnomalyDetection = true;
  bool _antiKeylogging = true;
  bool _antiScreenshot = true;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: QwamosColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: QwamosColors.neonGreen.withOpacity(0.3), width: 1.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.keyboard, color: QwamosColors.neonGreen, size: 28),
              const SizedBox(width: 12),
              Expanded(child: Text('SECURETYPE KEYBOARD', style: QwamosTypography.h5.copyWith(color: QwamosColors.neonGreen))),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(color: QwamosColors.neonGreen.withOpacity(0.2), borderRadius: BorderRadius.circular(4)),
                child: Row(
                  children: [
                    Icon(Icons.lock, size: 12, color: QwamosColors.neonGreen),
                    const SizedBox(width: 4),
                    Text('PQ', style: QwamosTypography.mono.copyWith(color: QwamosColors.neonGreen, fontSize: 10, fontWeight: FontWeight.bold)),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text('KEYBOARD MODE', style: QwamosTypography.labelSmall),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            children: ['Standard', 'Password', 'Terminal', 'Gesture'].map((m) => ChoiceChip(
                  label: Text(m, style: TextStyle(fontSize: 11)),
                  selected: _mode == m,
                  onSelected: (v) => setState(() => _mode = m),
                  selectedColor: QwamosColors.neonGreen.withOpacity(0.3),
                )).toList(),
          ),
          const SizedBox(height: 16),
          Text('SECURITY FEATURES', style: QwamosTypography.labelSmall),
          const SizedBox(height: 10),
          _buildToggle('ML Anomaly Detection', _mlAnomalyDetection, (v) => setState(() => _mlAnomalyDetection = v)),
          _buildToggle('Anti-Keylogging', _antiKeylogging, (v) => setState(() => _antiKeylogging = v)),
          _buildToggle('Anti-Screenshot', _antiScreenshot, (v) => setState(() => _antiScreenshot = v)),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(color: QwamosColors.neonGreen.withOpacity(0.1), borderRadius: BorderRadius.circular(6)),
            child: Row(
              children: [
                Icon(Icons.verified_user, color: QwamosColors.neonGreen, size: 16),
                const SizedBox(width: 10),
                Expanded(child: Text('Zero Telemetry • No Internet Permission', style: QwamosTypography.labelSmall.copyWith(color: QwamosColors.neonGreen, fontSize: 11))),
              ],
            ),
          ),
        ],
      ),
    ).animate().fadeIn(duration: 300.ms);
  }

  Widget _buildToggle(String label, bool value, ValueChanged<bool> onChanged) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Expanded(child: Text(label, style: QwamosTypography.body.copyWith(fontSize: 13))),
          Switch(value: value, onChanged: onChanged, activeColor: QwamosColors.neonGreen),
        ],
      ),
    );
  }
}
