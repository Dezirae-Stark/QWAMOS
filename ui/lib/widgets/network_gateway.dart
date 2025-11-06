import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/colors.dart';
import '../theme/typography.dart';
import '../theme/glow_effects.dart';

class NetworkGatewayWidget extends StatelessWidget {
  const NetworkGatewayWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('NETWORK GATEWAY', style: QwamosTypography.h4),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: _buildGatewayCard(
                'TOR',
                'ONLINE',
                QwamosColors.neonGreen,
                Icons.vpn_lock,
                '3 circuits',
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildGatewayCard(
                'I2P',
                'ACTIVE',
                QwamosColors.aquaBlue,
                Icons.wifi_protected_setup,
                '12 peers',
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _buildGatewayCard(
                'DNS',
                'SECURED',
                QwamosColors.cyberViolet,
                Icons.dns,
                'DNSCrypt',
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildGatewayCard(
                'VPN',
                'OFFLINE',
                QwamosColors.textSecondary,
                Icons.vpn_key_off,
                'Disconnected',
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildGatewayCard(
    String title,
    String status,
    Color statusColor,
    IconData icon,
    String info,
  ) {
    final bool isActive = status == 'ONLINE' || status == 'ACTIVE' || status == 'SECURED';

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: QwamosColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: statusColor.withOpacity(0.3),
          width: 1.5,
        ),
        boxShadow: isActive
            ? [
                BoxShadow(
                  color: statusColor.withOpacity(0.2),
                  blurRadius: 12,
                  spreadRadius: 1,
                ),
              ]
            : [],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Icon and Title
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: statusColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(icon, color: statusColor, size: 20),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  title,
                  style: QwamosTypography.h6,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          // Status Row
          Row(
            children: [
              GlowEffects.statusDot(
                color: statusColor,
                size: 8,
                isAnimated: isActive,
              ),
              const SizedBox(width: 8),
              Text(
                status,
                style: QwamosTypography.labelSmall.copyWith(
                  color: statusColor,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          // Info
          Text(
            info,
            style: QwamosTypography.labelSmall.copyWith(
              color: QwamosColors.textSecondary,
            ),
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
}
