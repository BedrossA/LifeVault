import 'dart:io';
import 'package:dio/dio.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_exception.dart';
import '../../../core/config/app_config.dart';

class FaceApiService {
  final ApiClient _apiClient = ApiClient();

  /// Enroll a new face
  Future<Map<String, dynamic>> enrollFace({
    required File imageFile,
    required String label,
  }) async {
    try {
      final formData = FormData.fromMap({
        'label': label,
        'image': await MultipartFile.fromFile(
          imageFile.path,
          filename: imageFile.path.split('/').last,
        ),
      });

      final response = await _apiClient.dio.post(
        '${AppConfig.baseUrl}/face/enroll',
        data: formData,
      );

      if (response.statusCode == 200) {
        return response.data as Map<String, dynamic>;
      } else {
        throw ApiException(
          message: 'Failed to enroll face',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      throw ApiException.fromDioException(e);
    }
  }

  /// Recognize a face
  Future<Map<String, dynamic>> recognizeFace({
    required File imageFile,
  }) async {
    try {
      final formData = FormData.fromMap({
        'image': await MultipartFile.fromFile(
          imageFile.path,
          filename: imageFile.path.split('/').last,
        ),
      });

      final response = await _apiClient.dio.post(
        '${AppConfig.baseUrl}/face/recognize',
        data: formData,
      );

      if (response.statusCode == 200) {
        return response.data as Map<String, dynamic>;
      } else {
        throw ApiException(
          message: 'Failed to recognize face',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      throw ApiException.fromDioException(e);
    }
  }

  /// Get list of enrolled faces for current user
  Future<List<Map<String, dynamic>>> getMyFaces() async {
    try {
      final response = await _apiClient.dio.get(
        '${AppConfig.baseUrl}/face/my-faces',
      );

      if (response.statusCode == 200) {
        final data = response.data;
        if (data is List) {
          return data.cast<Map<String, dynamic>>();
        }
        return [];
      } else {
        throw ApiException(
          message: 'Failed to get faces',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      throw ApiException.fromDioException(e);
    }
  }

  /// Delete a face
  Future<void> deleteFace(int faceId) async {
    try {
      final response = await _apiClient.dio.delete(
        '${AppConfig.baseUrl}/face/$faceId',
      );

      if (response.statusCode != 200 && response.statusCode != 204) {
        throw ApiException(
          message: 'Failed to delete face',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      throw ApiException.fromDioException(e);
    }
  }

  /// Add additional encoding to existing face
  Future<Map<String, dynamic>> addFaceEncoding({
    required int faceId,
    required File imageFile,
  }) async {
    try {
      final formData = FormData.fromMap({
        'image': await MultipartFile.fromFile(
          imageFile.path,
          filename: imageFile.path.split('/').last,
        ),
      });

      final response = await _apiClient.dio.post(
        '${AppConfig.baseUrl}/face/$faceId/add-encoding',
        data: formData,
      );

      if (response.statusCode == 200) {
        return response.data as Map<String, dynamic>;
      } else {
        throw ApiException(
          message: 'Failed to add face encoding',
          statusCode: response.statusCode,
        );
      }
    } on DioException catch (e) {
      throw ApiException.fromDioException(e);
    }
  }
}

