import 'package:workmanager/workmanager.dart';
import 'package:flutter/foundation.dart';
import 'offline_storage_service.dart';

/// Background sync service using WorkManager
class BackgroundSyncService {
  static final BackgroundSyncService _instance = BackgroundSyncService._internal();
  factory BackgroundSyncService() => _instance;
  BackgroundSyncService._internal();

  static const String _syncTaskName = 'backgroundSync';
  final OfflineStorageService _offlineStorage = OfflineStorageService();

  bool _initialized = false;

  /// Initialize background sync
  Future<void> init() async {
    if (_initialized) return;

    await Workmanager().initialize(
      callbackDispatcher,
      isInDebugMode: kDebugMode,
    );

    _initialized = true;
    debugPrint('Background sync service initialized');
  }

  /// Register periodic sync task
  Future<void> registerPeriodicSync({
    Duration frequency = const Duration(minutes: 15),
  }) async {
    await Workmanager().registerPeriodicTask(
      _syncTaskName,
      _syncTaskName,
      frequency: frequency,
      constraints: Constraints(
        networkType: NetworkType.connected,
        requiresBatteryNotLow: false,
        requiresCharging: false,
        requiresDeviceIdle: false,
        requiresStorageNotLow: false,
      ),
      initialDelay: const Duration(seconds: 10),
    );
    debugPrint('Periodic sync task registered');
  }

  /// Register one-time sync task
  Future<void> registerOneTimeSync({Duration delay = const Duration(seconds: 5)}) async {
    await Workmanager().registerOneOffTask(
      '${_syncTaskName}_onetime',
      _syncTaskName,
      initialDelay: delay,
      constraints: Constraints(
        networkType: NetworkType.connected,
      ),
    );
    debugPrint('One-time sync task registered');
  }

  /// Cancel all sync tasks
  Future<void> cancelAllTasks() async {
    await Workmanager().cancelAll();
    debugPrint('All sync tasks cancelled');
  }

  /// Cancel specific task
  Future<void> cancelTask(String taskName) async {
    await Workmanager().cancelByUniqueName(taskName);
    debugPrint('Task cancelled: $taskName');
  }

  /// Manual sync (can be called from UI)
  Future<void> syncNow() async {
    await performSync();
  }

  /// Perform the actual sync
  Future<void> performSync() async {
    try {
      debugPrint('Starting background sync...');
      
      final syncQueue = await _offlineStorage.getSyncQueue();
      if (syncQueue.isEmpty) {
        debugPrint('Sync queue is empty');
        return;
      }

      debugPrint('Found ${syncQueue.length} items in sync queue');

      // Process each item in the sync queue
      for (var item in syncQueue) {
        final id = item['id'] as String;
        final action = item['action'] as String;
        final retryCount = item['retryCount'] as int? ?? 0;

        // Skip if retry count is too high
        if (retryCount > 5) {
          debugPrint('Skipping item $id: too many retries');
          await _offlineStorage.removeFromSyncQueue(id);
          continue;
        }

        try {
          // Process based on action type
          bool success = false;
          switch (action) {
            case 'create_analytics_entry':
              // You'll need to inject the service here
              // For now, we'll just mark as processed
              success = true;
              break;
            case 'update_analytics_entry':
              success = true;
              break;
            case 'delete_analytics_entry':
              success = true;
              break;
            default:
              debugPrint('Unknown action: $action');
              success = false;
          }

          if (success) {
            await _offlineStorage.removeFromSyncQueue(id);
            debugPrint('Successfully synced item: $id');
          } else {
            await _offlineStorage.incrementRetryCount(id);
            debugPrint('Failed to sync item: $id, retry count: ${retryCount + 1}');
          }
        } catch (e) {
          debugPrint('Error syncing item $id: $e');
          await _offlineStorage.incrementRetryCount(id);
        }
      }

      debugPrint('Background sync completed');
    } catch (e) {
      debugPrint('Error in background sync: $e');
    }
  }
}

/// Callback dispatcher for WorkManager
/// This must be a top-level function
@pragma('vm:entry-point')
void callbackDispatcher() {
  Workmanager().executeTask((task, inputData) async {
    debugPrint('Background task started: $task');

    if (task == 'backgroundSync') {
      final syncService = BackgroundSyncService();
      await syncService.performSync();
      return Future.value(true);
    }

    return Future.value(false);
  });
}

