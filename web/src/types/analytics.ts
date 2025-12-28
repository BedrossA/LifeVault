/**
 * Analytics data types
 */

export interface AnalyticsEntry {
  id?: string;
  user_id: number;
  category: string;
  metric: string;
  value: number;
  unit?: string;
  timestamp: string;
  notes?: string;
  metadata?: Record<string, unknown>;
}

export interface AnalyticsEntryCreate {
  category: string;
  metric: string;
  value: number;
  unit?: string;
  notes?: string;
  metadata?: Record<string, unknown>;
}

export interface AnalyticsStats {
  total_entries: number;
  categories: Record<string, number>;
  date_range: {
    start: string;
    end: string;
  };
  trends: {
    metric: string;
    change: number;
    change_percent: number;
  }[];
}

export interface ChartDataPoint {
  date: string;
  value: number;
  label?: string;
}

export interface TimeSeriesData {
  metric: string;
  category: string;
  data: ChartDataPoint[];
}

export interface Goal {
  id?: string;
  user_id: number;
  metric: string;
  category: string;
  target_value: number;
  current_value: number;
  unit?: string;
  deadline?: string;
  created_at: string;
}

export interface GoalCreate {
  metric: string;
  category: string;
  target_value: number;
  unit?: string;
  deadline?: string;
}

export interface DateRange {
  start: string;
  end: string;
}

