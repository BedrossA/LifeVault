import 'package:flutter/material.dart';

class FaceRecognitionPage extends StatelessWidget {
  const FaceRecognitionPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Face Recognition'),
      ),
      body: const Center(
        child: Text('Face Recognition Page'),
      ),
    );
  }
}

