import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/colors.dart';
import '../theme/typography.dart';
import '../theme/glow_effects.dart';

class MLThreatDetectionWidget extends StatefulWidget {
  const MLThreatDetectionWidget({super.key});

  @override
  State<MLThreatDetectionWidget> createState() => _MLThreatDetectionWidgetState();
}

class _MLThreatDetectionWidgetState extends State<MLThreatDetectionWidget> {
  bool _networkDetectorEnabled = true;
  bool _fileSystemDetectorEnabled = true;
  bool _syscallDetectorEnabled = true;
  int _systemHealth = 87; // 0-100 score

  final List<Map<String, dynamic>> _recentThreats = [
    {
      'type': 'Port Scan',
      'severity': 'HIGH',
      'source': '192.168.1.100',
      'time': '2 min ago',
      'status': 'BLOCKED',
    },
    {
      'type': 'Ransomware Pattern',
      'severity': 'CRITICAL',
      'source': '/home/user/downloads',
      'time': '15 min ago',
      'status': 'QUARANTINED',
    },
    {
      'type': 'Privilege Escalation',
      'severity': 'MEDIUM',
      'source': 'PID 1337',
      'time': '1 hour ago',
      'status': 'MONITORED',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: QwamosColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: _systemHealth > 70
              ? QwamosColors.neonGreen.withOpacity(0.5)
              : QwamosColors.redCritical.withOpacity(0.5),
          width: 2,
        ),
        boxShadow: [
          BoxShadow(
            color: (_systemHealth > 70
                    ? QwamosColors.neonGreen
                    : QwamosColors.redCritical)
                .withOpacity(0.2),
            blurRadius: 12,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with System Health
          Row(
            children: [
              Icon(
                Icons.security,
                color: QwamosColors.neonGreen,
                size: 28,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'ML THREAT DETECTION',
                      style: QwamosTypography.h5.copyWith(
                        color: QwamosColors.neonGreen,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'System Health: $_systemHealth%',
                      style: QwamosTypography.labelSmall.copyWith(
                        color: QwamosColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              // Health Meter
              SizedBox(
                width: 60,
                height: 60,
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    CircularProgressIndicator(
                      value: _systemHealth / 100,
                      strokeWidth: 6,
                      backgroundColor: QwamosColors.background,
                      valueColor: AlwaysStoppedAnimation(
                        _systemHealth > 70
                            ? QwamosColors.neonGreen
                            : _systemHealth > 40
                                ? QwamosColors.amberWarning
                                : QwamosColors.redCritical,
                      ),
                    ),
                    Text(
                      '$_systemHealth',
                      style: QwamosTypography.h6.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          // Detectors
          Text('ML DETECTORS', style: QwamosTypography.labelSmall),
          const SizedBox(height: 12),
          _buildDetectorRow(
            'Network Anomaly Detector',
            _networkDetectorEnabled,
            Icons.wifi,
            (value) => setState(() => _networkDetectorEnabled = value),
          ),
          const SizedBox(height: 10),
          _buildDetectorRow(
            'File System Monitor',
            _fileSystemDetectorEnabled,
            Icons.folder,
            (value) => setState(() => _fileSystemDetectorEnabled = value),
          ),
          const SizedBox(height: 10),
          _buildDetectorRow(
            'System Call Analyzer',
            _syscallDetectorEnabled,
            Icons.code,
            (value) => setState(() => _syscallDetectorEnabled = value),
          ),
          const SizedBox(height: 20),
          // Recent Threats
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('RECENT THREATS', style: QwamosTypography.labelSmall),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: QwamosColors.redCritical.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  '${_recentThreats.length}',
                  style: QwamosTypography.mono.copyWith(
                    color: QwamosColors.redCritical,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ..._recentThreats.take(3).map((threat) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: _buildThreatCard(threat),
              )),
          const SizedBox(height: 12),
          // View All Button
          SizedBox(
            width: double.infinity,
            child: OutlinedButton(
              onPressed: () {},
              style: OutlinedButton.styleFrom(
                foregroundColor: QwamosColors.aquaBlue,
                side: BorderSide(
                  color: QwamosColors.aquaBlue.withOpacity(0.5),
                  width: 1.5,
                ),
                padding: const EdgeInsets.symmetric(vertical: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
              child: Text(
                'VIEW ALL THREATS',
                style: QwamosTypography.button.copyWith(
                  color: QwamosColors.aquaBlue,
                  fontSize: 12,
                ),
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

  Widget _buildDetectorRow(
    String name,
    bool enabled,
    IconData icon,
    ValueChanged<bool> onChanged,
  ) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: QwamosColors.background,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: enabled
              ? QwamosColors.neonGreen.withOpacity(0.3)
              : QwamosColors.textSecondary.withOpacity(0.2),
          width: 1.5,
        ),
      ),
      child: Row(
        children: [
          Icon(
            icon,
            color: enabled ? QwamosColors.neonGreen : QwamosColors.textSecondary,
            size: 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              name,
              style: QwamosTypography.body.copyWith(
                color: enabled ? QwamosColors.textPrimary : QwamosColors.textSecondary,
                fontSize: 13,
              ),
            ),
          ),
          Switch(
            value: enabled,
            onChanged: onChanged,
            activeColor: QwamosColors.neonGreen,
            activeTrackColor: QwamosColors.neonGreen.withOpacity(0.3),
          ),
        ],
      ),
    );
  }

  Widget _buildThreatCard(Map<String, dynamic> threat) {
    Color severityColor;
    switch (threat['severity']) {
      case 'CRITICAL':
        severityColor = QwamosColors.redCritical;
        break;
      case 'HIGH':
        severityColor = QwamosColors.amberWarning;
        break;
      default:
        severityColor = QwamosColors.aquaBlue;
    }

    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: QwamosColors.background,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(
          color: severityColor.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Row(
        children: [
          Container(
            width: 4,
            height: 40,
            decoration: BoxDecoration(
              color: severityColor,
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      threat['type'],
                      style: QwamosTypography.mono.copyWith(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: severityColor.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(3),
                      ),
                      child: Text(
                        threat['severity'],
                        style: QwamosTypography.mono.copyWith(
                          color: severityColor,
                          fontSize: 9,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  '${threat['source']} • ${threat['time']}',
                  style: QwamosTypography.labelSmall.copyWith(
                    color: QwamosColors.textSecondary,
                    fontSize: 10,
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: QwamosColors.neonGreen.withOpacity(0.2),
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              threat['status'],
              style: QwamosTypography.mono.copyWith(
                color: QwamosColors.neonGreen,
                fontSize: 9,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
