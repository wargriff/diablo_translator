import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/chat_message.dart';
import '../models/translate_result.dart';
import '../core/config.dart';

class ApiClient {
  ApiClient(this.config);

  final AppConfig config;

  Uri _uri(String path) => Uri.parse('${config.apiBaseUrl}$path');

  List<dynamic> _asList(dynamic payload) {
    if (payload is List) return payload;
    if (payload is Map && payload['items'] is List) {
      return payload['items'] as List;
    }
    return const [];
  }

  Future<bool> health() async {
    final response = await http.get(_uri('/api/v1/health'));
    return response.statusCode == 200;
  }

  Future<List<ChatMessage>> messages({int limit = 50}) async {
    final response = await http.get(_uri('/api/v1/messages?limit=$limit'));
    if (response.statusCode != 200) {
      throw Exception('API ${response.statusCode}');
    }
    final list = _asList(jsonDecode(response.body));
    return list.map((item) => ChatMessage.fromJson(item as Map<String, dynamic>)).toList();
  }

  Future<TranslateResult> translate(String text) async {
    final response = await http.post(
      _uri('/api/v1/translate'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'text': text, 'origin': 'user'}),
    );
    if (response.statusCode != 200) {
      throw Exception('API ${response.statusCode}');
    }
    return TranslateResult.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  Future<TranslateResult> compose(String text) async {
    final response = await http.post(
      _uri('/api/v1/reply/compose'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'text': text}),
    );
    if (response.statusCode != 200) {
      throw Exception('API ${response.statusCode}');
    }
    final json = jsonDecode(response.body) as Map<String, dynamic>;
    return TranslateResult(
      sourceText: json['source_text'] as String,
      translatedText: json['translated_text'] as String,
    );
  }

  Future<List<QuickReply>> quickReplies() async {
    final response = await http.get(_uri('/api/v1/reply/quick'));
    if (response.statusCode != 200) {
      throw Exception('API ${response.statusCode}');
    }
    final list = _asList(jsonDecode(response.body));
    return list
        .map((item) => QuickReply.fromJson(item as Map<String, dynamic>))
        .toList();
  }
}

class QuickReply {
  QuickReply({required this.key, required this.label, required this.translatedText});

  final String key;
  final String label;
  final String translatedText;

  factory QuickReply.fromJson(Map<String, dynamic> json) => QuickReply(
        key: json['key'] as String,
        label: json['label'] as String,
        translatedText: json['translated_text'] as String,
      );
}
