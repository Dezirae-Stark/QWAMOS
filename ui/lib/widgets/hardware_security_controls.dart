import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/colors.dart';
import '../theme/typography.dart';
import '../theme/glow_effects.dart';

class HardwareSecurityControlsWidget extends StatefulWidget {
  const HardwareSecurityControlsWidget({super.key});

  @override
  State<HardwareSecurityControlsWidget> createState() => _HardwareSecurityControlsWidgetState();
}

class _HardwareSecurityControlsWidgetState extends State<HardwareSecurityControlsWidget> {
  bool _mlBootloaderLock = true;
  bool _firmwareMonitoring = true;
  bool _abPartitionIsolation = true;
  final Map<String, bool> _killSwitches = {'Camera': false, 'Microphone': false, 'Cellular': false};

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: QwamosColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: QwamosColors.redCritical.withOpacity(0.5), width: 2),
        boxShadow: [BoxShadow(color: QwamosColors.redCritical.withOpacity(0.2), blurRadius: 12)],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.hardware, color: QwamosColors.redCritical, size: 28),
              const SizedBox(width: 12),
              Text('HARDWARE SECURITY', style: QwamosTypography.h5.copyWith(color: QwamosColors.redCritical)),
            ],
          ),
          const SizedBox(height: 16),
          _buildToggle('ML Bootloader Lock', _mlBootloaderLock, (v) => setState(() => _mlBootloaderLock = v)),
          _buildToggle('Firmware Monitoring', _firmwareMonitoring, (v) => setState(() => _firmwareMonitoring = v)),
          _buildToggle('A/B Partition Isolation', _abPartitionIsolation, (v) => setState(() => _abPartitionIsolation = v)),
          const Divider(height: 24),
          Text('HARDWARE KILL SWITCHES', style: QwamosTypography.labelSmall),
          const SizedBox(height: 12),
          ..._killSwitches.entries.map((e) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  children: [
                    Icon(Icons.power_settings_new, size: 16, color: e.value ? QwamosColors.redCritical : QwamosColors.textSecondary),
                    const SizedBox(width: 12),
                    Expanded(child: Text(e.key, style: QwamosTypography.body.copyWith(fontSize: 13))),
                    Switch(value: e.value, onChanged: (v) => setState(() => _killSwitches[e.key] = v), activeColor: QwamosColors.redCritical),
                  ],
                ),
              )),
        ],
      ),
    ).animate().fadeIn(duration: 300.ms).shake(duration: 500.ms, hz: 2);
  }

  Widget _buildToggle(String label, bool value, ValueChanged<bool> onChanged) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        children: [
          GlowEffects.statusDot(color: value ? QwamosColors.neonGreen : QwamosColors.textSecondary, size: 8, isAnimated: value),
          const SizedBox(width: 12),
          Expanded(child: Text(label, style: QwamosTypography.body.copyWith(fontSize: 13))),
          Switch(value: value, onChanged: onChanged, activeColor: QwamosColors.neonGreen),
        ],
      ),
    );
  }
}
