import 'package:dio/dio.dart';
import 'package:lifevault/core/network/api_client.dart';
import 'package:lifevault/core/network/api_exception.dart';
import 'package:lifevault/core/constants/app_constants.dart';
import '../models/auth_models.dart';

class AuthApiService {
  final ApiClient _apiClient = ApiClient();

  Future<TokenResponse> login(LoginRequest request) async {
    try {
      final formData = FormData.fromMap({
        'username': request.username,
        'password': request.password,
      });

      final response = await _apiClient.dio.post(
        AppConstants.authLogin,
        data: formData,
        options: Options(
          headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        ),
      );

      return TokenResponse.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<User> register(RegisterRequest request) async {
    try {
      final response = await _apiClient.dio.post(
        AppConstants.authRegister,
        data: request.toJson(),
      );

      return User.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<TokenResponse> refreshToken(RefreshTokenRequest request) async {
    try {
      final response = await _apiClient.dio.post(
        AppConstants.authRefresh,
        data: request.toJson(),
      );

      return TokenResponse.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<void> logout() async {
    try {
      await _apiClient.dio.post(AppConstants.authLogout);
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<User> getCurrentUser() async {
    try {
      final response = await _apiClient.dio.get(AppConstants.authMe);
      return User.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<List<LoginHistory>> getLoginHistory({int limit = 10}) async {
    try {
      final response = await _apiClient.dio.get(
        AppConstants.authHistory,
        queryParameters: {'limit': limit},
      );

      final List<dynamic> data = response.data;
      return data.map((json) => LoginHistory.fromJson(json)).toList();
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<void> forgotPassword(String email) async {
    try {
      await _apiClient.dio.post(
        AppConstants.authForgotPassword,
        data: {'email': email},
      );
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<void> resetPassword({
    required String token,
    required String newPassword,
  }) async {
    try {
      await _apiClient.dio.post(
        AppConstants.authResetPassword,
        data: {
          'token': token,
          'new_password': newPassword,
        },
      );
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }
}

