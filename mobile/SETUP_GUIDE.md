# LifeVault Mobile - Feature Setup Guide

This guide will help you set up all the new features that have been implemented.

## ✅ Implemented Features

1. ✅ **Local Authentication (Biometric)** - Face ID, Fingerprint, etc.
2. ✅ **Secure Storage** - Enhanced flutter_secure_storage
3. ✅ **Offline Support** - Hive database for local storage
4. ✅ **Push Notifications** - Firebase Cloud Messaging (FCM)
5. ✅ **Camera Integration** - Enhanced camera service
6. ✅ **Background Sync** - WorkManager for background tasks

## 📦 Dependencies Added

The following packages have been added to `pubspec.yaml`:

- `local_auth: ^2.1.7` - Biometric authentication
- `hive: ^2.2.3` - Local database
- `hive_flutter: ^1.1.0` - Hive Flutter integration
- `firebase_core: ^2.24.2` - Firebase core
- `firebase_messaging: ^14.7.10` - Push notifications
- `workmanager: ^0.5.2` - Background tasks

## 🔧 Installation Steps

### 1. Install Dependencies

```bash
cd mobile
flutter pub get
```

### 2. Firebase Setup (Required for Push Notifications)

#### Android:
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select existing one
3. Add Android app with package name from `android/app/build.gradle`
4. Download `google-services.json`
5. Place it in `android/app/`
6. Update `android/build.gradle`:
   ```gradle
   dependencies {
       classpath 'com.google.gms:google-services:4.4.0'
   }
   ```
7. Update `android/app/build.gradle`:
   ```gradle
   apply plugin: 'com.google.gms.google-services'
   ```

#### iOS:
1. In Firebase Console, add iOS app with bundle ID
2. Download `GoogleService-Info.plist`
3. Place it in `ios/Runner/`
4. Open `ios/Runner.xcworkspace` in Xcode
5. Add `GoogleService-Info.plist` to Runner target

### 3. Android Permissions

Add to `android/app/src/main/AndroidManifest.xml`:

```xml
<manifest>
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.CAMERA"/>
    <uses-permission android:name="android.permission.USE_BIOMETRIC"/>
    <uses-permission android:name="android.permission.USE_FINGERPRINT"/>
    <uses-permission android:name="android.permission.WAKE_LOCK"/>
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>
    
    <application>
        <!-- Your existing application config -->
    </application>
</manifest>
```

### 4. iOS Permissions

Add to `ios/Runner/Info.plist`:

```xml
<key>NSFaceIDUsageDescription</key>
<string>We need to use Face ID to authenticate you securely</string>

<key>NSCameraUsageDescription</key>
<string>We need access to your camera to take photos for face recognition</string>

<key>UIBackgroundModes</key>
<array>
    <string>remote-notification</string>
    <string>fetch</string>
</array>
```

### 5. iOS Background Tasks

For background sync to work on iOS, you need to enable background modes:

1. Open `ios/Runner.xcworkspace` in Xcode
2. Select Runner target
3. Go to "Signing & Capabilities"
4. Add "Background Modes"
5. Enable "Background fetch" and "Remote notifications"

## 🚀 Usage Examples

### Biometric Authentication

```dart
import 'package:lifevault/core/providers/services_provider.dart';
import 'package:lifevault/core/widgets/biometric_auth_widget.dart';

// In your widget
final biometricService = ref.read(biometricServiceProvider);
final isAvailable = await biometricService.isAvailable();

if (isAvailable) {
  final success = await biometricService.authenticate(
    reason: 'Please authenticate to continue',
  );
  
  if (success) {
    // User authenticated successfully
  }
}

// Or use the widget
BiometricAuthButton(
  reason: 'Login with biometric',
  onSuccess: () {
    // Navigate to home
  },
)
```

### Offline Storage

