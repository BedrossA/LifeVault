import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../services/auth_api_service.dart';
import '../models/auth_models.dart';

final authApiServiceProvider =
    Provider<AuthApiService>((ref) => AuthApiService());

class LoginHistoryPage extends ConsumerStatefulWidget {
  const LoginHistoryPage({super.key});

  @override
  ConsumerState<LoginHistoryPage> createState() => _LoginHistoryPageState();
}

class _LoginHistoryPageState extends ConsumerState<LoginHistoryPage> {
  List<LoginHistory> _history = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    setState(() => _isLoading = true);
    try {
      final service = ref.read(authApiServiceProvider);
      final history = await service.getLoginHistory(limit: 50);
      setState(() {
        _history = history;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading history: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Login History'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadHistory,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadHistory,
              child: _history.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.history,
                            size: 64,
                            color: Theme.of(context)
                                .colorScheme
                                .onSurface
                                .withValues(alpha: 0.5),
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'No login history',
                            style: Theme.of(context).textTheme.bodyLarge,
                          ),
                        ],
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: _history.length,
                      itemBuilder: (context, index) {
                        final entry = _history[index];
                        return Card(
                          margin: const EdgeInsets.only(bottom: 8),
                          child: ListTile(
                            leading: Icon(
                              entry.success ? Icons.check_circle : Icons.cancel,
                              color: entry.success ? Colors.green : Colors.red,
                            ),
                            title: Text(
                              entry.success ? 'Successful Login' : 'Failed Login',
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                color: entry.success ? Colors.green : Colors.red,
                              ),
                            ),
                            subtitle: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const SizedBox(height: 4),
                                Text(
                                  DateFormat('MMM d, y • h:mm a')
                                      .format(entry.timestamp),
                                  style: Theme.of(context).textTheme.bodySmall,
                                ),
                                if (entry.ipAddress != null)
                                  Text(
                                    'IP: ${entry.ipAddress}',
                                    style: Theme.of(context).textTheme.bodySmall,
                                  ),
                                if (entry.userAgent != null)
                                  Text(
                                    entry.userAgent!,
                                    style: Theme.of(context).textTheme.bodySmall,
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
            ),
    );
  }
}

