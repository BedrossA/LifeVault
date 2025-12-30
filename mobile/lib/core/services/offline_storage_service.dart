import 'package:hive_flutter/hive_flutter.dart';
import 'dart:convert';

/// Service for offline data storage using Hive
class OfflineStorageService {
  static final OfflineStorageService _instance = OfflineStorageService._internal();
  factory OfflineStorageService() => _instance;
  OfflineStorageService._internal();

  static const String _analyticsBoxName = 'analytics';
  static const String _faceDataBoxName = 'face_data';
  static const String _syncQueueBoxName = 'sync_queue';
  static const String _cacheBoxName = 'cache';

  bool _initialized = false;

  /// Initialize Hive and open boxes
  Future<void> init() async {
    if (_initialized) return;

    await Hive.initFlutter();
    
    // Open boxes
    await Hive.openBox(_analyticsBoxName);
    await Hive.openBox(_faceDataBoxName);
    await Hive.openBox(_syncQueueBoxName);
    await Hive.openBox(_cacheBoxName);

    _initialized = true;
  }

  // Analytics Storage
  Future<void> saveAnalyticsEntry(Map<String, dynamic> entry) async {
    final box = Hive.box(_analyticsBoxName);
    final id = entry['id'] ?? DateTime.now().millisecondsSinceEpoch.toString();
    await box.put(id, jsonEncode(entry));
  }

  Future<List<Map<String, dynamic>>> getAnalyticsEntries() async {
    final box = Hive.box(_analyticsBoxName);
    final entries = <Map<String, dynamic>>[];
    
    for (var key in box.keys) {
      final value = box.get(key);
      if (value != null) {
        try {
          entries.add(jsonDecode(value as String) as Map<String, dynamic>);
        } catch (e) {
          // Skip invalid entries
        }
      }
    }
    
    return entries;
  }

  Future<void> deleteAnalyticsEntry(String id) async {
    final box = Hive.box(_analyticsBoxName);
    await box.delete(id);
  }

  // Face Data Storage
  Future<void> saveFaceData(String userId, Map<String, dynamic> faceData) async {
    final box = Hive.box(_faceDataBoxName);
    await box.put(userId, jsonEncode(faceData));
  }

  Future<Map<String, dynamic>?> getFaceData(String userId) async {
    final box = Hive.box(_faceDataBoxName);
    final value = box.get(userId);
    if (value != null) {
      try {
        return jsonDecode(value as String) as Map<String, dynamic>;
      } catch (e) {
        return null;
      }
    }
    return null;
  }

  Future<void> deleteFaceData(String userId) async {
    final box = Hive.box(_faceDataBoxName);
    await box.delete(userId);
  }

  // Sync Queue (for background sync)
  Future<void> addToSyncQueue(String action, Map<String, dynamic> data) async {
    final box = Hive.box(_syncQueueBoxName);
    final item = {
      'id': DateTime.now().millisecondsSinceEpoch.toString(),
      'action': action,
      'data': data,
      'timestamp': DateTime.now().toIso8601String(),
      'retryCount': 0,
    };
    await box.put(item['id'], jsonEncode(item));
  }

  Future<List<Map<String, dynamic>>> getSyncQueue() async {
    final box = Hive.box(_syncQueueBoxName);
    final items = <Map<String, dynamic>>[];
    
    for (var key in box.keys) {
      final value = box.get(key);
      if (value != null) {
        try {
          items.add(jsonDecode(value as String) as Map<String, dynamic>);
        } catch (e) {
          // Skip invalid entries
        }
      }
    }
    
    // Sort by timestamp
    items.sort((a, b) {
      final aTime = a['timestamp'] as String? ?? '';
      final bTime = b['timestamp'] as String? ?? '';
      return aTime.compareTo(bTime);
    });
    
    return items;
  }

  Future<void> removeFromSyncQueue(String id) async {
    final box = Hive.box(_syncQueueBoxName);
    await box.delete(id);
  }

  Future<void> incrementRetryCount(String id) async {
    final box = Hive.box(_syncQueueBoxName);
    final value = box.get(id);
    if (value != null) {
      try {
        final item = jsonDecode(value as String) as Map<String, dynamic>;
        item['retryCount'] = (item['retryCount'] as int? ?? 0) + 1;
        await box.put(id, jsonEncode(item));
      } catch (e) {
        // Handle error
      }
    }
  }

  Future<void> clearSyncQueue() async {
    final box = Hive.box(_syncQueueBoxName);
    await box.clear();
  }

  // Cache Storage
  Future<void> cacheData(String key, Map<String, dynamic> data, {Duration? ttl}) async {
    final box = Hive.box(_cacheBoxName);
    final cacheItem = {
      'data': data,
      'timestamp': DateTime.now().toIso8601String(),
      'ttl': ttl?.inSeconds,
    };
    await box.put(key, jsonEncode(cacheItem));
  }

  Future<Map<String, dynamic>?> getCachedData(String key) async {
    final box = Hive.box(_cacheBoxName);
    final value = box.get(key);
    if (value != null) {
      try {
        final cacheItem = jsonDecode(value as String) as Map<String, dynamic>;
        final timestamp = DateTime.parse(cacheItem['timestamp'] as String);
        final ttl = cacheItem['ttl'] as int?;
        
        if (ttl != null) {
          final expiry = timestamp.add(Duration(seconds: ttl));
          if (DateTime.now().isAfter(expiry)) {
            await box.delete(key);
            return null;
          }
        }
        
        return cacheItem['data'] as Map<String, dynamic>?;
      } catch (e) {
        return null;
      }
    }
    return null;
  }

  Future<void> clearCache() async {
    final box = Hive.box(_cacheBoxName);
    await box.clear();
  }

  // Clear all offline data
  Future<void> clearAll() async {
    await Hive.box(_analyticsBoxName).clear();
    await Hive.box(_faceDataBoxName).clear();
    await Hive.box(_syncQueueBoxName).clear();
    await Hive.box(_cacheBoxName).clear();
  }

  // Get storage statistics
  Future<Map<String, int>> getStorageStats() async {
    return {
      'analytics': Hive.box(_analyticsBoxName).length,
      'face_data': Hive.box(_faceDataBoxName).length,
      'sync_queue': Hive.box(_syncQueueBoxName).length,
      'cache': Hive.box(_cacheBoxName).length,
    };
  }
}

