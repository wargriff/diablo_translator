import 'package:flutter_test/flutter_test.dart';

import 'package:diablo_translator/core/config.dart';

void main() {
  test('default API URL is set', () {
    expect(AppConfig.defaultApiUrl, startsWith('http://'));
  });
}
