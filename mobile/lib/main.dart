import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'core/config/app_config.dart';
import 'core/network/api_client.dart';
import 'core/config/feature_flags.dart';
import 'core/utils/storage_service.dart';
import 'core/navigation/app_router.dart';
import 'core/providers/theme_provider.dart';
import 'core/theme/app_theme.dart';
import 'core/services/offline_storage_service.dart';
import 'core/services/fcm_service.dart' show FCMService, firebaseMessagingBackgroundHandler;
import 'core/services/background_sync_service.dart';
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  if (FeatureFlags.enablePushNotifications) {
    // Initialize Firebase (if using FCM)
    try {
      await Firebase.initializeApp();
      // Only set up messaging if Firebase initialized successfully
      FirebaseMessaging.onBackgroundMessage(firebaseMessagingBackgroundHandler);

      // Initialize FCM service
      await FCMService().init();
      debugPrint('Firebase services initialized successfully');
    } catch (e) {
      debugPrint('Firebase initialization error: $e');
      debugPrint('App will continue without push notifications');
      // Don't try to initialize FCM if Firebase failed
    }
  }
  // Initialize services
  await StorageService().init();
  await OfflineStorageService().init();
  await ApiClient().init();

  // Initialize background sync service
  try {
    await BackgroundSyncService().init();
    // Register periodic sync (every 15 minutes)
    await BackgroundSyncService().registerPeriodicSync();
  } catch (e) {
    debugPrint('Background sync initialization error: $e');
    // Continue without background sync if initialization fails
  }

  runApp(
    const ProviderScope(
      child: LifeVaultApp(),
    ),
  );
}

class LifeVaultApp extends ConsumerWidget {
  const LifeVaultApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);
    final themeMode = ref.watch(themeModeProvider);

    return MaterialApp.router(
      title: AppConfig.appName,
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: themeMode,
      routerConfig: router,
    );
  }
}
