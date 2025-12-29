class LoginRequest {
  final String username;
  final String password;

  LoginRequest({
    required this.username,
    required this.password,
  });

  Map<String, dynamic> toJson() => {
        'username': username,
        'password': password,
      };
}

class RegisterRequest {
  final String username;
  final String email;
  final String password;

  RegisterRequest({
    required this.username,
    required this.email,
    required this.password,
  });

  Map<String, dynamic> toJson() => {
        'username': username,
        'email': email,
        'password': password,
      };
}

class TokenResponse {
  final String accessToken;
  final String refreshToken;
  final String tokenType;
  final int expiresIn;

  TokenResponse({
    required this.accessToken,
    required this.refreshToken,
    required this.tokenType,
    required this.expiresIn,
  });

  factory TokenResponse.fromJson(Map<String, dynamic> json) => TokenResponse(
        accessToken: json['access_token'] as String,
        refreshToken: json['refresh_token'] as String,
        tokenType: json['token_type'] as String? ?? 'bearer',
        expiresIn: json['expires_in'] as int? ?? 1800,
      );
}

class RefreshTokenRequest {
  final String refreshToken;

  RefreshTokenRequest({required this.refreshToken});

  Map<String, dynamic> toJson() => {
        'refresh_token': refreshToken,
      };
}

class User {
  final int id;
  final String username;
  final String email;
  final bool isActive;
  final DateTime? createdAt;
  final DateTime? lastLogin;

  User({
    required this.id,
    required this.username,
    required this.email,
    required this.isActive,
    this.createdAt,
    this.lastLogin,
  });

  factory User.fromJson(Map<String, dynamic> json) => User(
        id: json['id'] as int,
        username: json['username'] as String,
        email: json['email'] as String,
        isActive: json['is_active'] as bool? ?? true,
        createdAt: json['created_at'] != null
            ? DateTime.parse(json['created_at'] as String)
            : null,
        lastLogin: json['last_login'] != null
            ? DateTime.parse(json['last_login'] as String)
            : null,
      );
}

class LoginHistory {
  final int id;
  final int userId;
  final String? ipAddress;
  final String? userAgent;
  final bool success;
  final DateTime timestamp;

  LoginHistory({
    required this.id,
    required this.userId,
    this.ipAddress,
    this.userAgent,
    required this.success,
    required this.timestamp,
  });

  factory LoginHistory.fromJson(Map<String, dynamic> json) => LoginHistory(
        id: json['id'] as int,
        userId: json['user_id'] as int,
        ipAddress: json['ip_address'] as String?,
        userAgent: json['user_agent'] as String?,
        success: json['success'] as bool? ?? true,
        timestamp: DateTime.parse(json['timestamp'] as String),
      );
}

