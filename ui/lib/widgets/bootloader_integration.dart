import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/colors.dart';
import '../theme/typography.dart';
import '../theme/glow_effects.dart';

class BootloaderIntegrationWidget extends StatelessWidget {
  const BootloaderIntegrationWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: QwamosColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: QwamosColors.redCritical.withOpacity(0.5),
          width: 2,
        ),
        boxShadow: [
          BoxShadow(
            color: QwamosColors.redCritical.withOpacity(0.2),
            blurRadius: 12,
            spreadRadius: 1,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with Warning
          Row(
            children: [
              Icon(
                Icons.warning_amber_rounded,
                color: QwamosColors.redCritical,
                size: 28,
              ),
              const SizedBox(width: 12),
              Text(
                'BOOTLOADER INTEGRATION',
                style: QwamosTypography.h5.copyWith(
                  color: QwamosColors.redCritical,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          // Status Card
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: QwamosColors.redCritical.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: QwamosColors.redCritical.withOpacity(0.3),
                width: 1.5,
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    GlowEffects.statusDot(
                      color: QwamosColors.redCritical,
                      size: 10,
                      isAnimated: true,
                    ),
                    const SizedBox(width: 10),
                    Text(
                      'STATUS: BROKEN',
                      style: QwamosTypography.h6.copyWith(
                        color: QwamosColors.redCritical,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text(
                  'Bootloader Access: LOCKED',
                  style: QwamosTypography.body.copyWith(
                    color: QwamosColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  'Secure Boot: ENABLED',
                  style: QwamosTypography.body.copyWith(
                    color: QwamosColors.textSecondary,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  'Verified Boot: ENFORCING',
                  style: QwamosTypography.body.copyWith(
                    color: QwamosColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          // Warning Message
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: QwamosColors.background,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: QwamosColors.amberWarning.withOpacity(0.3),
                width: 1.5,
              ),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.info_outline,
                  color: QwamosColors.amberWarning,
                  size: 20,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Root access required to unlock bootloader',
                    style: QwamosTypography.labelSmall.copyWith(
                      color: QwamosColors.amberWarning,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
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
                    'DIAGNOSE',
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
                    backgroundColor: QwamosColors.redCritical.withOpacity(0.2),
                    foregroundColor: QwamosColors.redCritical,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                      side: BorderSide(
                        color: QwamosColors.redCritical.withOpacity(0.5),
                        width: 1.5,
                      ),
                    ),
                  ),
                  child: Text(
                    'UNLOCK',
                    style: QwamosTypography.button.copyWith(
                      color: QwamosColors.redCritical,
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
        .shake(duration: 500.ms, hz: 2, curve: Curves.easeInOutCubic);
  }
}
