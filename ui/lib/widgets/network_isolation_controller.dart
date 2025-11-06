import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/colors.dart';
import '../theme/typography.dart';
import '../theme/glow_effects.dart';

class NetworkIsolationControllerWidget extends StatefulWidget {
  const NetworkIsolationControllerWidget({super.key});

  @override
  State<NetworkIsolationControllerWidget> createState() => _NetworkIsolationControllerWidgetState();
}

class _NetworkIsolationControllerWidgetState extends State<NetworkIsolationControllerWidget> {
  String _selectedMode = 'Tor Only';
  final List<String> _modes = [
    'Direct',
    'Tor Only',
    'I2P Only',
    'Tor + I2P',
    'Tor + VPN',
    'Maximum Anonymity',
  ];

  final Map<String, bool> _serviceStatus = {
    'Tor': true,
    'I2P': false,
    'DNSCrypt': true,
    'VPN': false,
  };

  bool _killSwitchEnabled = true;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: QwamosColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: QwamosColors.aquaBlue.withOpacity(0.3), width: 1.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.public_off, color: QwamosColors.aquaBlue, size: 28),
              const SizedBox(width: 12),
              Text('NETWORK ISOLATION', style: QwamosTypography.h5.copyWith(color: QwamosColors.aquaBlue)),
            ],
          ),
          const SizedBox(height: 16),
          Text('ROUTING MODE', style: QwamosTypography.labelSmall),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _modes.map((mode) => _buildModeChip(mode)).toList(),
          ),
          const SizedBox(height: 16),
          Text('SERVICES', style: QwamosTypography.labelSmall),
          const SizedBox(height: 12),
          ..._serviceStatus.entries.map((e) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  children: [
                    GlowEffects.statusDot(color: e.value ? QwamosColors.neonGreen : QwamosColors.textSecondary, size: 8),
                    const SizedBox(width: 12),
                    Expanded(child: Text(e.key, style: QwamosTypography.body.copyWith(fontSize: 13))),
                    Switch(
                      value: e.value,
                      onChanged: (v) => setState(() => _serviceStatus[e.key] = v),
                      activeColor: QwamosColors.neonGreen,
                    ),
                  ],
                ),
              )),
          const Divider(height: 24),
          Row(
            children: [
              Expanded(child: Text('Kill Switch', style: QwamosTypography.body)),
              Switch(
                value: _killSwitchEnabled,
                onChanged: (v) => setState(() => _killSwitchEnabled = v),
                activeColor: QwamosColors.redCritical,
              ),
            ],
          ),
        ],
      ),
    ).animate().fadeIn(duration: 300.ms);
  }

  Widget _buildModeChip(String mode) {
    bool isSelected = mode == _selectedMode;
    return GestureDetector(
      onTap: () => setState(() => _selectedMode = mode),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? QwamosColors.aquaBlue.withOpacity(0.2) : QwamosColors.background,
          borderRadius: BorderRadius.circular(6),
          border: Border.all(color: isSelected ? QwamosColors.aquaBlue : QwamosColors.textSecondary.withOpacity(0.3)),
        ),
        child: Text(mode, style: QwamosTypography.button.copyWith(color: isSelected ? QwamosColors.aquaBlue : QwamosColors.textSecondary, fontSize: 11)),
      ),
    );
  }
}
