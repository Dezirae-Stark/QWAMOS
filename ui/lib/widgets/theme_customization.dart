import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/colors.dart';
import '../theme/typography.dart';

class ThemeCustomizationWidget extends StatefulWidget {
  const ThemeCustomizationWidget({super.key});

  @override
  State<ThemeCustomizationWidget> createState() => _ThemeCustomizationWidgetState();
}

class _ThemeCustomizationWidgetState extends State<ThemeCustomizationWidget> {
  bool _darkMode = true;
  String _selectedTheme = 'System Default';
  String _selectedFont = 'Inter';

  final List<String> _themes = [
    'System Default',
    'Rebirth',
    'Nova',
    'Courier New',
  ];

  final List<String> _fonts = [
    'Inter',
    'Roboto Mono',
    'Courier New',
    'JetBrains Mono',
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
                Icons.palette,
                color: QwamosColors.cyberViolet,
                size: 24,
              ),
              const SizedBox(width: 12),
              Text(
                'THEME CUSTOMIZATION',
                style: QwamosTypography.h5.copyWith(
                  color: QwamosColors.cyberViolet,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          // Dark Mode Toggle
          Row(
            children: [
              Expanded(
                child: Text(
                  'DARK MODE',
                  style: QwamosTypography.body,
                ),
              ),
              Switch(
                value: _darkMode,
                onChanged: (value) {
                  setState(() {
                    _darkMode = value;
                  });
                },
                activeColor: QwamosColors.cyberViolet,
                activeTrackColor: QwamosColors.cyberViolet.withOpacity(0.3),
              ),
            ],
          ),
          const Divider(height: 24, color: Color(0xFF1A1F2E)),
          // Theme Selector
          Text(
            'THEME',
            style: QwamosTypography.labelSmall,
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _themes.map((theme) {
              final bool isSelected = theme == _selectedTheme;
              return GestureDetector(
                onTap: () {
                  setState(() {
                    _selectedTheme = theme;
                  });
                },
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 10,
                  ),
                  decoration: BoxDecoration(
                    color: isSelected
                        ? QwamosColors.cyberViolet.withOpacity(0.2)
                        : QwamosColors.background,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                      color: isSelected
                          ? QwamosColors.cyberViolet
                          : QwamosColors.cyberViolet.withOpacity(0.3),
                      width: 1.5,
                    ),
                    boxShadow: isSelected
                        ? [
                            BoxShadow(
                              color: QwamosColors.cyberViolet.withOpacity(0.3),
                              blurRadius: 8,
                            ),
                          ]
                        : [],
                  ),
                  child: Text(
                    theme,
                    style: QwamosTypography.button.copyWith(
                      color: isSelected
                          ? QwamosColors.cyberViolet
                          : QwamosColors.textSecondary,
                      fontSize: 12,
                    ),
                  ),
                ),
              )
                  .animate()
                  .fadeIn(duration: 200.ms)
                  .scale(
                    begin: const Offset(0.95, 0.95),
                    end: const Offset(1.0, 1.0),
                    duration: 200.ms,
                  );
            }).toList(),
          ),
          const SizedBox(height: 16),
          const Divider(height: 24, color: Color(0xFF1A1F2E)),
          // Font Selector
          Text(
            'FONT FAMILY',
            style: QwamosTypography.labelSmall,
          ),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            decoration: BoxDecoration(
              color: QwamosColors.background,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: QwamosColors.cyberViolet.withOpacity(0.3),
                width: 1.5,
              ),
            ),
            child: DropdownButton<String>(
              value: _selectedFont,
              isExpanded: true,
              underline: const SizedBox(),
              dropdownColor: QwamosColors.surface,
              style: QwamosTypography.body.copyWith(
                color: QwamosColors.textPrimary,
              ),
              items: _fonts.map((String font) {
                return DropdownMenuItem<String>(
                  value: font,
                  child: Text(font),
                );
              }).toList(),
              onChanged: (String? newValue) {
                if (newValue != null) {
                  setState(() {
                    _selectedFont = newValue;
                  });
                }
              },
            ),
          ),
          const SizedBox(height: 16),
          // Apply Button
          SizedBox(
            width: double.infinity,
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
                'APPLY THEME',
                style: QwamosTypography.button.copyWith(
                  color: QwamosColors.cyberViolet,
                ),
              ),
            ),
          ),
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
}
