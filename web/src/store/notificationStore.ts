/**
 * Notification Store (Zustand) for managing notifications
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Notification, NotificationPreferences, NotificationType } from '../types/notification';

interface NotificationState {
  notifications: Notification[];
  preferences: NotificationPreferences;
  permission: NotificationPermission;
  
  // Actions
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => string;
  removeNotification: (id: string) => void;
  clearAll: () => void;
  
  // Permission
  requestPermission: () => Promise<NotificationPermission>;
  checkPermission: () => NotificationPermission;
  
  // Preferences
  updatePreferences: (preferences: Partial<NotificationPreferences>) => void;
  resetPreferences: () => void;
  
  // Helper methods
  showSuccess: (title: string, message?: string, options?: Partial<Notification>) => string;
  showError: (title: string, message?: string, options?: Partial<Notification>) => string;
  showInfo: (title: string, message?: string, options?: Partial<Notification>) => string;
  showWarning: (title: string, message?: string, options?: Partial<Notification>) => string;
}

const defaultPreferences: NotificationPreferences = {
  browserNotifications: true,
  soundEnabled: true,
  desktopEnabled: true,
  emailEnabled: false,
  types: {
    success: true,
    error: true,
    info: true,
    warning: true,
  },
  quietHours: {
    enabled: false,
    start: '22:00',
    end: '08:00',
  },
};

// Check if we're in quiet hours
const isQuietHours = (preferences: NotificationPreferences): boolean => {
  if (!preferences.quietHours.enabled) return false;
  
  const now = new Date();
  const currentTime = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
  const { start, end } = preferences.quietHours;
  
  // Handle quiet hours that span midnight
  if (start > end) {
    return currentTime >= start || currentTime <= end;
  }
  return currentTime >= start && currentTime <= end;
};

// Show browser notification
const showBrowserNotification = (
  notification: Notification,
  preferences: NotificationPreferences
) => {
  if (!preferences.browserNotifications) return;
  if (!preferences.types[notification.type]) return;
  if (isQuietHours(preferences)) return;
  
  if ('Notification' in window && Notification.permission === 'granted') {
    const browserNotification = new Notification(notification.title, {
      body: notification.message,
      icon: '/favicon.ico',
      badge: '/favicon.ico',
      tag: notification.id,
      requireInteraction: notification.persistent,
    });
    
    browserNotification.onclick = () => {
      window.focus();
      browserNotification.close();
    };
    
    // Auto-close after duration if not persistent
    if (!notification.persistent && notification.duration && notification.duration > 0) {
      setTimeout(() => browserNotification.close(), notification.duration);
    }
  }
};

// Play notification sound
const playNotificationSound = (type: NotificationType, preferences: NotificationPreferences) => {
  if (!preferences.soundEnabled) return;
  if (!preferences.types[type]) return;
  if (isQuietHours(preferences)) return;
  
  // Create audio context for simple beep sounds
  try {
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    // Different frequencies for different types
    const frequencies: Record<NotificationType, number> = {
      success: 800,
      error: 400,
      info: 600,
      warning: 500,
    };
    
    oscillator.frequency.value = frequencies[type];
    oscillator.type = 'sine';
    gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.2);
  } catch (error) {
    // Silently fail if audio context is not available
    console.debug('Audio notification not available:', error);
  }
};

export const useNotificationStore = create<NotificationState>()(
  persist(
    (set, get) => ({
      notifications: [],
      preferences: defaultPreferences,
      permission: typeof window !== 'undefined' && 'Notification' in window
        ? Notification.permission
        : 'denied',

      addNotification: (notification) => {
        const id = `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        const newNotification: Notification = {
          ...notification,
          id,
          timestamp: new Date(),
          duration: notification.duration ?? 5000,
        };

        set((state) => ({
          notifications: [...state.notifications, newNotification],
        }));

        const { preferences } = get();
        
        // Show browser notification
        if (preferences.desktopEnabled) {
          showBrowserNotification(newNotification, preferences);
        }
        
        // Play sound
        playNotificationSound(newNotification.type, preferences);

        // Auto-remove after duration
        if (!newNotification.persistent && newNotification.duration && newNotification.duration > 0) {
          setTimeout(() => {
            get().removeNotification(id);
          }, newNotification.duration);
        }

        return id;
      },

      removeNotification: (id) => {
        set((state) => ({
          notifications: state.notifications.filter((n) => n.id !== id),
        }));
      },

      clearAll: () => {
        set({ notifications: [] });
      },

      requestPermission: async () => {
        if (typeof window === 'undefined' || !('Notification' in window)) {
          return 'denied';
        }

        try {
          const permission = await Notification.requestPermission();
          set({ permission });
          return permission;
        } catch (error) {
          console.error('Error requesting notification permission:', error);
          return 'denied';
        }
      },

      checkPermission: () => {
        if (typeof window === 'undefined' || !('Notification' in window)) {
          return 'denied';
        }
        const permission = Notification.permission;
        set({ permission });
        return permission;
      },

      updatePreferences: (newPreferences) => {
        set((state) => ({
          preferences: { ...state.preferences, ...newPreferences },
        }));
      },

      resetPreferences: () => {
        set({ preferences: defaultPreferences });
      },

      // Helper methods
      showSuccess: (title, message, options) => {
        return get().addNotification({
          type: 'success',
          title,
          message,
          ...options,
        });
      },

      showError: (title, message, options) => {
        return get().addNotification({
          type: 'error',
          title,
          message,
          persistent: true, // Errors are persistent by default
          ...options,
        });
      },

      showInfo: (title, message, options) => {
        return get().addNotification({
          type: 'info',
          title,
          message,
          ...options,
        });
      },

      showWarning: (title, message, options) => {
        return get().addNotification({
          type: 'warning',
          title,
          message,
          ...options,
        });
      },
    }),
    {
      name: 'notification-storage',
      partialize: (state) => ({
        preferences: state.preferences,
      }),
    }
  )
);

