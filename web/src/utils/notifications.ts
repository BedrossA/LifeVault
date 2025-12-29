/**
 * Notification utility functions
 * Convenience wrappers for common notification patterns
 */
import { useNotificationStore } from '../store/notificationStore';

/**
 * Show a success notification
 */
export const notifySuccess = (title: string, message?: string) => {
  return useNotificationStore.getState().showSuccess(title, message);
};

/**
 * Show an error notification
 */
export const notifyError = (title: string, message?: string) => {
  return useNotificationStore.getState().showError(title, message);
};

/**
 * Show an info notification
 */
export const notifyInfo = (title: string, message?: string) => {
  return useNotificationStore.getState().showInfo(title, message);
};

/**
 * Show a warning notification
 */
export const notifyWarning = (title: string, message?: string) => {
  return useNotificationStore.getState().showWarning(title, message);
};

