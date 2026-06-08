import 'package:flutter/material.dart';

import 'core/config.dart';
import 'core/theme.dart';
import 'screens/home_screen.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final config = await AppConfig.load();
  runApp(DiabloTranslatorApp(config: config));
}

class DiabloTranslatorApp extends StatelessWidget {
  const DiabloTranslatorApp({super.key, required this.config});

  final AppConfig config;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Diablo Translator',
      theme: DiabloTheme.dark(),
      home: HomeScreen(config: config),
      debugShowCheckedModeBanner: false,
    );
  }
}
