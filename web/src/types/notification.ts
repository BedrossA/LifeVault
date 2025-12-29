/**
 * Notification type definitions
 */

export type NotificationType = 'success' | 'error' | 'info' | 'warning';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message?: string;
  duration?: number; // Auto-dismiss after milliseconds (0 = no auto-dismiss)
  persistent?: boolean; // Don't auto-dismiss
  action?: {
    label: string;
    onClick: () => void;
  };
  timestamp: Date;
}

export interface NotificationPreferences {
  browserNotifications: boolean;
  soundEnabled: boolean;
  desktopEnabled: boolean;
  emailEnabled: boolean;
  types: {
    success: boolean;
    error: boolean;
    info: boolean;
    warning: boolean;
  };
  quietHours: {
    enabled: boolean;
    start: string; // HH:mm format
    end: string; // HH:mm format
  };
}

export interface NotificationSettings {
  preferences: NotificationPreferences;
  permission: NotificationPermission;
}

