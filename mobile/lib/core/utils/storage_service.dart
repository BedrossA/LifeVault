import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../config/app_config.dart';

class StorageService {
  static final StorageService _instance = StorageService._internal();
  factory StorageService() => _instance;
  StorageService._internal();

  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();
  SharedPreferences? _prefs;
  bool _initialized = false;

  Future<void> init() async {
    if (_initialized) return;
    _prefs = await SharedPreferences.getInstance();
    _initialized = true;
  }

  Future<void> _ensureInitialized() async {
    if (!_initialized) {
      await init();
    }
  }

  // Secure Storage (for tokens)
  Future<void> setAccessToken(String token) async {
    await _ensureInitialized();
    await _secureStorage.write(key: AppConfig.accessTokenKey, value: token);
  }

  Future<String?> getAccessToken() async {
    await _ensureInitialized();
    return await _secureStorage.read(key: AppConfig.accessTokenKey);
  }

  Future<void> setRefreshToken(String token) async {
    await _ensureInitialized();
    await _secureStorage.write(key: AppConfig.refreshTokenKey, value: token);
  }

  Future<String?> getRefreshToken() async {
    await _ensureInitialized();
    return await _secureStorage.read(key: AppConfig.refreshTokenKey);
  }

  Future<void> clearTokens() async {
    await _ensureInitialized();
    await _secureStorage.delete(key: AppConfig.accessTokenKey);
    await _secureStorage.delete(key: AppConfig.refreshTokenKey);
  }

  // Shared Preferences (for non-sensitive data)
  Future<void> setString(String key, String value) async {
    await _ensureInitialized();
    await _prefs?.setString(key, value);
  }

  String? getString(String key) {
    if (!_initialized) {
      throw StateError('StorageService not initialized. Call init() first.');
    }
    return _prefs?.getString(key);
  }

  Future<void> setBool(String key, bool value) async {
    await _ensureInitialized();
    await _prefs?.setBool(key, value);
  }

  bool? getBool(String key) {
    if (!_initialized) {
      throw StateError('StorageService not initialized. Call init() first.');
    }
    return _prefs?.getBool(key);
  }

  Future<void> setInt(String key, int value) async {
    await _ensureInitialized();
    await _prefs?.setInt(key, value);
  }

  int? getInt(String key) {
    if (!_initialized) {
      throw StateError('StorageService not initialized. Call init() first.');
    }
    return _prefs?.getInt(key);
  }

  Future<void> clear() async {  
    await _ensureInitialized();
    await _prefs?.clear();
    await _secureStorage.deleteAll();
  }

  // Biometric preference
  static const String biometricEnabledKey = 'biometric_enabled';
  static const String fcmTokenKey = 'fcm_token';
  static const String lastSyncTimeKey = 'last_sync_time';

  Future<void> setBiometricEnabled(bool enabled) async {
    await _ensureInitialized();
    await setBool(biometricEnabledKey, enabled);
  }

  bool? getBiometricEnabled() {
    if (!_initialized) {
      throw StateError('StorageService not initialized. Call init() first.');
    }
    return getBool(biometricEnabledKey);
  }

  // FCM Token
  Future<void> setFCMToken(String token) async {
    await _ensureInitialized();
    await setString(fcmTokenKey, token);
  }

  String? getFCMToken() {
    if (!_initialized) {
      throw StateError('StorageService not initialized. Call init() first.');
    }
    return getString(fcmTokenKey);
  }

  // Last sync time
  Future<void> setLastSyncTime(DateTime time) async {
    await _ensureInitialized();
    await setString(lastSyncTimeKey, time.toIso8601String());
  }

  DateTime? getLastSyncTime() {
    final timeString = getString(lastSyncTimeKey);
    if (timeString != null) {
      try {
        return DateTime.parse(timeString);
      } catch (e) {
        return null;
      }
    }
    return null;
  }

  // Enhanced secure storage methods
  Future<void> setSecureString(String key, String value) async {
    await _ensureInitialized();
    await _secureStorage.write(key: key, value: value);
  }

  Future<String?> getSecureString(String key) async {
    await _ensureInitialized();
    return await _secureStorage.read(key: key);
  }

  Future<void> deleteSecureString(String key) async {
    await _ensureInitialized();
    await _secureStorage.delete(key: key);
  }

  Future<Map<String, String>> getAllSecureData() async {
    await _ensureInitialized();
    return await _secureStorage.readAll();
  }
}

