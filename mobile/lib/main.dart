import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'core/config/app_config.dart';
import 'core/network/api_client.dart';
import 'core/utils/storage_service.dart';
import 'core/navigation/app_router.dart';
import 'core/providers/theme_provider.dart';
import 'core/theme/app_theme.dart';
import 'core/services/offline_storage_service.dart';
import 'core/services/fcm_service.dart' show FCMService, firebaseMessagingBackgroundHandler;
import 'core/services/background_sync_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Firebase (if using FCM)
  try {
    await Firebase.initializeApp();
    // Set up background message handler
    FirebaseMessaging.onBackgroundMessage(firebaseMessagingBackgroundHandler);
  } catch (e) {
    debugPrint('Firebase initialization error: $e');
    // Continue without Firebase if initialization fails
  }

  // Initialize services
  await StorageService().init();
  await OfflineStorageService().init();
  await ApiClient().init();

  // Initialize FCM service
  try {
    await FCMService().init();
  } catch (e) {
    debugPrint('FCM initialization error: $e');
    // Continue without FCM if initialization fails
  }

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

