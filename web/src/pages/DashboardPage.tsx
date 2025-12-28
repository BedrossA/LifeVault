/**
 * Dashboard Page with Analytics
 */
import { useState, useEffect } from 'react';
import { format, subDays } from 'date-fns';
import { useAuthStore } from '../store/authStore';
import { analyticsApi } from '../services/analyticsApi';
import { StatCard } from '../components/dashboard/StatCard';
import { DateRangePicker } from '../components/dashboard/DateRangePicker';
import { LineChart } from '../components/dashboard/LineChart';
import { BarChart } from '../components/dashboard/BarChart';
import { HeatmapChart } from '../components/dashboard/HeatmapChart';
import { ComparisonChart } from '../components/dashboard/ComparisonChart';
import { ProgressBar } from '../components/dashboard/ProgressBar';
import { PredictiveChart } from '../components/dashboard/PredictiveChart';
import { Timeline } from '../components/dashboard/Timeline';
import { DataEntryForm } from '../components/dashboard/DataEntryForm';
import { GoalManager } from '../components/dashboard/GoalManager';
import type { AnalyticsEntry, AnalyticsStats, Goal, DateRange, AnalyticsEntryCreate, GoalCreate } from '../types/analytics';

export function DashboardPage() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState<AnalyticsStats | null>(null);
  const [entries, setEntries] = useState<AnalyticsEntry[]>([]);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [dateRange, setDateRange] = useState<DateRange>({
    start: format(subDays(new Date(), 30), 'yyyy-MM-dd'),
    end: format(new Date(), 'yyyy-MM-dd'),
  });
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [showEntryForm, setShowEntryForm] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, [dateRange, selectedCategory]);

  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      const [statsData, entriesData, goalsData] = await Promise.all([
        analyticsApi.getStats(dateRange).catch(() => ({
          total_entries: 0,
          categories: {},
          date_range: { start: dateRange.start, end: dateRange.end },
          trends: [],
        })),
        analyticsApi.getEntries(
          selectedCategory !== 'all' ? selectedCategory : undefined,
          dateRange.start,
          dateRange.end
        ).catch(() => []),
        analyticsApi.getGoals().catch(() => []),
      ]);
      setStats(statsData);
      setEntries(entriesData);
      setGoals(goalsData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      // Set defaults on error
      setStats({
        total_entries: 0,
        categories: {},
        date_range: { start: dateRange.start, end: dateRange.end },
        trends: [],
      });
      setEntries([]);
      setGoals([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateEntry = async (data: AnalyticsEntryCreate) => {
    await analyticsApi.createEntry(data);
    setShowEntryForm(false);
    loadDashboardData();
  };

  const handleCreateGoal = async (data: GoalCreate) => {
    await analyticsApi.createGoal(data);
    loadDashboardData();
  };

  const handleUpdateGoal = async (id: string, data: Partial<GoalCreate>) => {
    await analyticsApi.updateGoal(id, data);
    loadDashboardData();
  };

  const handleDeleteGoal = async (id: string) => {
    await analyticsApi.deleteGoal(id);
    loadDashboardData();
  };

  const handleExport = async (format: 'csv' | 'json' = 'json') => {
    try {
      const blob = await analyticsApi.exportData(format, dateRange);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `lifevault-analytics-${format(new Date(), 'yyyy-MM-dd')}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  // Prepare chart data
  const timeSeriesData = entries
    .filter((e) => e.metric === 'steps' || e.metric === 'calories' || entries.length < 10)
    .map((e) => {
      try {
        const date = new Date(e.timestamp);
        return {
          date: format(date, 'yyyy-MM-dd'),
          value: e.value,
        };
      } catch {
        return null;
      }
    })
    .filter((e): e is { date: string; value: number } => e !== null)
    .reduce((acc, curr) => {
      const existing = acc.find((a) => a.date === curr.date);
      if (existing) {
        existing.value += curr.value;
      } else {
        acc.push(curr);
      }
      return acc;
    }, [] as Array<{ date: string; value: number }>)
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

  const categoryData = Object.entries(stats?.categories || {}).map(([category, count]) => ({
    category: category.charAt(0).toUpperCase() + category.slice(1),
    count,
  }));

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="flex items-center justify-center min-h-screen">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Welcome back, {user?.username || 'User'}!
            </h1>
            <p className="mt-1 text-sm text-gray-500">Your personal analytics dashboard</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setShowEntryForm(!showEntryForm)}
              className="btn btn-primary"
            >
              {showEntryForm ? 'Cancel' : '+ Add Entry'}
            </button>
            <button onClick={() => handleExport('json')} className="btn btn-secondary">
              Export JSON
            </button>
            <button onClick={() => handleExport('csv')} className="btn btn-secondary">
              Export CSV
            </button>
          </div>
        </div>

        {/* Date Range Picker */}
        <div className="card">
          <DateRangePicker onRangeChange={setDateRange} defaultRange={dateRange} />
        </div>

        {/* Data Entry Form */}
        {showEntryForm && (
          <DataEntryForm
            onSubmit={handleCreateEntry}
            onCancel={() => setShowEntryForm(false)}
          />
        )}

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Entries"
            value={stats?.total_entries || 0}
            change={stats?.trends[0]?.change_percent}
            trend={stats?.trends[0]?.change_percent && stats.trends[0].change_percent > 0 ? 'up' : 'down'}
            icon={<span className="text-2xl">📊</span>}
          />
          <StatCard
            title="Categories"
            value={Object.keys(stats?.categories || {}).length}
            icon={<span className="text-2xl">📁</span>}
          />
          <StatCard
            title="Active Goals"
            value={goals.length}
            icon={<span className="text-2xl">🎯</span>}
          />
          <StatCard
            title="This Period"
            value={entries.length}
            icon={<span className="text-2xl">📈</span>}
          />
        </div>

        {/* Goals Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            {goals.length > 0 && (
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-4">Goals Progress</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {goals.map((goal) => (
                    <ProgressBar
                      key={goal.id}
                      label={`${goal.metric} - ${goal.category}`}
                      current={goal.current_value}
                      target={goal.target_value}
                      unit={goal.unit}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
          <div>
            <GoalManager
              goals={goals}
              onCreate={handleCreateGoal}
              onUpdate={handleUpdateGoal}
              onDelete={handleDeleteGoal}
            />
          </div>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Time Series Line Chart */}
          {timeSeriesData.length > 0 && (
            <LineChart
              data={timeSeriesData}
              title="Activity Over Time"
              dataKey="value"
            />
          )}

          {/* Category Distribution */}
          {categoryData.length > 0 && (
            <BarChart
              data={categoryData}
              title="Entries by Category"
              dataKey="count"
              xKey="category"
            />
          )}

          {/* Heatmap */}
          {entries.length > 0 && timeSeriesData.length > 0 && (
            <HeatmapChart
              data={timeSeriesData}
              title="Activity Heatmap"
              startDate={new Date(dateRange.start)}
              endDate={new Date(dateRange.end)}
            />
          )}

          {/* Predictive Chart */}
          {timeSeriesData.length > 5 && (
            <PredictiveChart
              historicalData={timeSeriesData.slice(0, Math.floor(timeSeriesData.length * 0.8))}
              predictedData={timeSeriesData.slice(Math.floor(timeSeriesData.length * 0.8))}
              title="Trend Prediction"
            />
          )}

          {/* Comparison Chart - Multiple Metrics */}
          {entries.length > 0 && (
            <ComparisonChart
              data={timeSeriesData}
              title="Metrics Comparison"
              metrics={['value']}
            />
          )}
        </div>

        {/* Timeline */}
        <Timeline entries={entries.slice(0, 10)} />
      </div>
    </div>
  );
}
