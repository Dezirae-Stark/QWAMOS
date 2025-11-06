import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'theme/dark_theme.dart';
import 'pages/main_dashboard.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Set status bar and navigation bar to transparent
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.light,
      systemNavigationBarColor: Color(0xFF0B0E16),
      systemNavigationBarIconBrightness: Brightness.light,
    ),
  );

  // Lock orientation to portrait
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);

  runApp(const QwamosApp());
}

class QwamosApp extends StatelessWidget {
  const QwamosApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'QWAMOS Hypervisor',
      debugShowCheckedModeBanner: false,
      theme: QwamosDarkTheme.theme,
      home: const MainDashboard(),
    );
  }
}
