import 'package:dio/dio.dart';

class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final dynamic data;

  ApiException({
    required this.message,
    this.statusCode,
    this.data,
  });

  factory ApiException.fromDioError(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return ApiException(
          message: 'Connection timeout. Please try again.',
          statusCode: error.response?.statusCode,
        );
      case DioExceptionType.badResponse:
        final statusCode = error.response?.statusCode;
        final data = error.response?.data;
        String message = 'An error occurred';
        
        if (data is Map<String, dynamic>) {
          message = data['detail'] ?? data['message'] ?? message;
        } else if (data is String) {
          message = data;
        }
        
        return ApiException(
          message: message,
          statusCode: statusCode,
          data: data,
        );
      case DioExceptionType.cancel:
        return ApiException(message: 'Request cancelled');
      case DioExceptionType.unknown:
      default:
        return ApiException(
          message: error.message ?? 'An unexpected error occurred',
          statusCode: error.response?.statusCode,
        );
    }
  }

  factory ApiException.fromDioException(DioException error) {
    return ApiException.fromDioError(error);
  }

  @override
  String toString() => message;
}

