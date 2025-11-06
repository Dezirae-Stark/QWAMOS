import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/colors.dart';
import '../theme/typography.dart';

class X86EmulationWidget extends StatelessWidget {
  const X86EmulationWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: QwamosColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: QwamosColors.aquaBlue.withOpacity(0.3),
          width: 1.5,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.computer,
                color: QwamosColors.aquaBlue,
                size: 24,
              ),
              const SizedBox(width: 12),
              Text(
                'x86 EMULATION',
                style: QwamosTypography.h5.copyWith(
                  color: QwamosColors.aquaBlue,
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _buildUsageRing(
                'CPU',
                7.02,
                'Cores',
                QwamosColors.aquaBlue,
              ),
              _buildUsageRing(
                'RAM',
                8.0,
                'GB Used',
                QwamosColors.cyberViolet,
              ),
            ],
          ),
          const SizedBox(height: 20),
          // Emulation Status
          Row(
            children: [
              Expanded(
                child: _buildStatusChip('QEMU', true),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildStatusChip('KVM', false),
              ),
            ],
          ),
        ],
      ),
    )
        .animate()
        .fadeIn(duration: 300.ms, curve: Curves.easeInOutCubic)
        .scale(
          begin: const Offset(0.95, 0.95),
          end: const Offset(1.0, 1.0),
          duration: 300.ms,
          curve: Curves.easeInOutCubic,
        );
  }

  Widget _buildUsageRing(String label, double value, String unit, Color color) {
    // Normalize value to 0-100 range for display
    final double percentage = (value / 16.0 * 100).clamp(0, 100);

    return Column(
      children: [
        // Circular Progress Ring
        SizedBox(
          width: 120,
          height: 120,
          child: Stack(
            alignment: Alignment.center,
            children: [
              // Background Circle
              CustomPaint(
                size: const Size(120, 120),
                painter: _CircularRingPainter(
                  progress: 1.0,
                  color: QwamosColors.background,
                  strokeWidth: 12,
                ),
              ),
              // Progress Circle
              CustomPaint(
                size: const Size(120, 120),
                painter: _CircularRingPainter(
                  progress: percentage / 100,
                  color: color,
                  strokeWidth: 12,
                ),
              )
                  .animate(onPlay: (controller) => controller.repeat())
                  .shimmer(
                    duration: 2000.ms,
                    color: color.withOpacity(0.3),
                  ),
              // Center Text
              Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    value.toStringAsFixed(value < 10 ? 2 : 0),
                    style: QwamosTypography.h3.copyWith(
                      color: color,
                      fontWeight: FontWeight.bold,
                      shadows: [
                        Shadow(
                          color: color.withOpacity(0.5),
                          blurRadius: 8,
                        ),
                      ],
                    ),
                  ),
                  Text(
                    label,
                    style: QwamosTypography.labelSmall.copyWith(
                      color: QwamosColors.textSecondary,
                      fontSize: 10,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 8),
        Text(
          unit,
          style: QwamosTypography.labelSmall.copyWith(
            color: QwamosColors.textSecondary,
          ),
        ),
      ],
    );
  }

  Widget _buildStatusChip(String label, bool isActive) {
    final Color statusColor = isActive
        ? QwamosColors.neonGreen
        : QwamosColors.textSecondary;

    return Container(
      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
      decoration: BoxDecoration(
        color: QwamosColors.background,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(
          color: statusColor.withOpacity(0.3),
          width: 1.5,
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: statusColor,
              shape: BoxShape.circle,
              boxShadow: isActive
                  ? [
                      BoxShadow(
                        color: statusColor.withOpacity(0.5),
                        blurRadius: 8,
                        spreadRadius: 2,
                      ),
                    ]
                  : [],
            ),
          ),
          const SizedBox(width: 8),
          Text(
            label,
            style: QwamosTypography.mono.copyWith(
              color: statusColor,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }
}

// Custom Painter for Circular Progress Ring
class _CircularRingPainter extends CustomPainter {
  final double progress;
  final Color color;
  final double strokeWidth;

  _CircularRingPainter({
    required this.progress,
    required this.color,
    required this.strokeWidth,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = (size.width - strokeWidth) / 2;

    final paint = Paint()
      ..color = color
      ..strokeWidth = strokeWidth
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    // Draw arc
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -pi / 2, // Start at top
      2 * pi * progress, // Progress angle
      false,
      paint,
    );
  }

  @override
  bool shouldRepaint(_CircularRingPainter oldDelegate) {
    return oldDelegate.progress != progress || oldDelegate.color != color;
  }
}
