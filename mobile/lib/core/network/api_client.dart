import 'package:dio/dio.dart';
import 'package:pretty_dio_logger/pretty_dio_logger.dart';
import '../config/app_config.dart';
import '../utils/storage_service.dart';
import '../constants/app_constants.dart';

class ApiClient {
  static final ApiClient _instance = ApiClient._internal();
  factory ApiClient() => _instance;
  ApiClient._internal();

  late Dio _dio;
  final StorageService _storage = StorageService();

  Dio get dio => _dio;

  Future<void> init() async {
    _dio = Dio(
      BaseOptions(
        baseUrl: AppConfig.baseUrl,
        connectTimeout: AppConfig.connectTimeout,
        receiveTimeout: AppConfig.receiveTimeout,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    // Add interceptors
    _dio.interceptors.add(
      QueuedInterceptorsWrapper(
        onRequest: (options, handler) async {
          // Add auth token if available
          final token = await _storage.getAccessToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
        onError: (error, handler) async {
          // Handle 401 - Unauthorized
          if (error.response?.statusCode == 401) {
            // Try to refresh token
            final refreshed = await _refreshToken();
            if (refreshed) {
              // Retry the request
              try {
                final opts = error.requestOptions;
                final token = await _storage.getAccessToken();
                opts.headers['Authorization'] = 'Bearer $token';
                final response = await _dio.fetch(opts);
                return handler.resolve(response);
              } catch (e) {
                return handler.reject(error);
              }
            } else {
              // Refresh failed, clear tokens
              await _storage.clearTokens();
              return handler.reject(error);
            }
          }
          
          // Retry on network errors (max 3 times)
          if (error.type == DioExceptionType.connectionTimeout ||
              error.type == DioExceptionType.receiveTimeout ||
              error.type == DioExceptionType.connectionError) {
            
            final retryCount = error.requestOptions.extra['retryCount'] as int? ?? 0;
            
            if (retryCount < 3) {
              error.requestOptions.extra['retryCount'] = retryCount + 1;
              
              // Wait before retry (exponential backoff)
              await Future.delayed(Duration(seconds: 1 << retryCount));
              
              try {
                final response = await _dio.fetch(error.requestOptions);
                return handler.resolve(response);
              } catch (e) {
                return handler.next(error);
              }
            }
          }
          return handler.next(error);
        },
      ),
    );

    // Add logger in debug mode
    if (const bool.fromEnvironment('dart.vm.product') == false) {
      _dio.interceptors.add(
        PrettyDioLogger(
          requestHeader: true,
          requestBody: true,
          responseBody: true,
          responseHeader: false,
          error: true,
          compact: true,
        ),
      );
    }
  }

  Future<bool> _refreshToken() async {
    try {
      final refreshToken = await _storage.getRefreshToken();
      if (refreshToken == null) return false;

      final response = await _dio.post(
        AppConstants.authRefresh,
        data: {'refresh_token': refreshToken},
      );

      if (response.statusCode == 200) {
        final data = response.data;
        await _storage.setAccessToken(data['access_token']);
        if (data['refresh_token'] != null) {
          await _storage.setRefreshToken(data['refresh_token']);
        }
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }
}

