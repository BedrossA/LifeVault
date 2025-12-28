/**
 * Analytics API Client
 */
import axios from 'axios';
import type {
  AnalyticsEntry,
  AnalyticsEntryCreate,
  AnalyticsStats,
  TimeSeriesData,
  Goal,
  GoalCreate,
  DateRange,
} from '../types/analytics';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

class AnalyticsApiClient {
  private getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  // Analytics Entries
  async createEntry(data: AnalyticsEntryCreate): Promise<AnalyticsEntry> {
    const response = await axios.post<AnalyticsEntry>(
      `${API_BASE_URL}/analytics/entries`,
      data,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async getEntries(category?: string, startDate?: string, endDate?: string): Promise<AnalyticsEntry[]> {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const response = await axios.get<AnalyticsEntry[]>(
      `${API_BASE_URL}/analytics/entries?${params.toString()}`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async getEntry(id: string): Promise<AnalyticsEntry> {
    const response = await axios.get<AnalyticsEntry>(
      `${API_BASE_URL}/analytics/entries/${id}`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async updateEntry(id: string, data: Partial<AnalyticsEntryCreate>): Promise<AnalyticsEntry> {
    const response = await axios.put<AnalyticsEntry>(
      `${API_BASE_URL}/analytics/entries/${id}`,
      data,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async deleteEntry(id: string): Promise<void> {
    await axios.delete(
      `${API_BASE_URL}/analytics/entries/${id}`,
      { headers: this.getAuthHeaders() }
    );
  }

  // Statistics
  async getStats(dateRange?: DateRange): Promise<AnalyticsStats> {
    const params = new URLSearchParams();
    if (dateRange) {
      params.append('start_date', dateRange.start);
      params.append('end_date', dateRange.end);
    }
    
    const response = await axios.get<AnalyticsStats>(
      `${API_BASE_URL}/analytics/stats?${params.toString()}`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  // Time Series Data
  async getTimeSeries(
    metric: string,
    category?: string,
    dateRange?: DateRange
  ): Promise<TimeSeriesData> {
    const params = new URLSearchParams();
    params.append('metric', metric);
    if (category) params.append('category', category);
    if (dateRange) {
      params.append('start_date', dateRange.start);
      params.append('end_date', dateRange.end);
    }
    
    const response = await axios.get<TimeSeriesData>(
      `${API_BASE_URL}/analytics/time-series?${params.toString()}`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  // Goals
  async createGoal(data: GoalCreate): Promise<Goal> {
    const response = await axios.post<Goal>(
      `${API_BASE_URL}/analytics/goals`,
      data,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async getGoals(): Promise<Goal[]> {
    const response = await axios.get<Goal[]>(
      `${API_BASE_URL}/analytics/goals`,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async updateGoal(id: string, data: Partial<GoalCreate>): Promise<Goal> {
    const response = await axios.put<Goal>(
      `${API_BASE_URL}/analytics/goals/${id}`,
      data,
      { headers: this.getAuthHeaders() }
    );
    return response.data;
  }

  async deleteGoal(id: string): Promise<void> {
    await axios.delete(
      `${API_BASE_URL}/analytics/goals/${id}`,
      { headers: this.getAuthHeaders() }
    );
  }

  // Export
  async exportData(format: 'csv' | 'json' = 'json', dateRange?: DateRange): Promise<Blob> {
    const params = new URLSearchParams();
    params.append('format', format);
    if (dateRange) {
      params.append('start_date', dateRange.start);
      params.append('end_date', dateRange.end);
    }
    
    const response = await axios.get(
      `${API_BASE_URL}/analytics/export?${params.toString()}`,
      {
        headers: this.getAuthHeaders(),
        responseType: 'blob',
      }
    );
    return response.data;
  }
}

export const analyticsApi = new AnalyticsApiClient();

