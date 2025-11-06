import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/colors.dart';
import '../theme/typography.dart';

class EmergencyProtectionWidget extends StatefulWidget {
  const EmergencyProtectionWidget({super.key});

  @override
  State<EmergencyProtectionWidget> createState() => _EmergencyProtectionWidgetState();
}

class _EmergencyProtectionWidgetState extends State<EmergencyProtectionWidget> {
  bool _panicGestureEnabled = true;
  bool _duressProfilesEnabled = false;
  String _panicAction = 'Wipe + Radio Kill';

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: QwamosColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: QwamosColors.amberWarning.withOpacity(0.5), width: 2),
        boxShadow: [BoxShadow(color: QwamosColors.amberWarning.withOpacity(0.2), blurRadius: 12)],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.emergency, color: QwamosColors.amberWarning, size: 28),
              const SizedBox(width: 12),
              Text('EMERGENCY PROTECTION', style: QwamosTypography.h5.copyWith(color: QwamosColors.amberWarning)),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: QwamosColors.amberWarning.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: QwamosColors.amberWarning.withOpacity(0.3)),
            ),
            child: Row(
              children: [
                Icon(Icons.touch_app, color: QwamosColors.amberWarning, size: 20),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Panic Gesture', style: QwamosTypography.h6.copyWith(fontSize: 14)),
                      Text('Power + VolUp + Fingerprint', style: QwamosTypography.labelSmall.copyWith(fontSize: 11)),
                    ],
                  ),
                ),
                Switch(value: _panicGestureEnabled, onChanged: (v) => setState(() => _panicGestureEnabled = v), activeColor: QwamosColors.amberWarning),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Text('PANIC ACTION', style: QwamosTypography.labelSmall),
          const SizedBox(height: 8),
          ...['Wipe + Radio Kill', 'Radio Kill Only', 'Duress Profile'].map((action) => RadioListTile<String>(
                dense: true,
                contentPadding: EdgeInsets.zero,
                title: Text(action, style: QwamosTypography.body.copyWith(fontSize: 13)),
                value: action,
                groupValue: _panicAction,
                onChanged: (v) => setState(() => _panicAction = v!),
                activeColor: QwamosColors.amberWarning,
              )),
          const Divider(height: 24),
          Row(
            children: [
              Expanded(child: Text('Duress Profiles', style: QwamosTypography.body)),
              Switch(value: _duressProfilesEnabled, onChanged: (v) => setState(() => _duressProfilesEnabled = v), activeColor: QwamosColors.cyberViolet),
            ],
          ),
          if (_duressProfilesEnabled) ...[
            const SizedBox(height: 12),
            OutlinedButton(
              onPressed: () {},
              style: OutlinedButton.styleFrom(foregroundColor: QwamosColors.cyberViolet, side: BorderSide(color: QwamosColors.cyberViolet.withOpacity(0.5))),
              child: Text('CONFIGURE DECOY USER'),
            ),
          ],
        ],
      ),
    ).animate().fadeIn(duration: 300.ms);
  }
}
