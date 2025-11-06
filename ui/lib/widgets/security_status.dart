import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/colors.dart';
import '../theme/typography.dart';
import '../theme/glow_effects.dart';

class SecurityStatusWidget extends StatelessWidget {
  const SecurityStatusWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('SECURITY STATUS', style: QwamosTypography.h4),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: _buildStatusCard(
                'ENCRYPTION',
                'ACTIVE',
                QwamosColors.neonGreen,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildStatusCard(
                'KYBER',
                'CONNECTED',
                QwamosColors.neonGreen,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildStatusCard(
                'CHACHA20',
                'ENABLED',
                QwamosColors.neonGreen,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildStatusCard(String title, String status, Color accentColor) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: GlowEffects.neonGlow(
        glowColor: accentColor,
        borderRadius: 8,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              GlowEffects.statusDot(color: accentColor, size: 6),
              const SizedBox(width: 6),
              Flexible(
                child: Text(
                  title,
                  style: QwamosTypography.labelSmall,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            status,
            style: QwamosTypography.neonGlow.copyWith(
              color: accentColor,
              fontSize: 12,
            ),
          ),
        ],
      ),
    )
        .animate()
        .fadeIn(duration: 300.ms, curve: Curves.easeInOutCubic)
        .shimmer(
          duration: 2000.ms,
          color: accentColor.withOpacity(0.3),
        );
  }
}
