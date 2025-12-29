/**
 * Notification Container Component
 * Displays all active notifications
 */
import { useEffect } from 'react';
import { useNotificationStore } from '../store/notificationStore';
import type { Notification } from '../types/notification';

function NotificationItem({ notification }: { notification: Notification }) {
  const removeNotification = useNotificationStore((state) => state.removeNotification);

  const getIcon = () => {
    switch (notification.type) {
      case 'success':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'error':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'warning':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        );
      case 'info':
      default:
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };

  const getStyles = () => {
    switch (notification.type) {
      case 'success':
        return 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800 text-green-800 dark:text-green-300';
      case 'error':
        return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-800 dark:text-red-300';
      case 'warning':
        return 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800 text-yellow-800 dark:text-yellow-300';
      case 'info':
      default:
        return 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-300';
    }
  };

  return (
    <div
      className={`${getStyles()} border-l-4 rounded-lg shadow-lg p-4 mb-3 animate-in slide-in-from-right duration-300 max-w-md`}
      role="alert"
    >
      <div className="flex items-start">
        <div className="flex-shrink-0">{getIcon()}</div>
        <div className="ml-3 flex-1">
          <h4 className="text-sm font-semibold">{notification.title}</h4>
          {notification.message && (
            <p className="mt-1 text-sm opacity-90">{notification.message}</p>
          )}
          {notification.action && (
            <button
              onClick={() => {
                notification.action?.onClick();
                removeNotification(notification.id);
              }}
              className="mt-2 text-sm font-medium underline hover:no-underline"
            >
              {notification.action.label}
            </button>
          )}
        </div>
        <button
          onClick={() => removeNotification(notification.id)}
          className="ml-4 flex-shrink-0 text-current opacity-50 hover:opacity-100 transition-opacity"
          aria-label="Dismiss notification"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
}

export function NotificationContainer() {
  const notifications = useNotificationStore((state) => state.notifications);
  const checkPermission = useNotificationStore((state) => state.checkPermission);

  useEffect(() => {
    // Check permission on mount
    checkPermission();
  }, [checkPermission]);

  if (notifications.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-h-screen overflow-y-auto">
      {notifications.map((notification) => (
        <NotificationItem key={notification.id} notification={notification} />
      ))}
    </div>
  );
}

