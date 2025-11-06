import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/colors.dart';
import '../theme/typography.dart';
import '../theme/glow_effects.dart';

class AIAssistantsPanelWidget extends StatefulWidget {
  const AIAssistantsPanelWidget({super.key});

  @override
  State<AIAssistantsPanelWidget> createState() => _AIAssistantsPanelWidgetState();
}

class _AIAssistantsPanelWidgetState extends State<AIAssistantsPanelWidget> {
  final Map<String, bool> _assistantStatus = {
    'kali-gpt': true,
    'claude': true,
    'chatgpt': false,
  };

  final Map<String, Map<String, dynamic>> _assistantInfo = {
    'kali-gpt': {
      'name': 'Kali GPT',
      'model': 'Llama 3.1 8B',
      'privacy': 'LOCAL',
      'color': QwamosColors.neonGreen,
      'icon': Icons.shield,
      'usage': '100% Private',
      'cost': '\$0.00',
    },
    'claude': {
      'name': 'Claude',
      'model': 'Sonnet 3.5',
      'privacy': 'VIA TOR',
      'color': QwamosColors.cyberViolet,
      'icon': Icons.psychology,
      'usage': '1.2K tokens',
      'cost': '\$0.18',
    },
    'chatgpt': {
      'name': 'ChatGPT',
      'model': 'GPT-4 Turbo',
      'privacy': 'VIA TOR',
      'color': QwamosColors.aquaBlue,
      'icon': Icons.chat,
      'usage': '0 tokens',
      'cost': '\$0.00',
    },
  };

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
          // Header
          Row(
            children: [
              Icon(
                Icons.smart_toy,
                color: QwamosColors.cyberViolet,
                size: 28,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'AI ASSISTANTS',
                      style: QwamosTypography.h5.copyWith(
                        color: QwamosColors.cyberViolet,
                      ),
                    ),
                    Text(
                      'Triple-AI Security System',
                      style: QwamosTypography.labelSmall.copyWith(
                        color: QwamosColors.textSecondary,
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),
              ),
              // Total Cost
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: QwamosColors.amberWarning.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  '\$0.18',
                  style: QwamosTypography.mono.copyWith(
                    color: QwamosColors.amberWarning,
                    fontSize: 13,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          // AI Assistant Cards
          _buildAssistantCard('kali-gpt'),
          const SizedBox(height: 12),
          _buildAssistantCard('claude'),
          const SizedBox(height: 12),
          _buildAssistantCard('chatgpt'),
          const SizedBox(height: 16),
          // Quick Actions
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () {},
                  icon: Icon(Icons.chat_bubble_outline, size: 16),
                  label: Text('Query AI'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: QwamosColors.cyberViolet,
                    side: BorderSide(
                      color: QwamosColors.cyberViolet.withOpacity(0.5),
                      width: 1.5,
                    ),
                    padding: const EdgeInsets.symmetric(vertical: 10),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () {},
                  icon: Icon(Icons.bar_chart, size: 16),
                  label: Text('Stats'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: QwamosColors.aquaBlue,
                    side: BorderSide(
                      color: QwamosColors.aquaBlue.withOpacity(0.5),
                      width: 1.5,
                    ),
                    padding: const EdgeInsets.symmetric(vertical: 10),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                ),
              ),
            ],
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

  Widget _buildAssistantCard(String assistantId) {
    final info = _assistantInfo[assistantId]!;
    final bool isEnabled = _assistantStatus[assistantId]!;
    final Color color = info['color'] as Color;

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: QwamosColors.background,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: isEnabled ? color.withOpacity(0.3) : QwamosColors.textSecondary.withOpacity(0.2),
          width: 1.5,
        ),
        boxShadow: isEnabled
            ? [
                BoxShadow(
                  color: color.withOpacity(0.15),
                  blurRadius: 8,
                ),
              ]
            : [],
      ),
      child: Column(
        children: [
          Row(
            children: [
              // Icon
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  info['icon'] as IconData,
                  color: color,
                  size: 20,
                ),
              ),
              const SizedBox(width: 12),
              // Info
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          info['name'] as String,
                          style: QwamosTypography.h6.copyWith(
                            fontSize: 14,
                            color: isEnabled ? QwamosColors.textPrimary : QwamosColors.textSecondary,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: color.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(3),
                          ),
                          child: Text(
                            info['privacy'] as String,
                            style: QwamosTypography.mono.copyWith(
                              color: color,
                              fontSize: 9,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      info['model'] as String,
                      style: QwamosTypography.labelSmall.copyWith(
                        color: QwamosColors.textSecondary,
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),
              ),
              // Toggle
              Switch(
                value: isEnabled,
                onChanged: (value) {
                  setState(() {
                    _assistantStatus[assistantId] = value;
                  });
                },
                activeColor: color,
                activeTrackColor: color.withOpacity(0.3),
              ),
            ],
          ),
          if (isEnabled) ...[
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.data_usage,
                      size: 14,
                      color: QwamosColors.textSecondary,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      info['usage'] as String,
                      style: QwamosTypography.mono.copyWith(
                        color: QwamosColors.textSecondary,
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),
                Text(
                  'Cost: ${info['cost']}',
                  style: QwamosTypography.mono.copyWith(
                    color: QwamosColors.textSecondary,
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }
}
