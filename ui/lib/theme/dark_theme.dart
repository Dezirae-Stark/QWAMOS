import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'colors.dart';

/// QWAMOS Dark Theme Configuration
class QwamosDarkTheme {
  static ThemeData get theme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,

      // Color Scheme
      colorScheme: ColorScheme.dark(
        background: QwamosColors.background,
        surface: QwamosColors.surface,
        surfaceVariant: QwamosColors.surfaceVariant,
        primary: QwamosColors.neonGreen,
        secondary: QwamosColors.cyberViolet,
        tertiary: QwamosColors.aquaBlue,
        error: QwamosColors.redCritical,
        onBackground: QwamosColors.textPrimary,
        onSurface: QwamosColors.textPrimary,
        onPrimary: QwamosColors.background,
        onSecondary: QwamosColors.background,
      ),

      // Scaffold
      scaffoldBackgroundColor: QwamosColors.background,

      // AppBar
      appBarTheme: const AppBarTheme(
        backgroundColor: QwamosColors.surface,
        elevation: 0,
        systemOverlayStyle: SystemUiOverlayStyle(
          statusBarColor: Colors.transparent,
          statusBarIconBrightness: Brightness.light,
        ),
      ),

      // Card
      cardTheme: CardTheme(
        color: QwamosColors.surface,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),

      // Elevated Button
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: QwamosColors.neonGreen,
          foregroundColor: QwamosColors.background,
          elevation: 0,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
      ),

      // Text Button
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: QwamosColors.neonGreen,
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        ),
      ),

      // Icon Theme
      iconTheme: const IconThemeData(
        color: QwamosColors.neonGreen,
        size: 24,
      ),

      // Divider
      dividerTheme: const DividerThemeData(
        color: QwamosColors.surfaceVariant,
        thickness: 1,
        space: 1,
      ),

      // Switch
      switchTheme: SwitchThemeData(
        thumbColor: MaterialStateProperty.resolveWith((states) {
          if (states.contains(MaterialState.selected)) {
            return QwamosColors.neonGreen;
          }
          return QwamosColors.textDim;
        }),
        trackColor: MaterialStateProperty.resolveWith((states) {
          if (states.contains(MaterialState.selected)) {
            return QwamosColors.neonGreenDim;
          }
          return QwamosColors.surfaceVariant;
        }),
      ),

      // Slider
      sliderTheme: SliderThemeData(
        activeTrackColor: QwamosColors.neonGreen,
        inactiveTrackColor: QwamosColors.surfaceVariant,
        thumbColor: QwamosColors.neonGreen,
        overlayColor: QwamosColors.glowNeonGreen,
      ),

      // Progress Indicator
      progressIndicatorTheme: const ProgressIndicatorThemeData(
        color: QwamosColors.neonGreen,
        linearTrackColor: QwamosColors.surfaceVariant,
      ),
    );
  }
}
