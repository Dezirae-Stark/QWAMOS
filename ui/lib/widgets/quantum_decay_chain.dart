import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/colors.dart';
import '../theme/typography.dart';
import '../theme/glow_effects.dart';

class QuantumDecayChainWidget extends StatelessWidget {
  const QuantumDecayChainWidget({super.key});

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
              GlowEffects.statusDot(
                color: QwamosColors.neonGreen,
                size: 10,
                isAnimated: true,
              ),
              const SizedBox(width: 12),
              Text(
                'QUANTUM DECAY CHAIN',
                style: QwamosTypography.h5.copyWith(
                  color: QwamosColors.neonGreen,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          // IP Status Boxes
          Row(
            children: [
              Expanded(
                child: _buildStatusBox(
                  'Tor',
                  'ONLINE',
                  QwamosColors.neonGreen,
                  '10.0.2.15',
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildStatusBox(
                  'I2P',
                  'ACTIVE',
                  QwamosColors.aquaBlue,
                  '127.0.0.1',
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _buildStatusBox(
                  'VPN',
                  'DEAD',
                  QwamosColors.redCritical,
                  'N/A',
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildStatusBox(
                  'DNS',
                  'ACTIVE',
                  QwamosColors.neonGreen,
                  '1.1.1.1',
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          // Action Buttons
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: () {},
                  style: OutlinedButton.styleFrom(
                    foregroundColor: QwamosColors.aquaBlue,
                    side: BorderSide(
                      color: QwamosColors.aquaBlue.withOpacity(0.5),
                      width: 1.5,
                    ),
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: Text(
                    'Configure',
                    style: QwamosTypography.button.copyWith(
                      color: QwamosColors.aquaBlue,
                      fontSize: 12,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton(
                  onPressed: () {},
                  style: ElevatedButton.styleFrom(
                    backgroundColor: QwamosColors.neonGreen.withOpacity(0.2),
                    foregroundColor: QwamosColors.neonGreen,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                      side: BorderSide(
                        color: QwamosColors.neonGreen.withOpacity(0.5),
                        width: 1.5,
                      ),
                    ),
                  ),
                  child: Text(
                    'Manual Reboot',
                    style: QwamosTypography.button.copyWith(
                      color: QwamosColors.neonGreen,
                      fontSize: 12,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    )
        .animate()
        .fadeIn(duration: 300.ms, curve: Curves.easeInOutCubic)
        .slideX(
          begin: -0.1,
          end: 0,
          duration: 300.ms,
          curve: Curves.easeInOutCubic,
        );
  }

  Widget _buildStatusBox(String label, String status, Color statusColor, String ip) {
    final bool isActive = status == 'ONLINE' || status == 'ACTIVE';

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
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: QwamosTypography.h6.copyWith(
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              GlowEffects.statusDot(
                color: statusColor,
                size: 8,
                isAnimated: isActive,
              ),
              const SizedBox(width: 8),
              Text(
                status,
                style: QwamosTypography.labelSmall.copyWith(
                  color: statusColor,
                  fontWeight: FontWeight.w600,
                  fontSize: 11,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            ip,
            style: QwamosTypography.mono.copyWith(
              color: QwamosColors.textSecondary,
              fontSize: 10,
            ),
          ),
        ],
      ),
    );
  }
}
