import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/colors.dart';
import '../theme/typography.dart';

class CryptoWalletHubWidget extends StatelessWidget {
  const CryptoWalletHubWidget({super.key});

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
          // Header with Atomic Swap indicator
          Row(
            children: [
              Icon(
                Icons.account_balance_wallet,
                color: QwamosColors.cyberViolet,
                size: 24,
              ),
              const SizedBox(width: 12),
              Text(
                'CRYPTO WALLET HUB',
                style: QwamosTypography.h5.copyWith(
                  color: QwamosColors.cyberViolet,
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: QwamosColors.cyberViolet.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(
                    color: QwamosColors.cyberViolet.withOpacity(0.5),
                    width: 1.5,
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.swap_horiz,
                      size: 14,
                      color: QwamosColors.cyberViolet,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      'Atomic Swap',
                      style: QwamosTypography.mono.copyWith(
                        color: QwamosColors.cyberViolet,
                        fontSize: 10,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          // Samourai Wallet Card
          _buildWalletCard(
            'Samourai Wallet',
            '+12w 24h',
            QwamosColors.neonGreen,
            [
              'Unspent',
              'Payments',
            ],
          ),
          const SizedBox(height: 12),
          // Colde Wallet Card
          _buildWalletCard(
            'Colde Wallet',
            'Paused Utx',
            QwamosColors.amberWarning,
            [
              'Bounces',
              'Reconstruct',
            ],
          ),
          const SizedBox(height: 16),
          // Config Button
          SizedBox(
            width: double.infinity,
            child: OutlinedButton(
              onPressed: () {},
              style: OutlinedButton.styleFrom(
                foregroundColor: QwamosColors.cyberViolet,
                side: BorderSide(
                  color: QwamosColors.cyberViolet.withOpacity(0.5),
                  width: 1.5,
                ),
                padding: const EdgeInsets.symmetric(vertical: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: Text(
                'CONFIG',
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
        .scale(
          begin: const Offset(0.95, 0.95),
          end: const Offset(1.0, 1.0),
          duration: 300.ms,
          curve: Curves.easeInOutCubic,
        );
  }

  Widget _buildWalletCard(String name, String status, Color statusColor, List<String> features) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: QwamosColors.background,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: statusColor.withOpacity(0.3),
          width: 1.5,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                name,
                style: QwamosTypography.h6,
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: statusColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  status,
                  style: QwamosTypography.mono.copyWith(
                    color: statusColor,
                    fontSize: 11,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: features.map((feature) {
              return Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: QwamosColors.surface,
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(
                    color: QwamosColors.textSecondary.withOpacity(0.2),
                    width: 1,
                  ),
                ),
                child: Text(
                  feature,
                  style: QwamosTypography.labelSmall.copyWith(
                    fontSize: 11,
                  ),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }
}
