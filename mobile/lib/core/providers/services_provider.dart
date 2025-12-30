import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/biometric_service.dart';
import '../services/offline_storage_service.dart';
import '../services/fcm_service.dart';
import '../services/background_sync_service.dart';
import '../services/camera_service.dart';
import '../utils/storage_service.dart';

// Storage Service Provider
final storageServiceProvider = Provider<StorageService>((ref) {
  return StorageService();
});

// Biometric Service Provider
final biometricServiceProvider = Provider<BiometricService>((ref) {
  return BiometricService();
});

// Offline Storage Service Provider
final offlineStorageServiceProvider = Provider<OfflineStorageService>((ref) {
  return OfflineStorageService();
});

// FCM Service Provider
final fcmServiceProvider = Provider<FCMService>((ref) {
  return FCMService();
});

// Background Sync Service Provider
final backgroundSyncServiceProvider = Provider<BackgroundSyncService>((ref) {
  return BackgroundSyncService();
});

// Camera Service Provider
final cameraServiceProvider = Provider<CameraService>((ref) {
  return CameraService();
});

