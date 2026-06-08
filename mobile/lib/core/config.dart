import 'package:shared_preferences/shared_preferences.dart';

class AppConfig {
  AppConfig(this.apiBaseUrl);

  final String apiBaseUrl;

  String get wsBaseUrl {
    final uri = Uri.parse(apiBaseUrl);
    final scheme = uri.scheme == 'https' ? 'wss' : 'ws';
    return '$scheme://${uri.host}:${uri.port}';
  }

  static const defaultApiUrl = 'http://192.168.1.100:8000';
  static const prefsKey = 'api_base_url';

  static Future<AppConfig> load() async {
    final prefs = await SharedPreferences.getInstance();
    final url = prefs.getString(prefsKey) ?? defaultApiUrl;
    return AppConfig(url);
  }

  Future<void> saveApiUrl(String url) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(prefsKey, url);
  }
}
