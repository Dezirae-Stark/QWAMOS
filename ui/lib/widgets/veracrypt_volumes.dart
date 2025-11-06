import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/colors.dart';
import '../theme/typography.dart';
import '../theme/glow_effects.dart';

class VeraCryptVolumesWidget extends StatefulWidget {
  const VeraCryptVolumesWidget({super.key});

  @override
  State<VeraCryptVolumesWidget> createState() => _VeraCryptVolumesWidgetState();
}

class _VeraCryptVolumesWidgetState extends State<VeraCryptVolumesWidget> {
  bool _isExpanded = true;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Header
        GestureDetector(
          onTap: () {
            setState(() {
              _isExpanded = !_isExpanded;
            });
          },
          child: Row(
            children: [
              Text('VERACRYPT VOLUMES', style: QwamosTypography.h4),
              const Spacer(),
              Icon(
                _isExpanded ? Icons.expand_less : Icons.expand_more,
                color: QwamosColors.cyberViolet,
                size: 24,
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),
        // Encryption Status
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: QwamosColors.surface,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: QwamosColors.cyberViolet.withOpacity(0.3),
              width: 1.5,
            ),
          ),
          child: Row(
            children: [
              Icon(
                Icons.lock,
                color: QwamosColors.cyberViolet,
                size: 20,
              ),
              const SizedBox(width: 12),
              Text(
                'ENCRYPTED: KYBER + CHACHA20',
                style: QwamosTypography.labelSmall.copyWith(
                  color: QwamosColors.cyberViolet,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
        if (_isExpanded) ...[
          const SizedBox(height: 16),
          _buildVolumeCard(
            'vault-vm.01',
            'MOUNTED',
            true,
            85,
            '128 GB',
          ),
          const SizedBox(height: 12),
          _buildVolumeCard(
            'work_data.01',
            'READY',
            false,
            42,
            '256 GB',
          ),
        ],
      ],
    );
  }

  Widget _buildVolumeCard(
    String name,
    String status,
    bool isMounted,
    double usagePercent,
    String capacity,
  ) {
    final Color statusColor = isMounted ? QwamosColors.neonGreen : QwamosColors.textSecondary;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: GlowEffects.neonGlow(
        glowColor: isMounted ? QwamosColors.cyberViolet : QwamosColors.surface,
        borderRadius: 12,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header Row
          Row(
            children: [
              Expanded(
                child: Text(
                  name,
                  style: QwamosTypography.h6,
                ),
              ),
              Row(
                children: [
                  GlowEffects.statusDot(
                    color: statusColor,
                    size: 8,
                    isAnimated: isMounted,
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
          const SizedBox(height: 12),
          // Progress Bar
          Stack(
            children: [
              Container(
                height: 8,
                decoration: BoxDecoration(
                  color: QwamosColors.background,
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
              FractionallySizedBox(
                widthFactor: usagePercent / 100,
                child: Container(
                  height: 8,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        QwamosColors.cyberViolet,
                        QwamosColors.cyberViolet.withOpacity(0.8),
                      ],
                    ),
                    borderRadius: BorderRadius.circular(4),
                    boxShadow: [
                      BoxShadow(
                        color: QwamosColors.cyberViolet.withOpacity(0.5),
                        blurRadius: 8,
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          // Stats Row
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '${usagePercent.toStringAsFixed(0)}% used',
                style: QwamosTypography.labelSmall.copyWith(
                  color: QwamosColors.textSecondary,
                ),
              ),
              Text(
                capacity,
                style: QwamosTypography.labelSmall.copyWith(
                  color: QwamosColors.textSecondary,
                ),
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
}
