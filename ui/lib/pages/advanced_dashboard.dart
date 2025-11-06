import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/colors.dart';
import '../theme/typography.dart';
import '../widgets/chimaera_protocol.dart';
import '../widgets/quantum_decay_chain.dart';
import '../widgets/silent_self_destruct.dart';
import '../widgets/aegis_vault.dart';
import '../widgets/crypto_wallet_hub.dart';
import '../widgets/adaptive_skin_layers.dart';
import '../widgets/quick_actions.dart';
import '../widgets/vm_list.dart';

class AdvancedDashboard extends StatelessWidget {
  const AdvancedDashboard({super.key});

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
              leading: IconButton(
                icon: Icon(
                  Icons.arrow_back,
                  color: QwamosColors.aquaBlue,
                ),
                onPressed: () {
                  Navigator.pop(context);
                },
              ),
              title: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Advanced Controls',
                    style: QwamosTypography.h2.copyWith(
                      color: QwamosColors.textPrimary,
                    ),
                  ),
                  Text(
                    'Security & Crypto Operations',
                    style: QwamosTypography.labelSmall.copyWith(
                      color: QwamosColors.textSecondary,
                    ),
                  ),
                ],
              ),
              actions: [
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
                  // Chimæra Protocol
                  const ChimaeraProtocolWidget(),
                  const SizedBox(height: 24),

                  // Quantum Decay Chain
                  const QuantumDecayChainWidget(),
                  const SizedBox(height: 24),

                  // Silent Self-Destruct
                  const SilentSelfDestructWidget(),
                  const SizedBox(height: 24),

                  // ÆGIS Vault
                  const AegisVaultWidget(),
                  const SizedBox(height: 24),

                  // Crypto Wallet Hub
                  const CryptoWalletHubWidget(),
                  const SizedBox(height: 24),

                  // Adaptive Skin Layers
                  const AdaptiveSkinLayersWidget(),
                  const SizedBox(height: 24),

                  // Quick Actions (Repeated)
                  const QuickActionsWidget(),
                  const SizedBox(height: 24),

                  // VM List (Repeated)
                  const VMListWidget(),
                  const SizedBox(height: 24),

                  // Footer
                  Center(
                    child: Text(
                      'QWAMOS v1.0.0 • Advanced Mode',
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
