import 'dart:convert';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';
import '../../../core/services/offline_storage_service.dart';
import '../../../features/analytics/services/analytics_api_service.dart';
import '../../../features/face/services/face_api_service.dart';

class ExportService {
  final OfflineStorageService _offlineStorage = OfflineStorageService();
  final AnalyticsApiService _analyticsService = AnalyticsApiService();
  final FaceApiService _faceService = FaceApiService();

  /// Export all user data to JSON file
  Future<void> exportData() async {
    try {
      final Map<String, dynamic> exportData = {
        'export_date': DateTime.now().toIso8601String(),
        'version': '1.0',
        'user_data': {},
        'analytics': [],
        'face_data': [],
        'offline_data': {},
      };

      // Export analytics data
      try {
        final analytics = await _analyticsService.getEntries();
        exportData['analytics'] = analytics.map((e) => {
          'id': e.id,
          'user_id': e.userId,
          'category': e.category,
          'metric': e.metric,
          'value': e.value,
          'unit': e.unit,
          'notes': e.notes,
          'metadata': e.metadata,
          'timestamp': e.timestamp.toIso8601String(),
        }).toList();
      } catch (e) {
        // Continue if analytics export fails
      }

      // Export face data
      try {
        final faces = await _faceService.getMyFaces();
        exportData['face_data'] = faces;
      } catch (e) {
        // Continue if face data export fails
      }

      // Export offline storage data
      try {
        final analyticsEntries = await _offlineStorage.getAnalyticsEntries();
        exportData['offline_data'] = {
          'analytics_entries': analyticsEntries,
          'sync_queue': await _offlineStorage.getSyncQueue(),
        };
      } catch (e) {
        // Continue if offline data export fails
      }

      // Get storage stats
      final stats = await _offlineStorage.getStorageStats();
      exportData['storage_stats'] = stats;

      // Convert to JSON
      final jsonString = const JsonEncoder.withIndent('  ').convert(exportData);

      // Save to file
      final directory = await getApplicationDocumentsDirectory();
      final file = File('${directory.path}/lifevault_export_${DateTime.now().millisecondsSinceEpoch}.json');
      await file.writeAsString(jsonString);

      // Share the file
      await Share.shareXFiles(
        [XFile(file.path)],
        text: 'LifeVault Data Export',
      );
    } catch (e) {
      rethrow;
    }
  }

  /// Export data as CSV (analytics only)
  Future<void> exportAnalyticsAsCsv() async {
    try {
      final analytics = await _analyticsService.getEntries();
      
      if (analytics.isEmpty) {
        throw Exception('No analytics data to export');
      }

      // Create CSV header
      final csvLines = <String>[];
      csvLines.add('Date,Category,Value,Notes');

      // Add data rows
      for (var entry in analytics) {
        final date = entry.timestamp.toIso8601String();
        final category = entry.category;
        final value = entry.value.toString();
        final notes = entry.notes ?? '';
        csvLines.add('$date,$category,$value,$notes');
      }

      final csvContent = csvLines.join('\n');

      // Save to file
      final directory = await getApplicationDocumentsDirectory();
      final file = File('${directory.path}/lifevault_analytics_${DateTime.now().millisecondsSinceEpoch}.csv');
      await file.writeAsString(csvContent);

      // Share the file
      await Share.shareXFiles(
        [XFile(file.path)],
        text: 'LifeVault Analytics Export',
      );
    } catch (e) {
      rethrow;
    }
  }
}

