/**
 * Notification API Service
 */
import { apiClient } from './api';
import type { NotificationPreferences } from '../types/notification';

class NotificationApiClient {
  /**
   * Get user notification preferences
   */
  async getPreferences(): Promise<NotificationPreferences> {
    const response = await apiClient.client.get<NotificationPreferences>(
      '/notifications/preferences'
    );
    return response.data;
  }

  /**
   * Update user notification preferences
   */
  async updatePreferences(preferences: Partial<NotificationPreferences>): Promise<NotificationPreferences> {
    const response = await apiClient.client.put<NotificationPreferences>(
      '/notifications/preferences',
      preferences
    );
    return response.data;
  }

  /**
   * Get unread notifications count
   */
  async getUnreadCount(): Promise<number> {
    const response = await apiClient.client.get<{ count: number }>(
      '/notifications/unread-count'
    );
    return response.data.count;
  }

  /**
   * Mark notification as read
   */
  async markAsRead(notificationId: string): Promise<void> {
    await apiClient.client.post(`/notifications/${notificationId}/read`);
  }

  /**
   * Mark all notifications as read
   */
  async markAllAsRead(): Promise<void> {
    await apiClient.client.post('/notifications/read-all');
  }

  /**
   * Get user notifications
   */
  async getNotifications(limit: number = 50, offset: number = 0): Promise<any[]> {
    const response = await apiClient.client.get<any[]>(
      `/notifications?limit=${limit}&offset=${offset}`
    );
    return response.data;
  }

  /**
   * Delete notification
   */
  async deleteNotification(notificationId: string): Promise<void> {
    await apiClient.client.delete(`/notifications/${notificationId}`);
  }
}

export const notificationApi = new NotificationApiClient();

