import 'package:flutter/material.dart';

import '../core/config.dart';
import '../core/theme.dart';
import '../services/api_client.dart';
import 'live_screen.dart';
import 'reply_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key, required this.config});

  final AppConfig config;

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late AppConfig _config;
  late ApiClient _api;
  int _tab = 0;
  bool _online = false;
  final _urlController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _config = widget.config;
    _api = ApiClient(_config);
    _urlController.text = _config.apiBaseUrl;
    _checkHealth();
  }

  Future<void> _checkHealth() async {
    try {
      final ok = await _api.health();
      if (mounted) setState(() => _online = ok);
    } catch (_) {
      if (mounted) setState(() => _online = false);
    }
  }

  Future<void> _saveUrl() async {
    final url = _urlController.text.trim();
    if (url.isEmpty) return;
    await _config.saveApiUrl(url);
    _config = AppConfig(url);
    _api = ApiClient(_config);
    await _checkHealth();
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('URL API enregistrée')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final pages = [
      LiveScreen(api: _api),
      ReplyScreen(api: _api),
      _SettingsTab(
        online: _online,
        urlController: _urlController,
        onSave: _saveUrl,
        onRefresh: _checkHealth,
      ),
    ];

    return Scaffold(
      appBar: AppBar(
        title: const Text('Diablo Translator'),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 12),
            child: Row(
              children: [
                Icon(Icons.circle, size: 10, color: _online ? Colors.green : Colors.red),
                const SizedBox(width: 6),
                Text(_online ? 'En ligne' : 'Hors ligne', style: const TextStyle(fontSize: 12)),
              ],
            ),
          ),
        ],
      ),
      body: pages[_tab],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _tab,
        onDestinationSelected: (index) => setState(() => _tab = index),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.forum_outlined), label: 'Live'),
          NavigationDestination(icon: Icon(Icons.edit_outlined), label: 'Reply'),
          NavigationDestination(icon: Icon(Icons.settings_outlined), label: 'Réglages'),
        ],
      ),
    );
  }
}

class _SettingsTab extends StatelessWidget {
  const _SettingsTab({
    required this.online,
    required this.urlController,
    required this.onSave,
    required this.onRefresh,
  });

  final bool online;
  final TextEditingController urlController;
  final VoidCallback onSave;
  final VoidCallback onRefresh;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'URL du serveur API',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          const Text(
            'Sur iPhone : utilisez l’IP de votre PC (même Wi‑Fi), ex. http://192.168.1.42:8000',
            style: TextStyle(color: Colors.white70, fontSize: 13),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: urlController,
            decoration: const InputDecoration(hintText: AppConfig.defaultApiUrl),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            children: [
              FilledButton(onPressed: onSave, child: const Text('Enregistrer')),
              OutlinedButton(onPressed: onRefresh, child: const Text('Tester connexion')),
            ],
          ),
          const SizedBox(height: 24),
          Text('Statut : ${online ? "Connecté" : "Déconnecté"}'),
          const SizedBox(height: 16),
          const Text(
            'Lancez sur le PC :\npy -3 launcher.py server\n\nPuis build iOS sur Mac :\ncd mobile && flutter build ios',
            style: TextStyle(color: DiabloTheme.gold, fontSize: 13),
          ),
        ],
      ),
    );
  }
}
