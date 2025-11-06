import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/colors.dart';
import '../theme/typography.dart';

class AIAppBuilderWidget extends StatefulWidget {
  const AIAppBuilderWidget({super.key});

  @override
  State<AIAppBuilderWidget> createState() => _AIAppBuilderWidgetState();
}

class _AIAppBuilderWidgetState extends State<AIAppBuilderWidget> {
  final TextEditingController _requestController = TextEditingController();
  bool _isBuilding = false;
  int _currentStage = 0;

  final List<String> _buildStages = [
    'Requirements Analysis',
    'Code Generation',
    'Security Audit',
    'Quality Assurance',
    'Enhancement Suggestions',
    'User Approval',
    'Isolated Build',
    'Deployment',
  ];

  @override
  void dispose() {
    _requestController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: QwamosColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: QwamosColors.cyberViolet.withOpacity(0.5),
          width: 2,
        ),
        boxShadow: [
          BoxShadow(
            color: QwamosColors.cyberViolet.withOpacity(0.2),
            blurRadius: 12,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              Icon(
                Icons.construction,
                color: QwamosColors.cyberViolet,
                size: 28,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'AI APP BUILDER',
                      style: QwamosTypography.h5.copyWith(
                        color: QwamosColors.cyberViolet,
                      ),
                    ),
                    Text(
                      'Triple-AI Generation & Validation',
                      style: QwamosTypography.labelSmall.copyWith(
                        color: QwamosColors.textSecondary,
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: QwamosColors.neonGreen.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(
                    color: QwamosColors.neonGreen.withOpacity(0.5),
                    width: 1.5,
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.verified_user,
                      size: 14,
                      color: QwamosColors.neonGreen,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      'SECURE',
                      style: QwamosTypography.mono.copyWith(
                        color: QwamosColors.neonGreen,
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          // App Request Input
          Text(
            'DESCRIBE YOUR APP',
            style: QwamosTypography.labelSmall,
          ),
          const SizedBox(height: 8),
          TextField(
            controller: _requestController,
            maxLines: 3,
            style: QwamosTypography.body,
            decoration: InputDecoration(
              hintText: 'e.g., "Build a todo app with AES encryption and dark mode"',
              hintStyle: QwamosTypography.body.copyWith(
                color: QwamosColors.textSecondary,
              ),
              filled: true,
              fillColor: QwamosColors.background,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide(
                  color: QwamosColors.cyberViolet.withOpacity(0.3),
                  width: 1.5,
                ),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide(
                  color: QwamosColors.cyberViolet.withOpacity(0.3),
                  width: 1.5,
                ),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: BorderSide(
                  color: QwamosColors.cyberViolet,
                  width: 2,
                ),
              ),
            ),
          ),
          const SizedBox(height: 16),
          // Build Progress
          if (_isBuilding) ...[
            Text(
              'BUILD PROGRESS',
              style: QwamosTypography.labelSmall,
            ),
            const SizedBox(height: 12),
            ..._buildStages.asMap().entries.map((entry) {
              int index = entry.key;
              String stage = entry.value;
              bool isActive = index == _currentStage;
              bool isCompleted = index < _currentStage;

              return Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  children: [
                    Icon(
                      isCompleted
                          ? Icons.check_circle
                          : isActive
                              ? Icons.radio_button_checked
                              : Icons.radio_button_unchecked,
                      size: 20,
                      color: isCompleted
                          ? QwamosColors.neonGreen
                          : isActive
                              ? QwamosColors.cyberViolet
                              : QwamosColors.textSecondary,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        stage,
                        style: QwamosTypography.body.copyWith(
                          color: isActive
                              ? QwamosColors.cyberViolet
                              : isCompleted
                                  ? QwamosColors.neonGreen
                                  : QwamosColors.textSecondary,
                          fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
                          fontSize: 13,
                        ),
                      ),
                    ),
                  ],
                ),
              );
            }),
            const SizedBox(height: 16),
          ],
          // Build Button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _isBuilding
                  ? null
                  : () {
                      setState(() {
                        _isBuilding = true;
                        _currentStage = 0;
                      });
                      // Simulate build progress
                      _simulateBuild();
                    },
              style: ElevatedButton.styleFrom(
                backgroundColor: _isBuilding
                    ? QwamosColors.textSecondary.withOpacity(0.2)
                    : QwamosColors.cyberViolet,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  if (_isBuilding)
                    SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation(Colors.white),
                      ),
                    ),
                  if (_isBuilding) const SizedBox(width: 12),
                  Text(
                    _isBuilding ? 'BUILDING...' : 'BUILD APP',
                    style: QwamosTypography.button.copyWith(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
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

  void _simulateBuild() {
    Future.forEach(_buildStages, (stage) {
      return Future.delayed(Duration(seconds: 2), () {
        setState(() {
          if (_currentStage < _buildStages.length - 1) {
            _currentStage++;
          } else {
            _isBuilding = false;
            _currentStage = 0;
          }
        });
      });
    });
  }
}
