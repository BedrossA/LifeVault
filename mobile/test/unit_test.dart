import 'package:flutter_test/flutter_test.dart';
import 'package:lifevault/features/auth/models/auth_models.dart';
import 'package:lifevault/features/analytics/models/analytics_models.dart';

void main() {
  group('Auth Models', () {
    test('LoginRequest toJson creates correct map', () {
      final request = LoginRequest(
        username: 'testuser',
        password: 'testpass',
      );
      
      final json = request.toJson();
      
      expect(json['username'], 'testuser');
      expect(json['password'], 'testpass');
    });
    
    test('TokenResponse fromJson parses correctly', () {
      final json = {
        'access_token': 'abc123',
        'refresh_token': 'refresh123',
        'token_type': 'bearer',
        'expires_in': 3600,
      };
      
      final response = TokenResponse.fromJson(json);
      
      expect(response.accessToken, 'abc123');
      expect(response.refreshToken, 'refresh123');
      expect(response.tokenType, 'bearer');
      expect(response.expiresIn, 3600);
    });
  });
  
  group('Analytics Models', () {
    test('AnalyticsEntryCreate toJson works correctly', () {
      final entry = AnalyticsEntryCreate(
        category: 'health',
        metric: 'steps',
        value: 10000,
        unit: 'steps',
        notes: 'Morning walk',
      );
      
      final json = entry.toJson();
      
      expect(json['category'], 'health');
      expect(json['metric'], 'steps');
      expect(json['value'], 10000);
      expect(json['unit'], 'steps');
      expect(json['notes'], 'Morning walk');
    });
  });
}