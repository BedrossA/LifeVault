class AppConstants {
  // API Endpoints
  static const String authLogin = '/auth/login';
  static const String authRegister = '/auth/register';
  static const String authRefresh = '/auth/refresh';
  static const String authLogout = '/auth/logout';
  static const String authMe = '/auth/me';
  static const String authHistory = '/auth/history';
  static const String authActivity = '/auth/activity';
  static const String authForgotPassword = '/auth/forgot-password';
  static const String authResetPassword = '/auth/reset-password';
  
  // Analytics Endpoints
  static const String analyticsEntries = '/analytics/entries';
  static const String analyticsStats = '/analytics/stats';
  static const String analyticsTimeSeries = '/analytics/time-series';
  static const String analyticsGoals = '/analytics/goals';
  static const String analyticsExport = '/analytics/export';
  
  // Face Recognition Endpoints
  static const String faceMyFaces = '/face/my-faces';
  static const String faceEnroll = '/face/enroll';
  static const String faceRecognize = '/face/recognize';
  static const String faceDelete = '/face/delete';
  static const String faceStats = '/face/stats';
  static const String faceConfig = '/face/config';
  
  // Routes
  static const String routeSplash = '/';
  static const String routeLogin = '/login';
  static const String routeRegister = '/register';
  static const String routeForgotPassword = '/forgot-password';
  static const String routeResetPassword = '/reset-password';
  static const String routeHome = '/home';
  static const String routeDashboard = '/dashboard';
  static const String routeAnalytics = '/analytics';
  static const String routeFaceRecognition = '/face-recognition';
  static const String routeProfile = '/profile';
  static const String routeActivity = '/activity';
  static const String routeSettings = '/settings';
}

