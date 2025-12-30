import 'package:flutter/material.dart';

class TermsPage extends StatelessWidget {
  const TermsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Terms of Service'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Terms of Service',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 16),
            Text(
              'Last Updated: ${DateTime.now().toString().split(' ')[0]}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 24),
            _buildSection(
              context,
              '1. Acceptance of Terms',
              'By accessing and using LifeVault, you accept and agree to be bound by the terms and provision of this agreement.',
            ),
            _buildSection(
              context,
              '2. Use License',
              'Permission is granted to temporarily use LifeVault for personal, non-commercial purposes. This is the grant of a license, not a transfer of title.',
            ),
            _buildSection(
              context,
              '3. User Account',
              'You are responsible for:\n'
              '• Maintaining the confidentiality of your account\n'
              '• All activities that occur under your account\n'
              '• Notifying us immediately of any unauthorized use',
            ),
            _buildSection(
              context,
              '4. Prohibited Uses',
              'You may not:\n'
              '• Use the service for any illegal purpose\n'
              '• Attempt to gain unauthorized access\n'
              '• Interfere with or disrupt the service\n'
              '• Use automated systems to access the service',
            ),
            _buildSection(
              context,
              '5. Data and Privacy',
              'Your use of LifeVault is also governed by our Privacy Policy. Please review our Privacy Policy to understand our practices.',
            ),
            _buildSection(
              context,
              '6. Service Availability',
              'We reserve the right to modify, suspend, or discontinue the service at any time without prior notice.',
            ),
            _buildSection(
              context,
              '7. Limitation of Liability',
              'LifeVault shall not be liable for any indirect, incidental, special, consequential, or punitive damages resulting from your use of the service.',
            ),
            _buildSection(
              context,
              '8. Changes to Terms',
              'We reserve the right to modify these terms at any time. Your continued use of the service after changes constitutes acceptance of the new terms.',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSection(BuildContext context, String title, String content) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            content,
            style: Theme.of(context).textTheme.bodyMedium,
          ),
        ],
      ),
    );
  }
}

