import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/colors.dart';
import '../theme/typography.dart';
import '../theme/glow_effects.dart';

class SilentSelfDestructWidget extends StatefulWidget {
  const SilentSelfDestructWidget({super.key});

  @override
  State<SilentSelfDestructWidget> createState() => _SilentSelfDestructWidgetState();
}

class _SilentSelfDestructWidgetState extends State<SilentSelfDestructWidget> {
  final Map<String, bool> _triggers = {
    'USB insertion': true,
    'Wrong password (3x)': true,
    'Remote command': false,
    'Tamper detection': true,
  };

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
            color: QwamosColors.redCritical.withOpacity(0.3),
            blurRadius: 16,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              Icon(
                Icons.warning_amber_rounded,
                color: QwamosColors.redCritical,
                size: 28,
              ),
              const SizedBox(width: 12),
              Text(
                'SILENT SELF-DESTRUCT',
                style: QwamosTypography.h4.copyWith(
                  color: QwamosColors.redCritical,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          // Status and Countdown
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: QwamosColors.redCritical.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: QwamosColors.redCritical.withOpacity(0.3),
                width: 1.5,
              ),
            ),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'SYSTEM STATUS',
                      style: QwamosTypography.labelSmall,
                    ),
                    Row(
                      children: [
                        GlowEffects.statusDot(
                          color: QwamosColors.redCritical,
                          size: 10,
                          isAnimated: true,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'ARMED',
                          style: QwamosTypography.mono.copyWith(
                            color: QwamosColors.redCritical,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Text(
                  '03h 12m',
                  style: QwamosTypography.h1.copyWith(
                    color: QwamosColors.redCritical,
                    fontSize: 42,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 4,
                    shadows: [
                      Shadow(
                        color: QwamosColors.redCritical.withOpacity(0.5),
                        blurRadius: 12,
                      ),
                    ],
                  ),
                )
                    .animate(onPlay: (controller) => controller.repeat())
                    .shimmer(
                      duration: 1500.ms,
                      color: QwamosColors.redCritical.withOpacity(0.5),
                    ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          // Trigger List
          Text(
            'TRIGGERS',
            style: QwamosTypography.labelSmall,
          ),
          const SizedBox(height: 12),
          ..._triggers.entries.map((entry) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  children: [
                    Checkbox(
                      value: entry.value,
                      onChanged: (value) {
                        setState(() {
                          _triggers[entry.key] = value ?? false;
                        });
                      },
                      activeColor: QwamosColors.redCritical,
                      side: BorderSide(
                        color: QwamosColors.redCritical.withOpacity(0.5),
                        width: 1.5,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      entry.key,
                      style: QwamosTypography.body.copyWith(
                        color: entry.value
                            ? QwamosColors.textPrimary
                            : QwamosColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              )),
          const SizedBox(height: 16),
          // Action Buttons
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: () {},
                  style: OutlinedButton.styleFrom(
                    foregroundColor: QwamosColors.redCritical,
                    side: BorderSide(
                      color: QwamosColors.redCritical.withOpacity(0.5),
                      width: 1.5,
                    ),
                    padding: const EdgeInsets.symmetric(vertical: 10),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: Text(
                    'Configure',
                    style: QwamosTypography.button.copyWith(
                      color: QwamosColors.redCritical,
                      fontSize: 12,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: OutlinedButton(
                  onPressed: () {},
                  style: OutlinedButton.styleFrom(
                    foregroundColor: QwamosColors.amberWarning,
                    side: BorderSide(
                      color: QwamosColors.amberWarning.withOpacity(0.5),
                      width: 1.5,
                    ),
                    padding: const EdgeInsets.symmetric(vertical: 10),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: Text(
                    'Test',
                    style: QwamosTypography.button.copyWith(
                      color: QwamosColors.amberWarning,
                      fontSize: 12,
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          // Stop Button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () {},
              style: ElevatedButton.styleFrom(
                backgroundColor: QwamosColors.redCritical,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.warning, size: 20),
                  const SizedBox(width: 8),
                  Text(
                    'STOP',
                    style: QwamosTypography.button.copyWith(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    )
        .animate()
        .fadeIn(duration: 300.ms, curve: Curves.easeInOutCubic)
        .shake(duration: 600.ms, hz: 2, curve: Curves.easeInOutCubic);
  }
}
