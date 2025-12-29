class AppConfig {
  // API Configuration
  static const String baseUrl = 'http://192.168.0.109:8000/api/v1';
  static const String apiVersion = 'v1';
  
  // App Info
  static const String appName = 'LifeVault';
  static const String appVersion = '1.0.0';
  
  // Timeouts
  static const Duration connectTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
  
  // Storage Keys
  static const String accessTokenKey = 'access_token';
  static const String refreshTokenKey = 'refresh_token';
  static const String userDataKey = 'user_data';
  static const String themeKey = 'theme_mode';
  
  // Face Recognition
  static const double faceRecognitionTolerance = 0.6;
  static const int maxFacesPerUser = 5;
}

