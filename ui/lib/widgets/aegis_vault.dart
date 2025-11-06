import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/colors.dart';
import '../theme/typography.dart';
import '../theme/glow_effects.dart';

class AegisVaultWidget extends StatefulWidget {
  const AegisVaultWidget({super.key});

  @override
  State<AegisVaultWidget> createState() => _AegisVaultWidgetState();
}

class _AegisVaultWidgetState extends State<AegisVaultWidget> {
  bool _isLocked = true;
  final TextEditingController _passwordController = TextEditingController();

  @override
  void dispose() {
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: QwamosColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: _isLocked
              ? QwamosColors.redCritical.withOpacity(0.5)
              : QwamosColors.neonGreen.withOpacity(0.5),
          width: 2,
        ),
        boxShadow: [
          BoxShadow(
            color: _isLocked
                ? QwamosColors.redCritical.withOpacity(0.2)
                : QwamosColors.neonGreen.withOpacity(0.2),
            blurRadius: 12,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          // Status Badge
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: _isLocked
                  ? QwamosColors.redCritical.withOpacity(0.2)
                  : QwamosColors.neonGreen.withOpacity(0.2),
              borderRadius: BorderRadius.circular(6),
              border: Border.all(
                color: _isLocked
                    ? QwamosColors.redCritical.withOpacity(0.5)
                    : QwamosColors.neonGreen.withOpacity(0.5),
                width: 1.5,
              ),
            ),
            child: Text(
              _isLocked ? 'LOCKED' : 'UNLOCKED',
              style: QwamosTypography.mono.copyWith(
                color: _isLocked ? QwamosColors.redCritical : QwamosColors.neonGreen,
                fontWeight: FontWeight.bold,
                fontSize: 13,
              ),
            ),
          ),
          const SizedBox(height: 24),
          // Lock Icon
          Icon(
            _isLocked ? Icons.lock : Icons.lock_open,
            size: 80,
            color: _isLocked ? QwamosColors.redCritical : QwamosColors.neonGreen,
          )
              .animate()
              .fadeIn(duration: 300.ms)
              .scale(
                begin: const Offset(0.8, 0.8),
                end: const Offset(1.0, 1.0),
                duration: 300.ms,
                curve: Curves.easeInOutCubic,
              ),
          const SizedBox(height: 24),
          // Title
          Text(
            '\u00c6GIS VAULT',
            style: QwamosTypography.h3.copyWith(
              color: QwamosColors.textPrimary,
              letterSpacing: 2,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Airgap Vault VM',
            style: QwamosTypography.labelSmall.copyWith(
              color: QwamosColors.textSecondary,
            ),
          ),
          const SizedBox(height: 24),
          if (_isLocked) ...[
            // Password Input
            TextField(
              controller: _passwordController,
              obscureText: true,
              style: QwamosTypography.mono.copyWith(
                color: QwamosColors.textPrimary,
              ),
              decoration: InputDecoration(
                hintText: 'Enter vault password',
                hintStyle: QwamosTypography.mono.copyWith(
                  color: QwamosColors.textSecondary,
                ),
                filled: true,
                fillColor: QwamosColors.background,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide: BorderSide(
                    color: QwamosColors.redCritical.withOpacity(0.3),
                    width: 1.5,
                  ),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide: BorderSide(
                    color: QwamosColors.redCritical.withOpacity(0.3),
                    width: 1.5,
                  ),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide: BorderSide(
                    color: QwamosColors.redCritical,
                    width: 2,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 16),
            // Unlock Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  setState(() {
                    _isLocked = false;
                  });
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: QwamosColors.neonGreen.withOpacity(0.2),
                  foregroundColor: QwamosColors.neonGreen,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                    side: BorderSide(
                      color: QwamosColors.neonGreen.withOpacity(0.5),
                      width: 1.5,
                    ),
                  ),
                ),
                child: Text(
                  'UNLOCK',
                  style: QwamosTypography.button.copyWith(
                    color: QwamosColors.neonGreen,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ] else ...[
            // Lock Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  setState(() {
                    _isLocked = true;
                    _passwordController.clear();
                  });
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: QwamosColors.redCritical.withOpacity(0.2),
                  foregroundColor: QwamosColors.redCritical,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                    side: BorderSide(
                      color: QwamosColors.redCritical.withOpacity(0.5),
                      width: 1.5,
                    ),
                  ),
                ),
                child: Text(
                  'LOCK',
                  style: QwamosTypography.button.copyWith(
                    color: QwamosColors.redCritical,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ],
          const SizedBox(height: 20),
          // Network Status
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: QwamosColors.background,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              children: [
                _buildStatusRow(Icons.wifi_off, 'No network access'),
                const SizedBox(height: 8),
                _buildStatusRow(Icons.security, 'Firewall active'),
                const SizedBox(height: 8),
                _buildStatusRow(Icons.block, 'Isolated'),
              ],
            ),
          ),
        ],
      ),
    )
        .animate()
        .fadeIn(duration: 300.ms, curve: Curves.easeInOutCubic)
        .slideY(
          begin: 0.1,
          end: 0,
          duration: 300.ms,
          curve: Curves.easeInOutCubic,
        );
  }

  Widget _buildStatusRow(IconData icon, String text) {
    return Row(
      children: [
        Icon(
          icon,
          size: 16,
          color: QwamosColors.textSecondary,
        ),
        const SizedBox(width: 8),
        Text(
          text,
          style: QwamosTypography.labelSmall.copyWith(
            color: QwamosColors.textSecondary,
            fontSize: 11,
          ),
        ),
      ],
    );
  }
}
