class TranslateResult {
  TranslateResult({
    required this.sourceText,
    required this.translatedText,
    this.sourceLanguage,
    this.targetLanguage,
  });

  final String sourceText;
  final String translatedText;
  final String? sourceLanguage;
  final String? targetLanguage;

  factory TranslateResult.fromJson(Map<String, dynamic> json) => TranslateResult(
        sourceText: json['source_text'] as String,
        translatedText: json['translated_text'] as String,
        sourceLanguage: json['source_language'] as String?,
        targetLanguage: json['target_language'] as String?,
      );
}
