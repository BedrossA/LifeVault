import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import '../models/analytics_models.dart';
import '../services/analytics_api_service.dart';
import '../widgets/add_entry_dialog.dart';

final analyticsServiceProvider =
    Provider<AnalyticsApiService>((ref) => AnalyticsApiService());

class AnalyticsPage extends ConsumerStatefulWidget {
  const AnalyticsPage({super.key});

  @override
  ConsumerState<AnalyticsPage> createState() => _AnalyticsPageState();
}

class _AnalyticsPageState extends ConsumerState<AnalyticsPage>
    with SingleTickerProviderStateMixin, AutomaticKeepAliveClientMixin {

  late TabController _tabController;
  List<AnalyticsEntry> _entries = [];
  AnalyticsStats? _stats;
  TimeSeriesData? _timeSeries;
  bool _isLoading = false;
  String _selectedMetric = 'steps';

  @override
  bool get wantKeepAlive => true;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadData();
  // Listen to tab changes to load data on demand
    _tabController.addListener(() {
      if (!_tabController.indexIsChanging) {
        _onTabChanged(_tabController.index);
      }
    });
  }
  
  void _onTabChanged(int index) {
    // Optionally refresh data for specific tabs
    if (index == 0 && _timeSeries == null) {
      _loadChartData();
    }
  }

  Future<void> _loadChartData() async {
    try {
      final service = ref.read(analyticsServiceProvider);
      final timeSeries = await service.getTimeSeries(metric: _selectedMetric);
      setState(() {
        _timeSeries = timeSeries;
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading chart data: $e')),
        );
      }
    }
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    try {
      final service = ref.read(analyticsServiceProvider);
      final entries = await service.getEntries();
      final stats = await service.getStats();
      final timeSeries = await service.getTimeSeries(metric: _selectedMetric);

      setState(() {
        _entries = entries;
        _stats = stats;
        _timeSeries = timeSeries;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading data: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Analytics'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(icon: Icon(Icons.show_chart), text: 'Charts'),
            Tab(icon: Icon(Icons.list), text: 'Entries'),
            Tab(icon: Icon(Icons.track_changes), text: 'Stats'),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => _showAddEntryDialog(),
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : TabBarView(
              controller: _tabController,
              children: [
                _buildChartsTab(),
                _buildEntriesTab(),
                _buildStatsTab(),
              ],
            ),
    );
  }

  Widget _buildChartsTab() {
    if (_timeSeries == null || _timeSeries!.data.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.show_chart,
              size: 64,
              color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5),
            ),
            const SizedBox(height: 16),
            Text(
              'No data available',
              style: Theme.of(context).textTheme.bodyLarge,
            ),
          ],
        ),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Metric Selector
          DropdownButtonFormField<String>(
            initialValue: _selectedMetric,
            decoration: const InputDecoration(
              labelText: 'Metric',
              border: OutlineInputBorder(),
            ),
            items: const [
              DropdownMenuItem(value: 'steps', child: Text('Steps')),
              DropdownMenuItem(value: 'calories', child: Text('Calories')),
              DropdownMenuItem(value: 'hours', child: Text('Hours')),
              DropdownMenuItem(value: 'mood_score', child: Text('Mood Score')),
            ],
            onChanged: (value) {
              if (value != null && value != _selectedMetric) {
                setState(() => _selectedMetric = value);
                _loadData();
              }
            },
          ),
          const SizedBox(height: 24),
          // Line Chart
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Time Series: $_selectedMetric',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    height: 300,
                    child: LineChart(
                      LineChartData(
                        gridData: FlGridData(
                          show: true,
                          drawVerticalLine: true,
                          horizontalInterval: _timeSeries!.data.isNotEmpty
                              ? (_timeSeries!.data.map((e) => e.value).reduce((a, b) => a > b ? a : b) / 5)
                              : 1,
                        ),
                        titlesData: FlTitlesData(
                          leftTitles: AxisTitles(
                            sideTitles: SideTitles(
                              showTitles: true,
                              reservedSize: 40,
                              getTitlesWidget: (value, meta) {
                                return Padding(
                                  padding: const EdgeInsets.only(right: 4),
                                  child: Text(
                                    value.toInt().toString(),
                                    style: TextStyle(
                                      fontSize: 10,
                                      color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.6),
                                    ),
                                  ),
                                );
                              },
                            ),
                          ),
                          bottomTitles: AxisTitles(
                            sideTitles: SideTitles(
                              showTitles: true,
                              reservedSize: 30,
                              getTitlesWidget: (value, meta) {
                                final index = value.toInt();
                                if (index >= 0 && index < _timeSeries!.data.length) {
                                  final datePoint = _timeSeries!.data[index];
                                  // Show label every nth point to avoid crowding
                                  final showInterval = (_timeSeries!.data.length / 6).ceil();
                                  if (index % showInterval == 0 || index == _timeSeries!.data.length - 1) {
                                    return Padding(
                                      padding: const EdgeInsets.only(top: 4),
                                      child: Text(
                                        DateFormat('MMM d').format(datePoint.date),
                                        style: TextStyle(
                                          fontSize: 10,
                                          color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.6),
                                        ),
                                      ),
                                    );
                                  }
                                }
                                return const Text('');
                              },
                            ),
                          ),
                          topTitles: const AxisTitles(
                            sideTitles: SideTitles(showTitles: false),
                          ),
                          rightTitles: const AxisTitles(
                            sideTitles: SideTitles(showTitles: false),
                          ),
                        ),
                        borderData: FlBorderData(
                          show: true,
                          border: Border.all(
                            color: Theme.of(context).colorScheme.outline.withValues(alpha: 0.3),
                            width: 1,
                          ),
                        ),
                        lineBarsData: [
                          LineChartBarData(
                            spots: _timeSeries!.data
                                .asMap()
                                .entries
                                .map((e) => FlSpot(
                                      e.key.toDouble(),
                                      e.value.value,
                                    ))
                                .toList(),
                            isCurved: true,
                            color: Theme.of(context).colorScheme.primary,
                            barWidth: 3,
                            dotData: FlDotData(
                              show: _timeSeries!.data.length <= 20, // Show dots only if not too many points
                              getDotPainter: (spot, percent, barData, index) {
                                return FlDotCirclePainter(
                                  radius: 4,
                                  color: Theme.of(context).colorScheme.primary,
                                  strokeWidth: 2,
                                  strokeColor: Theme.of(context).colorScheme.surface,
                                );
                              },
                            ),
                            belowBarData: BarAreaData(
                              show: true,
                              color: Theme.of(context).colorScheme.primary.withValues(alpha: 0.1),
                            ),
                          ),
                        ],
                        minX: 0,
                        maxX: _timeSeries!.data.length > 0 ? (_timeSeries!.data.length - 1).toDouble() : 0,
                        minY: _timeSeries!.data.isNotEmpty
                            ? (_timeSeries!.data.map((e) => e.value).reduce((a, b) => a < b ? a : b) * 0.9)
                            : 0,
                        maxY: _timeSeries!.data.isNotEmpty
                            ? (_timeSeries!.data.map((e) => e.value).reduce((a, b) => a > b ? a : b) * 1.1)
                            : 100,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEntriesTab() {
    return RefreshIndicator(
      onRefresh: _loadData,
      child: _entries.isEmpty
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.inbox,
                    size: 64,
                    color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'No entries yet',
                    style: Theme.of(context).textTheme.bodyLarge,
                  ),
                  const SizedBox(height: 8),
                  ElevatedButton.icon(
                    onPressed: _showAddEntryDialog,
                    icon: const Icon(Icons.add),
                    label: const Text('Add Entry'),
                  ),
                ],
              ),
            )
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _entries.length,
              itemBuilder: (context, index) {
                final entry = _entries[index];
                return Card(
                  margin: const EdgeInsets.only(bottom: 8),
                  child: ListTile(
                    leading: CircleAvatar(
                      backgroundColor: Theme.of(context).colorScheme.primaryContainer,
                      child: Text(
                        entry.category[0].toUpperCase(),
                        style: TextStyle(
                          color: Theme.of(context).colorScheme.onPrimaryContainer,
                        ),
                      ),
                    ),
                    title: Text('${entry.metric} - ${entry.category}'),
                    subtitle: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '${entry.value} ${entry.unit ?? ''}',
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                        ),
                        Text(
                          DateFormat('MMM d, y • h:mm a').format(entry.timestamp),
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                        if (entry.notes != null && entry.notes!.isNotEmpty)
                          Text(
                            entry.notes!,
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                      ],
                    ),
                    trailing: PopupMenuButton(
                      itemBuilder: (context) => [
                        const PopupMenuItem(
                          value: 'edit',
                          child: Text('Edit'),
                        ),
                        const PopupMenuItem(
                          value: 'delete',
                          child: Text('Delete'),
                        ),
                      ],
                      onSelected: (value) {
                        if (value == 'delete') {
                          _deleteEntry(entry.id);
                        }
                      },
                    ),
                  ),
                );
              },
            ),
    );
  }

  Widget _buildStatsTab() {
    if (_stats == null) {
      return const Center(child: CircularProgressIndicator());
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Total Entries',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '${_stats!.totalEntries}',
                    style: Theme.of(context).textTheme.displayMedium?.copyWith(
                          color: Theme.of(context).colorScheme.primary,
                        ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Categories',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 12),
          ..._stats!.categories.entries.map(
            (entry) => Card(
              margin: const EdgeInsets.only(bottom: 8),
              child: ListTile(
                title: Text(entry.key),
                trailing: Text(
                  '${entry.value} entries',
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _showAddEntryDialog() async {
    final result = await showDialog<bool>(
      context: context,
      builder: (context) => const AddEntryDialog(),
    );
    if (result == true) {
      _loadData();
    }
  }

  Future<void> _deleteEntry(String id) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Entry'),
        content: const Text('Are you sure you want to delete this entry?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      try {
        await ref.read(analyticsServiceProvider).deleteEntry(id);
        _loadData();
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Entry deleted')),
          );
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error deleting entry: $e')),
          );
        }
      }
    }
  }
}