```dart
import 'package:lifevault/core/providers/services_provider.dart';

final offlineStorage = ref.read(offlineStorageServiceProvider);

// Save data offline
await offlineStorage.saveAnalyticsEntry({
  'id': '123',
  'value': 'data',
});

// Get offline data
final entries = await offlineStorage.getAnalyticsEntries();

// Add to sync queue
await offlineStorage.addToSyncQueue('create_analytics_entry', {
  'data': 'value',
});
```

### Push Notifications

```dart
import 'package:lifevault/core/providers/services_provider.dart';

final fcmService = ref.read(fcmServiceProvider);

// Get FCM token (already initialized in main.dart)
final token = await fcmService.getSavedFCMToken();

// Subscribe to topic
await fcmService.subscribeToTopic('user_updates');
```

### Camera Service

```dart
import 'package:lifevault/core/providers/services_provider.dart';

final cameraService = ref.read(cameraServiceProvider);

// Initialize
final initialized = await cameraService.initialize();

if (initialized) {
  // Take picture
  final imageFile = await cameraService.takePicture();
  
  // Get controller for preview
  final controller = cameraService.controller;
  if (controller != null) {
    // Use CameraPreview(controller)
  }
}
```

### Background Sync

```dart
import 'package:lifevault/core/providers/services_provider.dart';

final syncService = ref.read(backgroundSyncServiceProvider);

// Manual sync
await syncService.syncNow();

// The service is already set up for periodic sync in main.dart
```

## 📝 Service Providers

All services are available through Riverpod providers:

```dart
// Biometric Service
final biometricService = ref.read(biometricServiceProvider);

// Storage Service
final storage = ref.read(storageServiceProvider);

// Offline Storage Service
final offlineStorage = ref.read(offlineStorageServiceProvider);

// FCM Service
final fcmService = ref.read(fcmServiceProvider);

// Background Sync Service
final syncService = ref.read(backgroundSyncServiceProvider);

// Camera Service
final cameraService = ref.read(cameraServiceProvider);
```

## 🔍 Testing

### Test Biometric Authentication
1. Run the app on a physical device (emulators don't support biometrics)
2. Enable biometric authentication in settings
3. Try to authenticate using biometric

### Test Offline Storage
1. Put device in airplane mode
2. Create some data
3. Check that it's saved locally
4. Re-enable network
5. Data should sync automatically

### Test Push Notifications
1. Get FCM token from logs
2. Send test notification from Firebase Console
3. Verify notification is received

### Test Background Sync
1. Add items to sync queue
2. Close the app
3. Wait for background sync (15 minutes default)
4. Check that data was synced

## ⚠️ Important Notes

1. **Firebase is optional**: The app will continue to work without Firebase, but push notifications won't function.

2. **Biometric requires physical device**: Emulators don't support biometric authentication.

3. **Background sync frequency**: Default is 15 minutes. You can adjust this in `main.dart`.

4. **Permissions**: Make sure all required permissions are granted before using features.

5. **iOS Background Modes**: Required for background sync to work on iOS.

## 🐛 Troubleshooting

### Firebase not initializing
- Check that `google-services.json` (Android) or `GoogleService-Info.plist` (iOS) is in the correct location
- Verify Firebase project configuration

### Biometric not working
- Ensure you're testing on a physical device
- Check that biometric is enabled in device settings
- Verify permissions in AndroidManifest.xml / Info.plist

### Background sync not working
- Check that WorkManager permissions are granted
- Verify background modes are enabled (iOS)
- Check logs for error messages

### Camera not working
- Verify camera permission is granted
- Check that camera is not being used by another app
- Ensure you're testing on a physical device (some emulators don't support camera)

## 📚 Additional Resources

- [Local Auth Package](https://pub.dev/packages/local_auth)
- [Hive Package](https://pub.dev/packages/hive)
- [Firebase Messaging](https://firebase.google.com/docs/cloud-messaging)
- [WorkManager](https://pub.dev/packages/workmanager)

