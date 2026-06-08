class ChatMessage {
  ChatMessage({
    required this.id,
    required this.sourceText,
    required this.translatedText,
    this.sourceLanguage,
    this.createdAt,
  });

  final int id;
  final String sourceText;
  final String translatedText;
  final String? sourceLanguage;
  final String? createdAt;

  factory ChatMessage.fromJson(Map<String, dynamic> json) => ChatMessage(
        id: json['id'] as int,
        sourceText: json['source_text'] as String,
        translatedText: json['translated_text'] as String,
        sourceLanguage: json['source_language'] as String?,
        createdAt: json['created_at'] as String?,
      );
}
