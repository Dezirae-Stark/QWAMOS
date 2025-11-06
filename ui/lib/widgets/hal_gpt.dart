import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/colors.dart';
import '../theme/typography.dart';
import '../theme/glow_effects.dart';

class HalGptWidget extends StatefulWidget {
  const HalGptWidget({super.key});

  @override
  State<HalGptWidget> createState() => _HalGptWidgetState();
}

class _HalGptWidgetState extends State<HalGptWidget> {
  bool _learningEnabled = true;

  final List<Map<String, dynamic>> _modules = [
    {'name': 'Auto-Aegis', 'status': 'IDLE', 'active': false},
    {'name': 'ShadowNet', 'status': 'READY', 'active': true},
    {'name': 'Neural_Kernel', 'status': 'TRAINING', 'active': true},
  ];

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: QwamosColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: QwamosColors.neonGreen.withOpacity(0.3),
          width: 1.5,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              Icon(
                Icons.psychology,
                color: QwamosColors.neonGreen,
                size: 24,
              ),
              const SizedBox(width: 12),
              Text(
                'HAL-GPT',
                style: QwamosTypography.h5.copyWith(
                  color: QwamosColors.neonGreen,
                ),
              ),
              const Spacer(),
              Row(
                children: [
                  GlowEffects.statusDot(
                    color: _learningEnabled
                        ? QwamosColors.neonGreen
                        : QwamosColors.textSecondary,
                    size: 8,
                    isAnimated: _learningEnabled,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    _learningEnabled ? 'LEARNING ON' : 'LEARNING OFF',
                    style: QwamosTypography.labelSmall.copyWith(
                      color: _learningEnabled
                          ? QwamosColors.neonGreen
                          : QwamosColors.textSecondary,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 16),
          // Neural Modules
          ..._modules.map((module) => Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: _buildModuleCard(
                  module['name'],
                  module['status'],
                  module['active'],
                ),
              )),
          const SizedBox(height: 8),
          // Master Toggle
          Row(
            children: [
              Expanded(
                child: Text(
                  'ENABLE NEURAL LEARNING',
                  style: QwamosTypography.body,
                ),
              ),
              Switch(
                value: _learningEnabled,
                onChanged: (value) {
                  setState(() {
                    _learningEnabled = value;
                  });
                },
                activeColor: QwamosColors.neonGreen,
                activeTrackColor: QwamosColors.neonGreen.withOpacity(0.3),
              ),
            ],
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

  Widget _buildModuleCard(String name, String status, bool isActive) {
    final Color statusColor = isActive
        ? QwamosColors.neonGreen
        : QwamosColors.textSecondary;

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: QwamosColors.background,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: statusColor.withOpacity(0.3),
          width: 1.5,
        ),
        boxShadow: isActive
            ? [
                BoxShadow(
                  color: statusColor.withOpacity(0.2),
                  blurRadius: 8,
                ),
              ]
            : [],
      ),
      child: Row(
        children: [
          // Module Icon
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: statusColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Icon(
              Icons.memory,
              color: statusColor,
              size: 20,
            ),
          ),
          const SizedBox(width: 12),
          // Module Info
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  name,
                  style: QwamosTypography.mono.copyWith(
                    color: QwamosColors.textPrimary,
                    fontSize: 13,
                  ),
                ),
                const SizedBox(height: 4),
                Row(
                  children: [
                    GlowEffects.statusDot(
                      color: statusColor,
                      size: 6,
                      isAnimated: status == 'TRAINING',
                    ),
                    const SizedBox(width: 6),
                    Text(
                      status,
                      style: QwamosTypography.labelSmall.copyWith(
                        color: statusColor,
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          // Init Button
          ElevatedButton(
            onPressed: isActive ? () {} : null,
            style: ElevatedButton.styleFrom(
              backgroundColor: statusColor.withOpacity(0.2),
              foregroundColor: statusColor,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              minimumSize: Size.zero,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(6),
                side: BorderSide(
                  color: statusColor.withOpacity(0.3),
                  width: 1.5,
                ),
              ),
            ),
            child: Text(
              'INIT',
              style: QwamosTypography.button.copyWith(
                color: statusColor,
                fontSize: 11,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
