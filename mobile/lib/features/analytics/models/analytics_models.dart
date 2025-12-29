class AnalyticsEntry {
  final String id;
  final int userId;
  final String category;
  final String metric;
  final double value;
  final String? unit;
  final String? notes;
  final Map<String, dynamic>? metadata;
  final DateTime timestamp;

  AnalyticsEntry({
    required this.id,
    required this.userId,
    required this.category,
    required this.metric,
    required this.value,
    this.unit,
    this.notes,
    this.metadata,
    required this.timestamp,
  });

  factory AnalyticsEntry.fromJson(Map<String, dynamic> json) => AnalyticsEntry(
        id: json['id'] as String,
        userId: json['user_id'] as int,
        category: json['category'] as String,
        metric: json['metric'] as String,
        value: (json['value'] as num).toDouble(),
        unit: json['unit'] as String?,
        notes: json['notes'] as String?,
        metadata: json['metadata'] as Map<String, dynamic>?,
        timestamp: DateTime.parse(json['timestamp'] as String),
      );
}

class AnalyticsEntryCreate {
  final String category;
  final String metric;
  final double value;
  final String? unit;
  final String? notes;
  final Map<String, dynamic>? metadata;

  AnalyticsEntryCreate({
    required this.category,
    required this.metric,
    required this.value,
    this.unit,
    this.notes,
    this.metadata,
  });

  Map<String, dynamic> toJson() => {
        'category': category,
        'metric': metric,
        'value': value,
        if (unit != null) 'unit': unit,
        if (notes != null) 'notes': notes,
        if (metadata != null) 'metadata': metadata,
      };
}

class AnalyticsStats {
  final int totalEntries;
  final Map<String, int> categories;
  final Map<String, String> dateRange;
  final List<dynamic> trends;

  AnalyticsStats({
    required this.totalEntries,
    required this.categories,
    required this.dateRange,
    required this.trends,
  });

  factory AnalyticsStats.fromJson(Map<String, dynamic> json) => AnalyticsStats(
        totalEntries: json['total_entries'] as int,
        categories: Map<String, int>.from(
          json['categories'] as Map<String, dynamic>,
        ),
        dateRange: Map<String, String>.from(
          json['date_range'] as Map<String, dynamic>,
        ),
        trends: json['trends'] as List<dynamic>,
      );
}

class TimeSeriesData {
  final String metric;
  final List<TimeSeriesPoint> data;

  TimeSeriesData({
    required this.metric,
    required this.data,
  });

  factory TimeSeriesData.fromJson(Map<String, dynamic> json) => TimeSeriesData(
        metric: json['metric'] as String,
        data: (json['data'] as List<dynamic>)
            .map((e) => TimeSeriesPoint.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
}

class TimeSeriesPoint {
  final DateTime date;
  final double value;

  TimeSeriesPoint({
    required this.date,
    required this.value,
  });

  factory TimeSeriesPoint.fromJson(Map<String, dynamic> json) => TimeSeriesPoint(
        date: DateTime.parse(json['date'] as String),
        value: (json['value'] as num).toDouble(),
      );
}

class Goal {
  final String id;
  final int userId;
  final String metric;
  final String category;
  final double targetValue;
  final String unit;
  final DateTime? deadline;
  final bool isActive;

  Goal({
    required this.id,
    required this.userId,
    required this.metric,
    required this.category,
    required this.targetValue,
    required this.unit,
    this.deadline,
    required this.isActive,
  });

  factory Goal.fromJson(Map<String, dynamic> json) => Goal(
        id: json['id'] as String,
        userId: json['user_id'] as int,
        metric: json['metric'] as String,
        category: json['category'] as String,
        targetValue: (json['target_value'] as num).toDouble(),
        unit: json['unit'] as String,
        deadline: json['deadline'] != null
            ? DateTime.parse(json['deadline'] as String)
            : null,
        isActive: json['is_active'] as bool? ?? true,
      );
}

class GoalCreate {
  final String metric;
  final String category;
  final double targetValue;
  final String unit;
  final DateTime? deadline;

  GoalCreate({
    required this.metric,
    required this.category,
    required this.targetValue,
    required this.unit,
    this.deadline,
  });

  Map<String, dynamic> toJson() => {
        'metric': metric,
        'category': category,
        'target_value': targetValue,
        'unit': unit,
        if (deadline != null) 'deadline': deadline!.toIso8601String(),
      };
}

