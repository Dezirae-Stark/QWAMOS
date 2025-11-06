import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/colors.dart';
import '../theme/typography.dart';

class Dom0PolicyManagerWidget extends StatefulWidget {
  const Dom0PolicyManagerWidget({super.key});

  @override
  State<Dom0PolicyManagerWidget> createState() => _Dom0PolicyManagerWidgetState();
}

class _Dom0PolicyManagerWidgetState extends State<Dom0PolicyManagerWidget> {
  final Map<String, Map<String, dynamic>> _policies = {
    'STRICT_FIREWALL': {'enabled': true, 'rebootRequired': true},
    'BASEBAND_ISOLATION': {'enabled': true, 'rebootRequired': true},
    'KERNEL_HARDENING': {'enabled': true, 'rebootRequired': true},
    'IMS_VOLTE_BLOCK': {'enabled': false, 'rebootRequired': false},
    'RADIO_KILL_SWITCH': {'enabled': false, 'rebootRequired': false},
    'GUEST_ISOLATION': {'enabled': true, 'rebootRequired': false},
    'MAC_RANDOMIZATION': {'enabled': true, 'rebootRequired': false},
    'DNS_OVER_TOR': {'enabled': true, 'rebootRequired': false},
    'APP_SANDBOX': {'enabled': true, 'rebootRequired': false},
    'VERIFIED_BOOT': {'enabled': true, 'rebootRequired': true},
    'SECURE_ERASE': {'enabled': true, 'rebootRequired': false},
    'DURESS_PROFILES': {'enabled': false, 'rebootRequired': false},
  };

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
              Icon(Icons.admin_panel_settings, color: QwamosColors.neonGreen, size: 28),
              const SizedBox(width: 12),
              Expanded(
                child: Text('DOM0 POLICY MANAGER', style: QwamosTypography.h5.copyWith(color: QwamosColors.neonGreen)),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(color: QwamosColors.neonGreen.withOpacity(0.2), borderRadius: BorderRadius.circular(4)),
                child: Text('12 Policies', style: QwamosTypography.mono.copyWith(color: QwamosColors.neonGreen, fontSize: 10)),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ..._policies.entries.map((e) => _buildPolicyRow(e.key, e.value)),
        ],
      ),
    ).animate().fadeIn(duration: 300.ms);
  }

  Widget _buildPolicyRow(String name, Map<String, dynamic> policy) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        children: [
          Icon(
            policy['rebootRequired'] ? Icons.restart_alt : Icons.check_circle_outline,
            size: 16,
            color: policy['rebootRequired'] ? QwamosColors.amberWarning : QwamosColors.aquaBlue,
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              name.replaceAll('_', ' '),
              style: QwamosTypography.mono.copyWith(fontSize: 12),
            ),
          ),
          Switch(
            value: policy['enabled'],
            onChanged: (v) => setState(() => _policies[name]!['enabled'] = v),
            activeColor: QwamosColors.neonGreen,
          ),
        ],
      ),
    );
  }
}
