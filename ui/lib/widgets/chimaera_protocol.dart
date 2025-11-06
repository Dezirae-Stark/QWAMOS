import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/colors.dart';
import '../theme/typography.dart';
import '../theme/glow_effects.dart';

class ChimaeraProtocolWidget extends StatefulWidget {
  const ChimaeraProtocolWidget({super.key});

  @override
  State<ChimaeraProtocolWidget> createState() => _ChimaeraProtocolWidgetState();
}

class _ChimaeraProtocolWidgetState extends State<ChimaeraProtocolWidget> {
  double _decayWork = 0.65;
  double _decayPersonal = 0.42;
  double _decayBurner = 0.88;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: QwamosColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: QwamosColors.cyberViolet.withOpacity(0.5),
          width: 2,
        ),
        boxShadow: [
          BoxShadow(
            color: QwamosColors.cyberViolet.withOpacity(0.2),
            blurRadius: 12,
            spreadRadius: 1,
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
                Icons.auto_graph,
                color: QwamosColors.cyberViolet,
                size: 28,
              ),
              const SizedBox(width: 12),
              Text(
                'CHIMÆRA PROTOCOL',
                style: QwamosTypography.h4.copyWith(
                  color: QwamosColors.cyberViolet,
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: QwamosColors.cyberViolet.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(
                    color: QwamosColors.cyberViolet.withOpacity(0.5),
                    width: 1.5,
                  ),
                ),
                child: Text(
                  '1 Ready',
                  style: QwamosTypography.mono.copyWith(
                    color: QwamosColors.cyberViolet,
                    fontSize: 12,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          // Decay Sliders
          _buildDecaySlider('decay-work', _decayWork, (value) {
            setState(() => _decayWork = value);
          }),
          const SizedBox(height: 16),
          _buildDecaySlider('decay-personal', _decayPersonal, (value) {
            setState(() => _decayPersonal = value);
          }),
          const SizedBox(height: 16),
          _buildDecaySlider('decay-burner', _decayBurner, (value) {
            setState(() => _decayBurner = value);
          }),
          const SizedBox(height: 20),
          // Timestamp
          Row(
            children: [
              Icon(
                Icons.access_time,
                color: QwamosColors.textSecondary,
                size: 16,
              ),
              const SizedBox(width: 8),
              Text(
                'Last: 2w 2m',
                style: QwamosTypography.labelSmall.copyWith(
                  color: QwamosColors.textSecondary,
                ),
              ),
              const Spacer(),
              TextButton(
                onPressed: () {},
                style: TextButton.styleFrom(
                  foregroundColor: QwamosColors.cyberViolet,
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                ),
                child: Text(
                  'Config',
                  style: QwamosTypography.button.copyWith(
                    color: QwamosColors.cyberViolet,
                    fontSize: 12,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          // Action Buttons
          Row(
            children: [
              Expanded(
                child: ElevatedButton(
                  onPressed: () {},
                  style: ElevatedButton.styleFrom(
                    backgroundColor: QwamosColors.cyberViolet.withOpacity(0.2),
                    foregroundColor: QwamosColors.cyberViolet,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                      side: BorderSide(
                        color: QwamosColors.cyberViolet.withOpacity(0.5),
                        width: 1.5,
                      ),
                    ),
                  ),
                  child: Text(
                    'Deploy Mark',
                    style: QwamosTypography.button.copyWith(
                      color: QwamosColors.cyberViolet,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: OutlinedButton(
                  onPressed: () {},
                  style: OutlinedButton.styleFrom(
                    foregroundColor: QwamosColors.redCritical,
                    side: BorderSide(
                      color: QwamosColors.redCritical.withOpacity(0.5),
                      width: 1.5,
                    ),
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: Text(
                    'Destroy Personal',
                    style: QwamosTypography.button.copyWith(
                      color: QwamosColors.redCritical,
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
        .slideY(
          begin: 0.1,
          end: 0,
          duration: 300.ms,
          curve: Curves.easeInOutCubic,
        );
  }

  Widget _buildDecaySlider(String label, double value, ValueChanged<double> onChanged) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: QwamosTypography.mono.copyWith(
                color: QwamosColors.textPrimary,
                fontSize: 13,
              ),
            ),
            Text(
              '${(value * 100).toStringAsFixed(0)}%',
              style: QwamosTypography.mono.copyWith(
                color: QwamosColors.cyberViolet,
                fontSize: 13,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        SliderTheme(
          data: SliderThemeData(
            activeTrackColor: QwamosColors.cyberViolet,
            inactiveTrackColor: QwamosColors.background,
            thumbColor: QwamosColors.cyberViolet,
            overlayColor: QwamosColors.cyberViolet.withOpacity(0.2),
            trackHeight: 6,
            thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 8),
          ),
          child: Slider(
            value: value,
            onChanged: onChanged,
            min: 0,
            max: 1,
          ),
        ),
      ],
    );
  }
}
