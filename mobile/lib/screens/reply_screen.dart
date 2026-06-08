import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../core/theme.dart';
import '../services/api_client.dart';

class ReplyScreen extends StatefulWidget {
  const ReplyScreen({super.key, required this.api});

  final ApiClient api;

  @override
  State<ReplyScreen> createState() => _ReplyScreenState();
}

class _ReplyScreenState extends State<ReplyScreen> {
  final _controller = TextEditingController();
  String _preview = '';
  List<QuickReply> _quick = [];
  bool _busy = false;

  @override
  void initState() {
    super.initState();
    _controller.addListener(_onTextChanged);
    _loadQuick();
  }

  Future<void> _loadQuick() async {
    try {
      final items = await widget.api.quickReplies();
      if (mounted) setState(() => _quick = items);
    } catch (_) {}
  }

  void _onTextChanged() {
    final text = _controller.text.trim();
    if (text.isEmpty) {
      setState(() => _preview = '');
      return;
    }
    Future.delayed(const Duration(milliseconds: 400), () async {
      if (_controller.text.trim() != text) return;
      try {
        final result = await widget.api.compose(text);
        if (mounted && _controller.text.trim() == text) {
          setState(() => _preview = result.translatedText);
        }
      } catch (_) {}
    });
  }

  Future<void> _copy({bool clear = false}) async {
    if (_preview.isEmpty) return;
    await Clipboard.setData(ClipboardData(text: _preview));
    if (clear) {
      _controller.clear();
      setState(() => _preview = '');
    }
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Texte copié')),
      );
    }
  }

  Future<void> _save() async {
    final text = _controller.text.trim();
    if (text.isEmpty) return;
    setState(() => _busy = true);
    try {
      await widget.api.translate(text);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Traduction enregistrée')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erreur : $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        TextField(
          controller: _controller,
          maxLines: 4,
          decoration: const InputDecoration(
            hintText: 'Bonjour, comment vas-tu ?',
            labelText: 'Votre message',
          ),
        ),
        const SizedBox(height: 12),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Aperçu traduit', style: TextStyle(color: DiabloTheme.gold)),
                const SizedBox(height: 8),
                Text(_preview.isEmpty ? '…' : _preview, style: const TextStyle(fontSize: 16)),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            FilledButton(
              onPressed: _preview.isEmpty ? null : () => _copy(),
              child: const Text('Copier'),
            ),
            OutlinedButton(
              onPressed: _preview.isEmpty ? null : () => _copy(clear: true),
              child: const Text('Copier et effacer'),
            ),
            OutlinedButton(
              onPressed: _busy ? null : _save,
              child: const Text('Enregistrer'),
            ),
          ],
        ),
        const SizedBox(height: 20),
        const Text('Réponses rapides', style: TextStyle(fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          children: _quick
              .map(
                (item) => ActionChip(
                  label: Text(item.label),
                  onPressed: () {
                    _controller.text = item.label;
                    setState(() => _preview = item.translatedText);
                  },
                ),
              )
              .toList(),
        ),
      ],
    );
  }
}
