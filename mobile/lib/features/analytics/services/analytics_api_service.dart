import 'package:dio/dio.dart';
import 'package:lifevault/core/network/api_client.dart';
import 'package:lifevault/core/network/api_exception.dart';
import 'package:lifevault/core/constants/app_constants.dart';
import '../models/analytics_models.dart';

class AnalyticsApiService {
  final ApiClient _apiClient = ApiClient();

  // Entries
  Future<AnalyticsEntry> createEntry(AnalyticsEntryCreate entry) async {
    try {
      final response = await _apiClient.dio.post(
        AppConstants.analyticsEntries,
        data: entry.toJson(),
      );
      return AnalyticsEntry.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<List<AnalyticsEntry>> getEntries({
    String? category,
    String? startDate,
    String? endDate,
    int? limit,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (category != null) queryParams['category'] = category;
      if (startDate != null) queryParams['start_date'] = startDate;
      if (endDate != null) queryParams['end_date'] = endDate;
      if (limit != null) queryParams['limit'] = limit;

      final response = await _apiClient.dio.get(
        AppConstants.analyticsEntries,
        queryParameters: queryParams,
      );

      final List<dynamic> data = response.data;
      return data.map((json) => AnalyticsEntry.fromJson(json)).toList();
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<AnalyticsEntry> getEntry(String id) async {
    try {
      final response = await _apiClient.dio.get(
        '${AppConstants.analyticsEntries}/$id',
      );
      return AnalyticsEntry.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<AnalyticsEntry> updateEntry(
    String id,
    AnalyticsEntryCreate entry,
  ) async {
    try {
      final response = await _apiClient.dio.put(
        '${AppConstants.analyticsEntries}/$id',
        data: entry.toJson(),
      );
      return AnalyticsEntry.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<void> deleteEntry(String id) async {
    try {
      await _apiClient.dio.delete('${AppConstants.analyticsEntries}/$id');
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  // Statistics
  Future<AnalyticsStats> getStats({
    String? startDate,
    String? endDate,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (startDate != null) queryParams['start_date'] = startDate;
      if (endDate != null) queryParams['end_date'] = endDate;

      final response = await _apiClient.dio.get(
        AppConstants.analyticsStats,
        queryParameters: queryParams,
      );
      return AnalyticsStats.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  // Time Series
  Future<TimeSeriesData> getTimeSeries({
    required String metric,
    String? category,
    String? startDate,
    String? endDate,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'metric': metric,
      };
      if (category != null) queryParams['category'] = category;
      if (startDate != null) queryParams['start_date'] = startDate;
      if (endDate != null) queryParams['end_date'] = endDate;

      final response = await _apiClient.dio.get(
        AppConstants.analyticsTimeSeries,
        queryParameters: queryParams,
      );
      return TimeSeriesData.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  // Goals
  Future<Goal> createGoal(GoalCreate goal) async {
    try {
      final response = await _apiClient.dio.post(
        AppConstants.analyticsGoals,
        data: goal.toJson(),
      );
      return Goal.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<List<Goal>> getGoals() async {
    try {
      final response = await _apiClient.dio.get(AppConstants.analyticsGoals);
      final List<dynamic> data = response.data;
      return data.map((json) => Goal.fromJson(json)).toList();
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<Goal> updateGoal(String id, GoalCreate goal) async {
    try {
      final response = await _apiClient.dio.put(
        '${AppConstants.analyticsGoals}/$id',
        data: goal.toJson(),
      );
      return Goal.fromJson(response.data);
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }

  Future<void> deleteGoal(String id) async {
    try {
      await _apiClient.dio.delete('${AppConstants.analyticsGoals}/$id');
    } on DioException catch (e) {
      throw ApiException.fromDioError(e);
    }
  }
}

