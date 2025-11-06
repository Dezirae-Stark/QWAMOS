import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/colors.dart';
import '../theme/typography.dart';
import '../widgets/security_status.dart';
import '../widgets/quick_actions.dart';
import '../widgets/vm_list.dart';
import '../widgets/veracrypt_volumes.dart';
import '../widgets/network_gateway.dart';
import '../widgets/encryption_manager.dart';
import '../widgets/airgap_controls.dart';
import '../widgets/osint_tools.dart';
import '../widgets/hal_gpt.dart';
import '../widgets/x86_emulation.dart';
import '../widgets/theme_customization.dart';
import '../widgets/bootloader_integration.dart';

class MainDashboard extends StatelessWidget {
  const MainDashboard({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: QwamosColors.background,
      body: SafeArea(
        child: CustomScrollView(
          slivers: [
            // App Bar
            SliverAppBar(
              floating: true,
              backgroundColor: QwamosColors.background,
              elevation: 0,
              title: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'QubesOS',
                    style: QwamosTypography.h2.copyWith(
                      color: QwamosColors.textPrimary,
                    ),
                  ),
                  Text(
                    'Hypervisor Layer',
                    style: QwamosTypography.labelSmall.copyWith(
                      color: QwamosColors.textSecondary,
                    ),
                  ),
                ],
              ),
              actions: [
                // APK Build Guide Button
                Padding(
                  padding: const EdgeInsets.only(right: 8.0),
                  child: TextButton(
                    onPressed: () {},
                    style: TextButton.styleFrom(
                      backgroundColor: QwamosColors.neonGreen.withOpacity(0.2),
                      foregroundColor: QwamosColors.neonGreen,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 8,
                      ),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                        side: BorderSide(
                          color: QwamosColors.neonGreen.withOpacity(0.5),
                          width: 1.5,
                        ),
                      ),
                    ),
                    child: Text(
                      'APK Build Guide',
                      style: QwamosTypography.button.copyWith(
                        color: QwamosColors.neonGreen,
                        fontSize: 12,
                      ),
                    ),
                  ).animate(onPlay: (controller) => controller.repeat()).shimmer(
                        duration: 2000.ms,
                        color: QwamosColors.neonGreen.withOpacity(0.3),
                      ),
                ),
                // Settings Icon
                IconButton(
                  icon: Icon(
                    Icons.settings,
                    color: QwamosColors.aquaBlue,
                  ),
                  onPressed: () {},
                ),
              ],
            ),
            // Content
            SliverPadding(
              padding: const EdgeInsets.all(16),
              sliver: SliverList(
                delegate: SliverChildListDelegate([
                  // Security Status
                  const SecurityStatusWidget(),
                  const SizedBox(height: 24),

                  // VeraCrypt Volumes
                  const VeraCryptVolumesWidget(),
                  const SizedBox(height: 24),

                  // Encryption Manager
                  const EncryptionManagerWidget(),
                  const SizedBox(height: 24),

                  // Network Gateway
                  const NetworkGatewayWidget(),
                  const SizedBox(height: 24),

                  // Airgap Controls
                  const AirgapControlsWidget(),
                  const SizedBox(height: 24),

                  // OSINT Tools
                  const OsintToolsWidget(),
                  const SizedBox(height: 24),

                  // HAL-GPT
                  const HalGptWidget(),
                  const SizedBox(height: 24),

                  // x86 Emulation
                  const X86EmulationWidget(),
                  const SizedBox(height: 24),

                  // Theme Customization
                  const ThemeCustomizationWidget(),
                  const SizedBox(height: 24),

                  // Bootloader Integration
                  const BootloaderIntegrationWidget(),
                  const SizedBox(height: 24),

                  // Quick Actions
                  const QuickActionsWidget(),
                  const SizedBox(height: 24),

                  // VM List
                  const VMListWidget(),
                  const SizedBox(height: 24),

                  // Footer
                  Center(
                    child: Text(
                      'QWAMOS v1.0.0 • Hypervisor Active',
                      style: QwamosTypography.labelSmall.copyWith(
                        color: QwamosColors.textSecondary,
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                ]),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
