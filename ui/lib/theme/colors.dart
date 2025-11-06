import 'package:flutter/material.dart';

/// QWAMOS Color Palette - Based on official screenshots
class QwamosColors {
  // Base Theme
  static const Color background = Color(0xFF0B0E16);
  static const Color surface = Color(0xFF151922);
  static const Color surfaceVariant = Color(0xFF1A1F2E);

  // Neon Accents
  static const Color neonGreen = Color(0xFF00FFB3);
  static const Color neonGreenDim = Color(0xFF00B37F);
  static const Color cyberViolet = Color(0xFFB368FF);
  static const Color cyberVioletDim = Color(0xFF8B52CC);
  static const Color aquaBlue = Color(0xFF00E5FF);
  static const Color aquaBlueDim = Color(0xFF00A8CC);

  // Status Colors
  static const Color amberWarning = Color(0xFFFFC400);
  static const Color redCritical = Color(0xFFFF3B30);
  static const Color greenActive = Color(0xFF00FF87);
  static const Color blueInfo = Color(0xFF007AFF);

  // Text Colors
  static const Color textPrimary = Color(0xFFFFFFFF);
  static const Color textSecondary = Color(0xFFB0B8C8);
  static const Color textDim = Color(0xFF7A8299);

  // Glow Effects
  static const Color glowNeonGreen = Color(0x4000FFB3);
  static const Color glowCyberViolet = Color(0x40B368FF);
  static const Color glowAquaBlue = Color(0x4000E5FF);
  static const Color glowAmber = Color(0x40FFC400);
  static const Color glowRed = Color(0x40FF3B30);

  // Gradients
  static const LinearGradient neonGreenGradient = LinearGradient(
    colors: [neonGreen, neonGreenDim],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient cyberVioletGradient = LinearGradient(
    colors: [cyberViolet, cyberVioletDim],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient aquaBlueGradient = LinearGradient(
    colors: [aquaBlue, aquaBlueDim],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const RadialGradient neonGlowGradient = RadialGradient(
    colors: [glowNeonGreen, Colors.transparent],
    radius: 1.5,
  );

  static const RadialGradient violetGlowGradient = RadialGradient(
    colors: [glowCyberViolet, Colors.transparent],
    radius: 1.5,
  );

  static const RadialGradient aquaGlowGradient = RadialGradient(
    colors: [glowAquaBlue, Colors.transparent],
    radius: 1.5,
  );
}
