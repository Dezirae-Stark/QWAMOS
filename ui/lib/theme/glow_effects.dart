import 'package:flutter/material.dart';
import 'colors.dart';

/// Glow Effect Utilities for QWAMOS UI
class GlowEffects {
  /// Creates a neon glow box decoration
  static BoxDecoration neonGlow({
    required Color glowColor,
    Color? backgroundColor,
    double borderRadius = 12,
    double glowRadius = 20,
    double glowSpread = 0,
  }) {
    return BoxDecoration(
      color: backgroundColor ?? QwamosColors.surface,
      borderRadius: BorderRadius.circular(borderRadius),
      boxShadow: [
        BoxShadow(
          color: glowColor.withOpacity(0.3),
          blurRadius: glowRadius,
          spreadRadius: glowSpread,
        ),
        BoxShadow(
          color: glowColor.withOpacity(0.2),
          blurRadius: glowRadius * 1.5,
          spreadRadius: glowSpread,
        ),
        BoxShadow(
          color: glowColor.withOpacity(0.1),
          blurRadius: glowRadius * 2,
          spreadRadius: glowSpread,
        ),
      ],
    );
  }

  /// Creates a pulsing glow animation
  static Widget pulsingGlow({
    required Widget child,
    required Color glowColor,
    double minOpacity = 0.2,
    double maxOpacity = 0.6,
    Duration duration = const Duration(seconds: 2),
  }) {
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: minOpacity, end: maxOpacity),
      duration: duration,
      curve: Curves.easeInOut,
      builder: (context, value, _) {
        return Container(
          decoration: BoxDecoration(
            boxShadow: [
              BoxShadow(
                color: glowColor.withOpacity(value),
                blurRadius: 20,
                spreadRadius: 2,
              ),
            ],
          ),
          child: child,
        );
      },
      onEnd: () {
        // Reverse animation (handled by AnimatedBuilder loop in practice)
      },
    );
  }

  /// Creates a ripple effect
  static BoxDecoration rippleGlow({
    required Color color,
    double borderRadius = 12,
  }) {
    return BoxDecoration(
      border: Border.all(
        color: color.withOpacity(0.5),
        width: 2,
      ),
      borderRadius: BorderRadius.circular(borderRadius),
      boxShadow: [
        BoxShadow(
          color: color.withOpacity(0.3),
          blurRadius: 12,
          spreadRadius: 2,
        ),
      ],
    );
  }

  /// Creates an inner glow effect
  static BoxDecoration innerGlow({
    required Color glowColor,
    Color? backgroundColor,
    double borderRadius = 12,
  }) {
    return BoxDecoration(
      color: backgroundColor ?? QwamosColors.surface,
      borderRadius: BorderRadius.circular(borderRadius),
      border: Border.all(
        color: glowColor.withOpacity(0.3),
        width: 1,
      ),
      boxShadow: [
        BoxShadow(
          color: glowColor.withOpacity(0.15),
          blurRadius: 8,
          spreadRadius: -2,
        ),
      ],
    );
  }

  /// Creates a shimmer effect gradient
  static LinearGradient shimmerGradient({
    required Color baseColor,
    double animationValue = 0.0,
  }) {
    return LinearGradient(
      begin: Alignment(-1.0 + animationValue * 2, -1.0),
      end: Alignment(1.0 + animationValue * 2, 1.0),
      colors: [
        baseColor.withOpacity(0.1),
        baseColor.withOpacity(0.3),
        baseColor.withOpacity(0.1),
      ],
      stops: const [0.0, 0.5, 1.0],
    );
  }

  /// Creates a progress bar with glowing effect
  static Widget glowingProgressBar({
    required double progress,
    required Color glowColor,
    double height = 8,
    double borderRadius = 4,
  }) {
    return Container(
      height: height,
      decoration: BoxDecoration(
        color: QwamosColors.surfaceVariant,
        borderRadius: BorderRadius.circular(borderRadius),
      ),
      child: Stack(
        children: [
          // Background track
          Container(
            decoration: BoxDecoration(
              color: QwamosColors.surfaceVariant,
              borderRadius: BorderRadius.circular(borderRadius),
            ),
          ),
          // Progress fill with glow
          FractionallySizedBox(
            widthFactor: progress.clamp(0.0, 1.0),
            child: Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    glowColor,
                    glowColor.withOpacity(0.8),
                  ],
                ),
                borderRadius: BorderRadius.circular(borderRadius),
                boxShadow: [
                  BoxShadow(
                    color: glowColor.withOpacity(0.5),
                    blurRadius: 8,
                    spreadRadius: 1,
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// Creates a status dot with pulsing glow
  static Widget statusDot({
    required Color color,
    double size = 8,
    bool pulsing = true,
    bool isAnimated = true, // Alias for pulsing
  }) {
    // Use pulsing or isAnimated (whichever is provided)
    final bool shouldPulse = pulsing && isAnimated;
    Widget dot = Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: color,
        shape: BoxShape.circle,
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.6),
            blurRadius: size,
            spreadRadius: size / 2,
          ),
        ],
      ),
    );

    if (!shouldPulse) return dot;

    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0.6, end: 1.0),
      duration: const Duration(milliseconds: 1000),
      curve: Curves.easeInOut,
      builder: (context, value, child) {
        return Transform.scale(
          scale: value,
          child: Opacity(
            opacity: value,
            child: child,
          ),
        );
      },
      child: dot,
    );
  }
}
