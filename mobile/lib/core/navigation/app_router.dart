import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../features/auth/providers/auth_provider.dart';
import '../../features/auth/pages/login_page.dart';
import '../../features/auth/pages/register_page.dart';
import '../../features/home/pages/home_page.dart';
import '../../features/dashboard/pages/dashboard_page.dart';
import '../../features/analytics/pages/analytics_page.dart';
import '../../features/face/pages/face_recognition_page.dart';
import '../../features/profile/pages/profile_page.dart';
import '../../features/settings/pages/settings_page.dart';
import '../../features/auth/pages/login_history_page.dart';
import '../../features/auth/pages/activity_page.dart';
import '../constants/app_constants.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authProvider);

  return GoRouter(
    initialLocation: AppConstants.routeSplash,
    redirect: (context, state) {
     // Wait for auth to initialize
      if (authState.isLoading) {
        return AppConstants.routeSplash;
      }

      final isAuthenticated = authState.isAuthenticated;
      final isLoggingIn = state.matchedLocation == AppConstants.routeLogin ||
          state.matchedLocation == AppConstants.routeRegister;
      final isSplash = state.matchedLocation == AppConstants.routeSplash;
      // If not authenticated and trying to access protected route
      if (!isAuthenticated && !isLoggingIn && !isSplash) {
        return AppConstants.routeLogin;
      }

      // If authenticated and trying to access auth pages
      if (isAuthenticated && (isLoggingIn || isSplash)) {
        return AppConstants.routeHome;
      }

      return null;
    },
    routes: [
      GoRoute(
        path: AppConstants.routeSplash,
        builder: (context, state) => const SplashPage(),
      ),
      GoRoute(
        path: AppConstants.routeLogin,
        builder: (context, state) => const LoginPage(),
      ),
      GoRoute(
        path: AppConstants.routeRegister,
        builder: (context, state) => const RegisterPage(),
      ),
      GoRoute(
        path: '/login-history',
        builder: (context, state) => const LoginHistoryPage(),
      ),
      GoRoute(
        path: '/activity',
        builder: (context, state) => const ActivityPage(),
      ),
      GoRoute(
        path: AppConstants.routeHome,
        builder: (context, state) => const HomePage(),
        routes: [
          GoRoute(
            path: 'dashboard',
            builder: (context, state) => const DashboardPage(),
          ),
          GoRoute(
            path: 'analytics',
            builder: (context, state) => const AnalyticsPage(),
          ),
          GoRoute(
            path: 'face-recognition',
            builder: (context, state) => const FaceRecognitionPage(),
          ),
          GoRoute(
            path: 'profile',
            builder: (context, state) => const ProfilePage(),
          ),
          GoRoute(
            path: 'settings',
            builder: (context, state) => const SettingsPage(),
          ),
        ],
      ),
    ],
  );
});

class SplashPage extends ConsumerWidget {
  const SplashPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);

    // Wait for auth check to complete
    if (authState.isLoading) {
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    // Navigate based on auth status
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (authState.isAuthenticated) {
        context.go(AppConstants.routeHome);
      } else {
        context.go(AppConstants.routeLogin);
      }
    });

    return const Scaffold(
      body: Center(
        child: CircularProgressIndicator(),
      ),
    );
  }
}

