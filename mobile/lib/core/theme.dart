import 'package:flutter/material.dart';

class DiabloTheme {
  static const bg = Color(0xFF0F0F12);
  static const panel = Color(0xFF17171C);
  static const border = Color(0xFF2A2A33);
  static const accent = Color(0xFFC41E3A);
  static const gold = Color(0xFFD4AF37);

  static ThemeData dark() {
    return ThemeData(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: bg,
      colorScheme: const ColorScheme.dark(
        primary: accent,
        secondary: gold,
        surface: panel,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: panel,
        foregroundColor: Colors.white,
      ),
      cardTheme: CardThemeData(
        color: panel,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: const BorderSide(color: border),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.black26,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: border),
        ),
      ),
    );
  }
}
