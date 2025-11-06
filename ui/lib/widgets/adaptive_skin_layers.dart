import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/colors.dart';
import '../theme/typography.dart';

class AdaptiveSkinLayersWidget extends StatefulWidget {
  const AdaptiveSkinLayersWidget({super.key});

  @override
  State<AdaptiveSkinLayersWidget> createState() => _AdaptiveSkinLayersWidgetState();
}

class _AdaptiveSkinLayersWidgetState extends State<AdaptiveSkinLayersWidget> {
  String _selectedTheme = 'Nova Future';

  final List<Map<String, dynamic>> _themes = [
    {
      'name': 'Quantum Dawn',
      'colors': [Color(0xFF00FFB3), Color(0xFF00E5FF)],
    },
    {
      'name': 'Nova Future',
      'colors': [Color(0xFFB368FF), Color(0xFFFF3B30)],
    },
    {
      'name': 'Shizen Sunset',
      'colors': [Color(0xFFFFC400), Color(0xFFFF3B30)],
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: QwamosColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: QwamosColors.cyberViolet.withOpacity(0.3),
          width: 1.5,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.layers,
                color: QwamosColors.cyberViolet,
                size: 24,
              ),
              const SizedBox(width: 12),
              Text(
                'ADAPTIVE SKIN LAYERS',
                style: QwamosTypography.h5.copyWith(
                  color: QwamosColors.cyberViolet,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          // Theme Cards
          ..._themes.map((theme) => Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: _buildThemeCard(
                  theme['name'] as String,
                  theme['colors'] as List<Color>,
                ),
              )),
        ],
      ),
    )
        .animate()
        .fadeIn(duration: 300.ms, curve: Curves.easeInOutCubic)
        .slideX(
          begin: 0.1,
          end: 0,
          duration: 300.ms,
          curve: Curves.easeInOutCubic,
        );
  }

  Widget _buildThemeCard(String name, List<Color> colors) {
    final bool isSelected = name == _selectedTheme;

    return GestureDetector(
      onTap: () {
        setState(() {
          _selectedTheme = name;
        });
      },
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: QwamosColors.background,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: isSelected
                ? QwamosColors.cyberViolet
                : QwamosColors.cyberViolet.withOpacity(0.2),
            width: isSelected ? 2 : 1.5,
          ),
          boxShadow: isSelected
              ? [
                  BoxShadow(
                    color: QwamosColors.cyberViolet.withOpacity(0.3),
                    blurRadius: 12,
                  ),
                ]
              : [],
        ),
        child: Row(
          children: [
            // Theme Preview
            Container(
              width: 60,
              height: 60,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: colors,
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(6),
                boxShadow: [
                  BoxShadow(
                    color: colors[0].withOpacity(0.3),
                    blurRadius: 8,
                  ),
                ],
              ),
            ),
            const SizedBox(width: 16),
            // Theme Name
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    name,
                    style: QwamosTypography.h6.copyWith(
                      color: isSelected
                          ? QwamosColors.cyberViolet
                          : QwamosColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${colors.length} colors',
                    style: QwamosTypography.labelSmall.copyWith(
                      color: QwamosColors.textSecondary,
                      fontSize: 11,
                    ),
                  ),
                ],
              ),
            ),
            // Selection Indicator
            if (isSelected)
              Icon(
                Icons.check_circle,
                color: QwamosColors.cyberViolet,
                size: 24,
              ),
          ],
        ),
      )
          .animate()
          .fadeIn(duration: 200.ms)
          .scale(
            begin: const Offset(0.95, 0.95),
            end: const Offset(1.0, 1.0),
            duration: 200.ms,
          ),
    );
  }
}
