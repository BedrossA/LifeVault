import 'package:flutter/material.dart';

class PrivacyPolicyPage extends StatelessWidget {
  const PrivacyPolicyPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Privacy Policy'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Privacy Policy',
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
              '1. Information We Collect',
              'We collect information that you provide directly to us, including:\n'
              '• Account information (username, email)\n'
              '• Analytics data you choose to track\n'
              '• Face recognition data (stored securely and encrypted)\n'
              '• Device information for app functionality',
            ),
            _buildSection(
              context,
              '2. How We Use Your Information',
              'We use the information we collect to:\n'
              '• Provide and maintain our services\n'
              '• Process your requests and transactions\n'
              '• Send you technical notices and support messages\n'
              '• Improve our services and develop new features',
            ),
            _buildSection(
              context,
              '3. Data Security',
              'We implement appropriate technical and organizational measures to protect your personal data:\n'
              '• Encryption of sensitive data\n'
              '• Secure storage using industry-standard practices\n'
              '• Regular security audits\n'
              '• Access controls and authentication',
            ),
            _buildSection(
              context,
              '4. Data Retention',
              'We retain your personal data only for as long as necessary to fulfill the purposes outlined in this policy, unless a longer retention period is required by law.',
            ),
            _buildSection(
              context,
              '5. Your Rights',
              'You have the right to:\n'
              '• Access your personal data\n'
              '• Correct inaccurate data\n'
              '• Request deletion of your data\n'
              '• Export your data\n'
              '• Withdraw consent at any time',
            ),
            _buildSection(
              context,
              '6. Contact Us',
              'If you have any questions about this Privacy Policy, please contact us through the app settings or support channels.',
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

