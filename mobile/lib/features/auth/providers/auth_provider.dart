import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/auth_models.dart';
import '../services/auth_api_service.dart';
import '../../../core/utils/storage_service.dart';

final authApiServiceProvider = Provider<AuthApiService>((ref) {
  return AuthApiService();
});

final storageServiceProvider = Provider<StorageService>((ref) {
  return StorageService();
});

class AuthState {
  final User? user;
  final bool isLoading;
  final String? error;
  final bool isAuthenticated;

  AuthState({
    this.user,
    this.isLoading = false,
    this.error,
    this.isAuthenticated = false,
  });

  AuthState copyWith({
    User? user,
    bool? isLoading,
    String? error,
    bool? isAuthenticated,
  }) {
    return AuthState(
      user: user ?? this.user,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  final AuthApiService _authService;
  final StorageService _storage;
  bool _initialized = false;
  
  AuthNotifier(this._authService, this._storage)
      : super(AuthState(isLoading: true)) {
    _checkAuthStatus();
  }

  Future<void> _checkAuthStatus() async {
    try {
      final token = await _storage.getAccessToken();
      if (token != null) {
        try {
          final user = await _authService.getCurrentUser();
          state = state.copyWith(
            user: user,
            isAuthenticated: true,
            isLoading: false,
          );
        } catch (e) {
          await _storage.clearTokens();
          state = state.copyWith(
            isAuthenticated: false,
            isLoading: false,
          );
        }
      } else {
        state = state.copyWith(
          isAuthenticated: false,
          isLoading: false,
        );
      }
    } catch (e) {
      state = state.copyWith(
        isAuthenticated: false,
        isLoading: false,
        error: e.toString(),
      );
    } finally {
      _initialized = true;
    }
  }

  Future<bool> login(String username, String password) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final request = LoginRequest(username: username, password: password);
      final tokenResponse = await _authService.login(request);

      await _storage.setAccessToken(tokenResponse.accessToken);
      await _storage.setRefreshToken(tokenResponse.refreshToken);

      final user = await _authService.getCurrentUser();
      state = state.copyWith(
        user: user,
        isAuthenticated: true,
        isLoading: false,
      );
      return true;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
        isAuthenticated: false,
      );
      return false;
    }
  }

  Future<bool> register(String username, String email, String password) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final request = RegisterRequest(
        username: username,
        email: email,
        password: password,
      );
      await _authService.register(request);

      // Auto-login after registration
      return await login(username, password);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
      return false;
    }
  }

  Future<void> logout() async {
    state = state.copyWith(isLoading: true);
    try {
      await _authService.logout();
    } catch (e) {
      // Continue with logout even if API call fails
    } finally {
      await _storage.clearTokens();
      state = AuthState(isAuthenticated: false);
    }
  }

  Future<void> refreshUser() async {
    try {
      final user = await _authService.getCurrentUser();
      state = state.copyWith(user: user);
    } catch (e) {
      // Handle error silently or update state
    }
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  final authService = ref.watch(authApiServiceProvider);
  final storage = ref.watch(storageServiceProvider);
  return AuthNotifier(authService, storage);
});

