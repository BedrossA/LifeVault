import 'package:camera/camera.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:flutter/foundation.dart';
import 'dart:io';

/// Enhanced camera service with better error handling
class CameraService {
  static final CameraService _instance = CameraService._internal();
  factory CameraService() => _instance;
  CameraService._internal();

  CameraController? _controller;
  List<CameraDescription>? _cameras;
  bool _isInitialized = false;
  int _currentCameraIndex = 0;

  /// Get available cameras
  Future<List<CameraDescription>> getAvailableCameras() async {
    try {
      _cameras = await availableCameras();
      return _cameras ?? [];
    } catch (e) {
      debugPrint('Error getting cameras: $e');
      return [];
    }
  }

  /// Check camera permission
  Future<bool> checkPermission() async {
    if (Platform.isAndroid) {
      final status = await Permission.camera.status;
      if (status.isDenied) {
        final result = await Permission.camera.request();
        return result.isGranted;
      }
      return status.isGranted;
    } else if (Platform.isIOS) {
      final status = await Permission.camera.status;
      if (status.isDenied) {
        final result = await Permission.camera.request();
        return result.isGranted;
      }
      return status.isGranted;
    }
    return false;
  }

  /// Initialize camera
  Future<bool> initialize({
    ResolutionPreset resolution = ResolutionPreset.medium,
    int cameraIndex = 0,
    bool enableAudio = false,
  }) async {
    try {
      // Check permission first
      final hasPermission = await checkPermission();
      if (!hasPermission) {
        debugPrint('Camera permission denied');
        return false;
      }

      // Get available cameras
      _cameras = await getAvailableCameras();
      if (_cameras == null || _cameras!.isEmpty) {
        debugPrint('No cameras available');
        return false;
      }

      // Validate camera index
      if (cameraIndex >= _cameras!.length) {
        cameraIndex = 0;
      }

      _currentCameraIndex = cameraIndex;

      // Dispose existing controller if any
      await dispose();

      // Create new controller
      _controller = CameraController(
        _cameras![_currentCameraIndex],
        resolution,
        enableAudio: enableAudio,
        imageFormatGroup: ImageFormatGroup.jpeg,
      );

      // Initialize controller
      await _controller!.initialize();
      _isInitialized = true;

      debugPrint('Camera initialized successfully');
      return true;
    } catch (e) {
      debugPrint('Error initializing camera: $e');
      _isInitialized = false;
      return false;
    }
  }

  /// Switch between front and back camera
  Future<bool> switchCamera() async {
    if (_cameras == null || _cameras!.length < 2) {
      return false;
    }

    _currentCameraIndex = (_currentCameraIndex + 1) % _cameras!.length;
    return await initialize(cameraIndex: _currentCameraIndex);
  }

  /// Take a picture
  Future<XFile?> takePicture() async {
    if (!_isInitialized || _controller == null) {
      debugPrint('Camera not initialized');
      return null;
    }

    if (!_controller!.value.isInitialized) {
      debugPrint('Camera controller not initialized');
      return null;
    }

    if (_controller!.value.isTakingPicture) {
      debugPrint('Camera is already taking a picture');
      return null;
    }

    try {
      final XFile file = await _controller!.takePicture();
      debugPrint('Picture taken: ${file.path}');
      return file;
    } catch (e) {
      debugPrint('Error taking picture: $e');
      return null;
    }
  }

  /// Start video recording
  Future<bool> startVideoRecording() async {
    if (!_isInitialized || _controller == null) {
      return false;
    }

    if (!_controller!.value.isInitialized) {
      return false;
    }

    if (_controller!.value.isRecordingVideo) {
      return false;
    }

    try {
      await _controller!.startVideoRecording();
      return true;
    } catch (e) {
      debugPrint('Error starting video recording: $e');
      return false;
    }
  }

  /// Stop video recording
  Future<XFile?> stopVideoRecording() async {
    if (!_isInitialized || _controller == null) {
      return null;
    }

    if (!_controller!.value.isRecordingVideo) {
      return null;
    }

    try {
      final XFile file = await _controller!.stopVideoRecording();
      debugPrint('Video recorded: ${file.path}');
      return file;
    } catch (e) {
      debugPrint('Error stopping video recording: $e');
      return null;
    }
  }

  /// Get camera controller
  CameraController? get controller => _controller;

  /// Check if camera is initialized
  bool get isInitialized => _isInitialized;

  /// Get current camera index
  int get currentCameraIndex => _currentCameraIndex;

  /// Get available cameras count
  int get availableCamerasCount => _cameras?.length ?? 0;

  /// Dispose camera resources
  Future<void> dispose() async {
    if (_controller != null) {
      await _controller!.dispose();
      _controller = null;
    }
    _isInitialized = false;
  }

  /// Set flash mode
  Future<void> setFlashMode(FlashMode mode) async {
    if (!_isInitialized || _controller == null) {
      return;
    }

    try {
      await _controller!.setFlashMode(mode);
    } catch (e) {
      debugPrint('Error setting flash mode: $e');
    }
  }

  /// Set exposure mode
  Future<void> setExposureMode(ExposureMode mode) async {
    if (!_isInitialized || _controller == null) {
      return;
    }

    try {
      await _controller!.setExposureMode(mode);
    } catch (e) {
      debugPrint('Error setting exposure mode: $e');
    }
  }

  /// Set focus mode
  Future<void> setFocusMode(FocusMode mode) async {
    if (!_isInitialized || _controller == null) {
      return;
    }

    try {
      await _controller!.setFocusMode(mode);
    } catch (e) {
      debugPrint('Error setting focus mode: $e');
    }
  }
}

