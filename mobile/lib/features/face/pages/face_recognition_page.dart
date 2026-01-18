// ignore_for_file: use_build_context_synchronously

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:camera/camera.dart';
import 'dart:io';
import '../services/face_api_service.dart';
import '../../../core/providers/services_provider.dart';
import '../../../core/network/api_exception.dart';

class FaceRecognitionPage extends ConsumerStatefulWidget {
  const FaceRecognitionPage({super.key});

  @override
  ConsumerState<FaceRecognitionPage> createState() =>
      _FaceRecognitionPageState();
}

class _FaceRecognitionPageState extends ConsumerState<FaceRecognitionPage> {
  final FaceApiService _faceApiService = FaceApiService();
  CameraController? _cameraController;
  bool _isInitialized = false;
  bool _isProcessing = false;
  int _enrolledFaces = 0;
  List<Map<String, dynamic>> _faces = [];

  @override
  void initState() {
    super.initState();
    _initializeCamera();
    _loadFaceData();
  }

  Future<void> _initializeCamera() async {
    try {
      final cameraService = ref.read(cameraServiceProvider);
      final initialized = await cameraService.initialize(
        resolution: ResolutionPreset.medium,
      );
      
      if (initialized && cameraService.controller != null) {
        setState(() {
          _cameraController = cameraService.controller;
          _isInitialized = true;
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Camera error: $e')),
        );
      }
    }
  }

  Future<void> _loadFaceData() async {
  if (!mounted) return;
  
  setState(() => _isProcessing = true);
  
  try {
    final faces = await _faceApiService.getMyFaces();
    if (mounted) {
      setState(() {
        _faces = faces;
        _enrolledFaces = faces.length;
        _isProcessing = false;
        });
      }
    } catch (e) {
      if (mounted) {
        // Silently fail - user might not be logged in
        setState(() {
          _enrolledFaces = 0;
          _faces = [];
          _isProcessing = false;
        });
      
      // Show error only if it's not an auth issue
      if (e is! ApiException || (e.statusCode != 401 && e.statusCode != 403)) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to load face data: ${e.toString()}'),
            action: SnackBarAction(
              label: 'Retry',
              onPressed: _loadFaceData,
            ),
          ),
        );
      }
    }
  }
}

  @override
  void dispose() {
    final cameraService = ref.read(cameraServiceProvider);
    cameraService.dispose();
    super.dispose();
  }

  Future<void> _enrollFace() async {
    if (_cameraController == null || !_isInitialized) return;

    setState(() => _isProcessing = true);
    try {
      final imageFile = await _cameraController!.takePicture();
      final file = File(imageFile.path);

      // Show dialog to get label
      final label = await showDialog<String>(
        context: context,
        builder: (context) {
          String labelText = 'primary';
          return AlertDialog(
            title: const Text('Enroll Face'),
            content: TextField(
              autofocus: true,
              decoration: const InputDecoration(
                labelText: 'Label',
                hintText: 'e.g., primary, with_glasses',
              ),
              onChanged: (value) => labelText = value,
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Cancel'),
              ),
              TextButton(
                onPressed: () => Navigator.pop(context, labelText),
                child: const Text('Enroll'),
              ),
            ],
          );
        },
      );

      if (label != null && label.isNotEmpty) {
        final result = await _faceApiService.enrollFace(
          imageFile: file,
          label: label,
        );

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Face enrolled successfully! Face ID: ${result['face_id']}'),
              backgroundColor: Colors.green,
            ),
          );
          // Reload face data
          await _loadFaceData();
        }
      }
    } on ApiException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: ${e.message}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() => _isProcessing = false);
    }
  }

  Future<void> _recognizeFace() async {
    if (_cameraController == null || !_isInitialized) return;

    setState(() => _isProcessing = true);
    try {
      final imageFile = await _cameraController!.takePicture();
      final file = File(imageFile.path);

      final result = await _faceApiService.recognizeFace(imageFile: file);

      if (mounted) {
        if (result['recognized'] == true) {
          final username = result['username'] ?? 'Unknown';
          final confidence = result['confidence'] ?? 0.0;
          
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Recognized: $username (${(confidence * 100).toStringAsFixed(1)}% confidence)'),
              backgroundColor: Colors.green,
              duration: const Duration(seconds: 3),
            ),
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Face not recognized'),
              backgroundColor: Colors.orange,
            ),
          );
        }
      }
    } on ApiException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: ${e.message}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() => _isProcessing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Face Recognition'),
        actions: [
          IconButton(
            icon: const Icon(Icons.face),
            onPressed: () {
              // Show enrolled faces
              showDialog(
                context: context,
                builder: (context) => AlertDialog(
                  title: const Text('Enrolled Faces'),
                  content: _faces.isEmpty
                      ? const Text('No faces enrolled yet')
                      : SizedBox(
                          width: double.maxFinite,
                          child: ListView.builder(
                            shrinkWrap: true,
                            itemCount: _faces.length,
                            itemBuilder: (context, index) {
                              final face = _faces[index];
                              return ListTile(
                                leading: const Icon(Icons.face),
                                title: Text(face['label'] ?? 'Unknown'),
                                subtitle: Text('Face ID: ${face['face_id']}'),
                                trailing: IconButton(
                                  icon: const Icon(Icons.delete, color: Colors.red),
                                  onPressed: () async {
                                    try {
                                      await _faceApiService.deleteFace(face['face_id']);
                                      if (context.mounted) {
                                        Navigator.pop(context);
                                        await _loadFaceData();
                                        ScaffoldMessenger.of(context).showSnackBar(
                                          const SnackBar(content: Text('Face deleted')),
                                        );
                                      }
                                    } catch (e) {
                                      if (context.mounted) {
                                        ScaffoldMessenger.of(context).showSnackBar(
                                          SnackBar(content: Text('Error: $e')),
                                        );
                                      }
                                    }
                                  },
                                ),
                              );
                            },
                          ),
                        ),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(context),
                      child: const Text('Close'),
                    ),
                  ],
                ),
              );
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Camera Preview
          Expanded(
            flex: 3,
            child: _isInitialized && _cameraController != null
                ? CameraPreview(_cameraController!)
                : Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.camera_alt,
                          size: 64,
                          color: Theme.of(context)
                              .colorScheme
                              .onSurface
                              .withValues(alpha: 0.5),
                        ),
                        const SizedBox(height: 16),
                        Text(
                          _isInitialized
                              ? 'Camera not available'
                              : 'Initializing camera...',
                          style: Theme.of(context).textTheme.bodyLarge,
                        ),
                      ],
                    ),
                  ),
          ),
          // Controls
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.surface,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.1),
                  blurRadius: 10,
                  offset: const Offset(0, -5),
                ),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: _isProcessing ? null : _enrollFace,
                        icon: const Icon(Icons.person_add),
                        label: const Text('Enroll Face'),
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 16),
                        ),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: _isProcessing ? null : _recognizeFace,
                        icon: const Icon(Icons.face),
                        label: const Text('Recognize'),
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 16),
                        ),
                      ),
                    ),
                  ],
                ),
                if (_isProcessing) ...[
                  const SizedBox(height: 16),
                  const LinearProgressIndicator(),
                  const SizedBox(height: 8),
                  Text(
                    'Processing...',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
                const SizedBox(height: 16),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        _StatItem(
                          icon: Icons.face,
                          label: 'Enrolled',
                          value: '$_enrolledFaces',
                        ),
                        _StatItem(
                          icon: Icons.check_circle,
                          label: 'Status',
                          value: _isInitialized ? 'Ready' : 'Not Ready',
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _StatItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _StatItem({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(icon, size: 32, color: Theme.of(context).colorScheme.primary),
        const SizedBox(height: 8),
        Text(
          value,
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ],
    );
  }
}
