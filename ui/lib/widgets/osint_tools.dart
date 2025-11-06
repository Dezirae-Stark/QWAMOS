import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/colors.dart';
import '../theme/typography.dart';

class OsintToolsWidget extends StatefulWidget {
  const OsintToolsWidget({super.key});

  @override
  State<OsintToolsWidget> createState() => _OsintToolsWidgetState();
}

class _OsintToolsWidgetState extends State<OsintToolsWidget> {
  final Map<String, bool> _toolStates = {
    'Haloscope': false,
    'Shodan': true,
    'Torchmeter': false,
    'Rosary': true,
  };

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('OSINT TOOLS', style: QwamosTypography.h4),
        const SizedBox(height: 16),
        GridView.count(
          crossAxisCount: 2,
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          mainAxisSpacing: 12,
          crossAxisSpacing: 12,
          childAspectRatio: 1.3,
          children: [
            _buildToolCard('Haloscope', Icons.radar, _toolStates['Haloscope']!),
            _buildToolCard('Shodan', Icons.search, _toolStates['Shodan']!),
            _buildToolCard('Torchmeter', Icons.speed, _toolStates['Torchmeter']!),
            _buildToolCard('Rosary', Icons.security, _toolStates['Rosary']!),
          ],
        ),
      ],
    );
  }

  Widget _buildToolCard(String name, IconData icon, bool isActive) {
    final Color accentColor = isActive ? QwamosColors.neonGreen : QwamosColors.textSecondary;

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: QwamosColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: accentColor.withOpacity(0.3),
          width: 1.5,
        ),
        boxShadow: isActive
            ? [
                BoxShadow(
                  color: accentColor.withOpacity(0.2),
                  blurRadius: 12,
                ),
              ]
            : [],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Icon(icon, color: accentColor, size: 24),
              Switch(
                value: isActive,
                onChanged: (value) {
                  setState(() {
                    _toolStates[name] = value;
                  });
                },
                activeColor: QwamosColors.neonGreen,
                activeTrackColor: QwamosColors.neonGreen.withOpacity(0.3),
              ),
            ],
          ),
          Text(
            name,
            style: QwamosTypography.h6.copyWith(
              color: isActive ? QwamosColors.textPrimary : QwamosColors.textSecondary,
            ),
          ),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: isActive ? () {} : null,
              style: ElevatedButton.styleFrom(
                backgroundColor: isActive
                    ? QwamosColors.neonGreen.withOpacity(0.2)
                    : QwamosColors.background,
                foregroundColor: accentColor,
                padding: const EdgeInsets.symmetric(vertical: 8),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(6),
                  side: BorderSide(
                    color: accentColor.withOpacity(0.3),
                    width: 1.5,
                  ),
                ),
              ),
              child: Text(
                'DETECT',
                style: QwamosTypography.button.copyWith(
                  color: accentColor,
                  fontSize: 11,
                ),
              ),
            ),
          ),
        ],
      ),
    )
        .animate()
        .fadeIn(duration: 300.ms, curve: Curves.easeInOutCubic)
        .scale(
          begin: const Offset(0.9, 0.9),
          end: const Offset(1.0, 1.0),
          duration: 300.ms,
          curve: Curves.easeInOutCubic,
        );
  }
}
