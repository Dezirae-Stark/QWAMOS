import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'colors.dart';

/// QWAMOS Typography System
class QwamosTypography {
  // Heading Styles
  static TextStyle h1 = GoogleFonts.inter(
    fontSize: 32,
    fontWeight: FontWeight.bold,
    color: QwamosColors.textPrimary,
    letterSpacing: -0.5,
  );

  static TextStyle h2 = GoogleFonts.inter(
    fontSize: 24,
    fontWeight: FontWeight.bold,
    color: QwamosColors.textPrimary,
    letterSpacing: -0.3,
  );

  static TextStyle h3 = GoogleFonts.inter(
    fontSize: 18,
    fontWeight: FontWeight.w600,
    color: QwamosColors.textPrimary,
  );

  static TextStyle h4 = GoogleFonts.inter(
    fontSize: 16,
    fontWeight: FontWeight.w600,
    color: QwamosColors.textPrimary,
  );

  // Body Styles
  static TextStyle bodyLarge = GoogleFonts.inter(
    fontSize: 16,
    fontWeight: FontWeight.normal,
    color: QwamosColors.textPrimary,
  );

  static TextStyle bodyMedium = GoogleFonts.inter(
    fontSize: 14,
    fontWeight: FontWeight.normal,
    color: QwamosColors.textSecondary,
  );

  static TextStyle bodySmall = GoogleFonts.inter(
    fontSize: 12,
    fontWeight: FontWeight.normal,
    color: QwamosColors.textDim,
  );

  // Monospace Styles (for code/data)
  static TextStyle mono = GoogleFonts.robotoMono(
    fontSize: 14,
    fontWeight: FontWeight.normal,
    color: QwamosColors.neonGreen,
  );

  static TextStyle monoSmall = GoogleFonts.robotoMono(
    fontSize: 12,
    fontWeight: FontWeight.normal,
    color: QwamosColors.textSecondary,
  );

  // Label Styles
  static TextStyle label = GoogleFonts.inter(
    fontSize: 12,
    fontWeight: FontWeight.w500,
    color: QwamosColors.textSecondary,
    letterSpacing: 0.5,
    textBaseline: TextBaseline.alphabetic,
  );

  static TextStyle labelSmall = GoogleFonts.inter(
    fontSize: 10,
    fontWeight: FontWeight.w500,
    color: QwamosColors.textDim,
    letterSpacing: 0.5,
  );

  // Button Styles
  static TextStyle button = GoogleFonts.inter(
    fontSize: 14,
    fontWeight: FontWeight.w600,
    color: QwamosColors.textPrimary,
    letterSpacing: 0.3,
  );

  static TextStyle buttonSmall = GoogleFonts.inter(
    fontSize: 12,
    fontWeight: FontWeight.w600,
    color: QwamosColors.textPrimary,
    letterSpacing: 0.3,
  );

  // Special Effects
  static TextStyle neonGlow = GoogleFonts.inter(
    fontSize: 14,
    fontWeight: FontWeight.w600,
    color: QwamosColors.neonGreen,
    shadows: [
      Shadow(
        color: QwamosColors.glowNeonGreen,
        blurRadius: 8,
      ),
      Shadow(
        color: QwamosColors.glowNeonGreen,
        blurRadius: 16,
      ),
    ],
  );

  static TextStyle violetGlow = GoogleFonts.inter(
    fontSize: 14,
    fontWeight: FontWeight.w600,
    color: QwamosColors.cyberViolet,
    shadows: [
      Shadow(
        color: QwamosColors.glowCyberViolet,
        blurRadius: 8,
      ),
      Shadow(
        color: QwamosColors.glowCyberViolet,
        blurRadius: 16,
      ),
    ],
  );
}
