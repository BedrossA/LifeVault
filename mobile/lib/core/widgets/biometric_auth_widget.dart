import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:local_auth/local_auth.dart';
import '../providers/services_provider.dart';

/// Widget for biometric authentication
class BiometricAuthWidget extends ConsumerStatefulWidget {
  final String reason;
  final VoidCallback? onSuccess;
  final VoidCallback? onFailure;
  final Widget? child;

  const BiometricAuthWidget({
    super.key,
    this.reason = 'Please authenticate to continue',
    this.onSuccess,
    this.onFailure,
    this.child,
  });

  @override
  ConsumerState<BiometricAuthWidget> createState() => _BiometricAuthWidgetState();
}

class _BiometricAuthWidgetState extends ConsumerState<BiometricAuthWidget> {
  bool _isChecking = false;
  bool _isAvailable = false;
  List<BiometricType> _availableBiometrics = [];

  @override
  void initState() {
    super.initState();
    _checkAvailability();
  }

  Future<void> _checkAvailability() async {
    final biometricService = ref.read(biometricServiceProvider);
    final storage = ref.read(storageServiceProvider);

    final available = await biometricService.isAvailable();
    final biometricsEnabled = await storage.getBiometricEnabled() ?? false;

    if (mounted) {
      setState(() {
        _isAvailable = available && biometricsEnabled;
      });

      if (_isAvailable) {
        final biometrics = await biometricService.getAvailableBiometrics();
        setState(() {
          _availableBiometrics = biometrics;
        });
      }
    }
  }

  Future<void> _authenticate() async {
    if (!_isAvailable) return;

    setState(() => _isChecking = true);

    try {
      final biometricService = ref.read(biometricServiceProvider);
      final success = await biometricService.authenticate(
        reason: widget.reason,
      );

      if (mounted) {
        if (success) {
          widget.onSuccess?.call();
        } else {
          widget.onFailure?.call();
        }
      }
    } catch (e) {
      if (mounted) {
        widget.onFailure?.call();
      }
    } finally {
      if (mounted) {
        setState(() => _isChecking = false);
      }
    }
  }

  IconData _getBiometricIcon() {
    if (_availableBiometrics.contains(BiometricType.face)) {
      return Icons.face;
    } else if (_availableBiometrics.contains(BiometricType.fingerprint)) {
      return Icons.fingerprint;
    } else if (_availableBiometrics.contains(BiometricType.iris)) {
      return Icons.remove_red_eye;
    } else {
      return Icons.lock;
    }
  }

  String _getBiometricText() {
    if (_availableBiometrics.contains(BiometricType.face)) {
      return 'Face ID';
    } else if (_availableBiometrics.contains(BiometricType.fingerprint)) {
      return 'Fingerprint';
    } else if (_availableBiometrics.contains(BiometricType.iris)) {
      return 'Iris';
    } else {
      return 'Biometric';
    }
  }

  @override
  Widget build(BuildContext context) {
    if (!_isAvailable) {
      return widget.child ?? const SizedBox.shrink();
    }

    return widget.child != null
        ? GestureDetector(
            onTap: _isChecking ? null : _authenticate,
            child: widget.child,
          )
        : ElevatedButton.icon(
            onPressed: _isChecking ? null : _authenticate,
            icon: _isChecking
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : Icon(_getBiometricIcon()),
            label: Text(_isChecking ? 'Authenticating...' : _getBiometricText()),
          );
  }
}

/// Helper widget to show biometric authentication button
class BiometricAuthButton extends ConsumerWidget {
  final String reason;
  final VoidCallback? onSuccess;
  final VoidCallback? onFailure;

  const BiometricAuthButton({
    super.key,
    this.reason = 'Please authenticate to continue',
    this.onSuccess,
    this.onFailure,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return BiometricAuthWidget(
      reason: reason,
      onSuccess: onSuccess,
      onFailure: onFailure,
      child: ElevatedButton.icon(
        onPressed: null, // Handled by BiometricAuthWidget
        icon: const Icon(Icons.fingerprint),
        label: const Text('Use Biometric'),
      ),
    );
  }
}

