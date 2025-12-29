import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../services/auth_api_service.dart';

class UserActivity {
  final int id;
  final int userId;
  final String action;
  final String? details;
  final String? ipAddress;
  final DateTime timestamp;

  UserActivity({
    required this.id,
    required this.userId,
    required this.action,
    this.details,
    this.ipAddress,
    required this.timestamp,
  });

  factory UserActivity.fromJson(Map<String, dynamic> json) => UserActivity(
        id: json['id'] as int,
        userId: json['user_id'] as int,
        action: json['action'] as String,
        details: json['details'] as String?,
        ipAddress: json['ip_address'] as String?,
        timestamp: DateTime.parse(json['timestamp'] as String),
      );
}

final authApiServiceProvider =
    Provider<AuthApiService>((ref) => AuthApiService());

class ActivityPage extends ConsumerStatefulWidget {
  const ActivityPage({super.key});

  @override
  ConsumerState<ActivityPage> createState() => _ActivityPageState();
}

class _ActivityPageState extends ConsumerState<ActivityPage> {
  List<UserActivity> _activities = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadActivities();
  }

  Future<void> _loadActivities() async {
    setState(() => _isLoading = true);
    try {
      final service = ref.read(authApiServiceProvider);
      final activitiesData = await service.getUserActivity(limit: 50);
      setState(() {
        _activities = activitiesData
            .map((json) => UserActivity.fromJson(json))
            .toList();
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading activities: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Activity Log'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadActivities,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadActivities,
              child: _activities.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.timeline,
                            size: 64,
                            color: Theme.of(context)
                                .colorScheme
                                .onSurface
                                .withValues(alpha: 0.5),
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'No activity yet',
                            style: Theme.of(context).textTheme.bodyLarge,
                          ),
                        ],
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: _activities.length,
                      itemBuilder: (context, index) {
                        final activity = _activities[index];
                        return Card(
                          margin: const EdgeInsets.only(bottom: 8),
                          child: ListTile(
                            leading: CircleAvatar(
                              backgroundColor:
                                  Theme.of(context).colorScheme.primaryContainer,
                              child: Icon(
                                Icons.timeline,
                                color: Theme.of(context)
                                    .colorScheme
                                    .onPrimaryContainer,
                              ),
                            ),
                            title: Text(activity.action),
                            subtitle: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const SizedBox(height: 4),
                                Text(
                                  DateFormat('MMM d, y • h:mm a')
                                      .format(activity.timestamp),
                                  style: Theme.of(context).textTheme.bodySmall,
                                ),
                                if (activity.details != null)
                                  Text(
                                    activity.details!,
                                    style: Theme.of(context).textTheme.bodySmall,
                                  ),
                                if (activity.ipAddress != null)
                                  Text(
                                    'IP: ${activity.ipAddress}',
                                    style: Theme.of(context).textTheme.bodySmall,
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

