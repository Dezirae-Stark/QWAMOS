import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/colors.dart';
import '../theme/typography.dart';
import '../theme/glow_effects.dart';

class VMListWidget extends StatelessWidget {
  const VMListWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('VIRTUAL MACHINES', style: QwamosTypography.h4),
        const SizedBox(height: 16),
        _buildVMCard(
          'work-vm',
          'READY',
          QwamosColors.neonGreen,
          'Debian 12 • 4GB RAM',
          Icons.work_outline,
        ),
        const SizedBox(height: 12),
        _buildVMCard(
          'kali-nethunter',
          'RUNNING',
          QwamosColors.neonGreen,
          'Kali Linux • 8GB RAM',
          Icons.security,
        ),
        const SizedBox(height: 12),
        _buildVMCard(
          'vault-vm',
          'READY',
          QwamosColors.cyberViolet,
          'Alpine Linux • 2GB RAM',
          Icons.lock_outline,
        ),
        const SizedBox(height: 12),
        _buildVMCard(
          'disposable-vm',
          'STOPPED',
          QwamosColors.textSecondary,
          'Whonix • 2GB RAM',
          Icons.restore_from_trash,
        ),
      ],
    );
  }

  Widget _buildVMCard(
    String name,
    String status,
    Color statusColor,
    String specs,
    IconData icon,
  ) {
    final bool isRunning = status == 'RUNNING';
    final bool isStopped = status == 'STOPPED';

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: QwamosColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isStopped
              ? QwamosColors.textSecondary.withOpacity(0.2)
              : statusColor.withOpacity(0.3),
          width: 1.5,
        ),
        boxShadow: isStopped
            ? []
            : [
                BoxShadow(
                  color: statusColor.withOpacity(0.2),
                  blurRadius: 12,
                  spreadRadius: 1,
                ),
              ],
      ),
      child: Row(
        children: [
          // VM Icon
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: statusColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: statusColor, size: 24),
          ),
          const SizedBox(width: 16),
          // VM Info
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  name,
                  style: QwamosTypography.h6.copyWith(
                    color: isStopped
                        ? QwamosColors.textSecondary
                        : QwamosColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  specs,
                  style: QwamosTypography.labelSmall.copyWith(
                    color: QwamosColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          // Status Indicator
          Row(
            children: [
              GlowEffects.statusDot(
                color: statusColor,
                size: 8,
                isAnimated: isRunning,
              ),
              const SizedBox(width: 8),
              Text(
                status,
                style: QwamosTypography.labelSmall.copyWith(
                  color: statusColor,
                  fontWeight: FontWeight.w600,
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
}
