# Core Services Documentation

This document describes the core services available in the LifeVault mobile application.

## Services Overview

### 1. Biometric Service (`biometric_service.dart`)

Provides biometric authentication using device capabilities (Face ID, Fingerprint, etc.).

**Usage:**
```dart
final biometricService = BiometricService();

// Check if biometric is available
final isAvailable = await biometricService.isAvailable();

// Get available biometric types
final types = await biometricService.getAvailableBiometrics();

// Authenticate
final success = await biometricService.authenticate(
  reason: 'Please authenticate to continue',
);
```

**Provider:**
```dart
final biometricService = ref.read(biometricServiceProvider);
```

### 2. Secure Storage Service (`storage_service.dart`)

Enhanced secure storage using `flutter_secure_storage` for sensitive data.

**Usage:**
```dart
final storage = StorageService();

// Store tokens
await storage.setAccessToken('token');
await storage.setRefreshToken('refresh_token');

// Store FCM token
await storage.setFCMToken('fcm_token');

// Store any secure string
await storage.setSecureString('key', 'value');
final value = await storage.getSecureString('key');
```

**Provider:**
```dart
final storage = ref.read(storageServiceProvider);
```

### 3. Offline Storage Service (`offline_storage_service.dart`)

Local database storage using Hive for offline support.

**Usage:**
```dart
final offlineStorage = OfflineStorageService();
await offlineStorage.init();

// Save analytics entry
await offlineStorage.saveAnalyticsEntry({
  'id': '123',
  'data': 'value',
});

// Get analytics entries
final entries = await offlineStorage.getAnalyticsEntries();

// Add to sync queue
await offlineStorage.addToSyncQueue('create_analytics_entry', {
  'data': 'value',
});

// Get sync queue
final queue = await offlineStorage.getSyncQueue();
```

**Provider:**
```dart
final offlineStorage = ref.read(offlineStorageServiceProvider);
```

### 4. FCM Service (`fcm_service.dart`)

Firebase Cloud Messaging for push notifications.

**Usage:**
```dart
final fcmService = FCMService();
await fcmService.init();

// Get FCM token
final token = await fcmService.getSavedFCMToken();

// Subscribe to topic
await fcmService.subscribeToTopic('user_updates');

// Unsubscribe from topic
await fcmService.unsubscribeFromTopic('user_updates');
```

**Provider:**
```dart
final fcmService = ref.read(fcmServiceProvider);
```

**Note:** FCM requires Firebase configuration. Make sure to:
1. Add `google-services.json` (Android) to `android/app/`
2. Add `GoogleService-Info.plist` (iOS) to `ios/Runner/`
3. Configure Firebase in your project

### 5. Background Sync Service (`background_sync_service.dart`)

Handles background synchronization of offline data.

**Usage:**
```dart
final syncService = BackgroundSyncService();
await syncService.init();

// Register periodic sync (every 15 minutes)
await syncService.registerPeriodicSync();

// Register one-time sync
await syncService.registerOneTimeSync();

// Manual sync
await syncService.syncNow();

// Cancel all tasks
await syncService.cancelAllTasks();
```

**Provider:**
```dart
final syncService = ref.read(backgroundSyncServiceProvider);
```

### 6. Camera Service (`camera_service.dart`)

Enhanced camera service with better error handling and features.

**Usage:**
```dart
final cameraService = CameraService();

// Check permission
final hasPermission = await cameraService.checkPermission();

// Initialize camera
final initialized = await cameraService.initialize(
  resolution: ResolutionPreset.high,
  cameraIndex: 0,
);

// Take picture
final imageFile = await cameraService.takePicture();

// Switch camera
await cameraService.switchCamera();

// Set flash mode
await cameraService.setFlashMode(FlashMode.auto);

// Get controller for preview
final controller = cameraService.controller;
```

**Provider:**
```dart
final cameraService = ref.read(cameraServiceProvider);
```

## Widgets

### BiometricAuthWidget

A widget that provides biometric authentication UI.

**Usage:**
```dart
BiometricAuthWidget(
  reason: 'Please authenticate to continue',
  onSuccess: () {
    // Handle success
  },
  onFailure: () {
    // Handle failure
  },
  child: ElevatedButton(
    onPressed: null,
    child: Text('Authenticate'),
  ),
)
```

Or use the button directly:
```dart
BiometricAuthButton(
  reason: 'Please authenticate',
  onSuccess: () => Navigator.push(...),
)
```

## Integration Example

Here's how to integrate biometric authentication in a login page:

```dart
class LoginPage extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final storage = ref.read(storageServiceProvider);
    final biometricService = ref.read(biometricServiceProvider);
    
    return Scaffold(
      body: Column(
        children: [
          // Regular login form
          TextField(...),
          ElevatedButton(
            onPressed: () async {
              // Login logic
            },
            child: Text('Login'),
          ),
          
          // Biometric login
          FutureBuilder<bool>(
            future: storage.getBiometricEnabled(),
            builder: (context, snapshot) {
              if (snapshot.data == true) {
                return BiometricAuthButton(
                  reason: 'Login with biometric',
                  onSuccess: () {
                    // Navigate to home
                  },
                );
              }
              return SizedBox.shrink();
            },
          ),
        ],
      ),
    );
  }
}
```

## Android Configuration

### For WorkManager (Background Sync)

Add to `android/app/src/main/AndroidManifest.xml`:
```xml
<uses-permission android:name="android.permission.INTERNET"/>
<uses-permission android:name="android.permission.WAKE_LOCK"/>
```

### For Biometric Authentication

Add to `android/app/src/main/AndroidManifest.xml`:
```xml
<uses-permission android:name="android.permission.USE_BIOMETRIC"/>
<uses-permission android:name="android.permission.USE_FINGERPRINT"/>
```

### For Camera

Add to `android/app/src/main/AndroidManifest.xml`:
```xml
<uses-permission android:name="android.permission.CAMERA"/>
```

## iOS Configuration

### For Biometric Authentication

Add to `ios/Runner/Info.plist`:
```xml
<key>NSFaceIDUsageDescription</key>
<string>We need to use Face ID to authenticate you</string>
```

### For Camera

Add to `ios/Runner/Info.plist`:
```xml
<key>NSCameraUsageDescription</key>
<string>We need access to your camera to take photos</string>
```

### For Push Notifications

Enable Push Notifications capability in Xcode and add:
```xml
<key>UIBackgroundModes</key>
<array>
    <string>remote-notification</string>
</array>
```

