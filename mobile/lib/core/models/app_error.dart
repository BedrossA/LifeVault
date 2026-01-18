import '../network/api_exception.dart';

enum ErrorType {
  network,
  authentication,
  server,
  validation,
  unknown,
}

class AppError {
  final String message;
  final ErrorType type;
  final int? statusCode;
  final dynamic originalError;

  AppError({
    required this.message,
    required this.type,
    this.statusCode,
    this.originalError,
  });

  factory AppError.fromException(Exception exception) {
    if (exception is ApiException) {
      return AppError(
        message: exception.message,
        type: _mapStatusCodeToType(exception.statusCode),
        statusCode: exception.statusCode,
        originalError: exception,
      );
    }
    
    return AppError(
      message: exception.toString(),
      type: ErrorType.unknown,
      originalError: exception,
    );
  }

  static ErrorType _mapStatusCodeToType(int? statusCode) {
    if (statusCode == null) return ErrorType.network;
    if (statusCode == 401 || statusCode == 403) return ErrorType.authentication;
    if (statusCode >= 400 && statusCode < 500) return ErrorType.validation;
    if (statusCode >= 500) return ErrorType.server;
    return ErrorType.unknown;
  }

  bool get isAuthError => type == ErrorType.authentication;
  bool get isNetworkError => type == ErrorType.network;
}