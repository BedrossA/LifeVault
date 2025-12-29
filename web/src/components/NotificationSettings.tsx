/**
 * Notification Settings Component
 */
import { useNotificationStore } from '../store/notificationStore';
import { useState } from 'react';

export function NotificationSettings() {
  const {
    preferences,
    permission,
    requestPermission,
    checkPermission,
    updatePreferences,
    resetPreferences,
  } = useNotificationStore();

  const [isRequesting, setIsRequesting] = useState(false);

  const handleRequestPermission = async () => {
    setIsRequesting(true);
    try {
      await requestPermission();
    } finally {
      setIsRequesting(false);
    }
  };

  const handleToggle = (key: keyof typeof preferences, subKey?: string) => {
    if (subKey) {
      updatePreferences({
        [key]: {
          ...(preferences[key] as any),
          [subKey]: !(preferences[key] as any)[subKey],
        },
      });
    } else {
      updatePreferences({
        [key]: !preferences[key],
      });
    }
  };

  const handleTypeToggle = (type: 'success' | 'error' | 'info' | 'warning') => {
    updatePreferences({
      types: {
        ...preferences.types,
        [type]: !preferences.types[type],
      },
    });
  };

  const handleQuietHoursToggle = (field: 'enabled' | 'start' | 'end', value?: string) => {
    if (field === 'enabled') {
      updatePreferences({
        quietHours: {
          ...preferences.quietHours,
          enabled: !preferences.quietHours.enabled,
        },
      });
    } else if (value) {
      updatePreferences({
        quietHours: {
          ...preferences.quietHours,
          [field]: value,
        },
      });
    }
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">Notification Settings</h2>
        <button
          onClick={resetPreferences}
          className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100"
        >
          Reset to Defaults
        </button>
      </div>

      <div className="space-y-6">
        {/* Browser Permission */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Browser Notifications
            </label>
            <span className={`text-xs px-2 py-1 rounded ${
              permission === 'granted'
                ? 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-300'
                : permission === 'denied'
                ? 'bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-300'
                : 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-300'
            }`}>
              {permission === 'granted' ? 'Granted' : permission === 'denied' ? 'Denied' : 'Default'}
            </span>
          </div>
          {permission !== 'granted' && (
            <button
              onClick={handleRequestPermission}
              disabled={isRequesting || permission === 'denied'}
              className="btn btn-primary text-sm mt-2"
            >
              {isRequesting ? 'Requesting...' : 'Request Permission'}
            </button>
          )}
          {permission === 'denied' && (
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
              Permission denied. Please enable notifications in your browser settings.
            </p>
          )}
        </div>

        {/* General Settings */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">General Settings</h3>
          
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Enable Browser Notifications
              </label>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Show desktop notifications
              </p>
            </div>
            <button
              onClick={() => handleToggle('browserNotifications')}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                preferences.browserNotifications
                  ? 'bg-primary-600'
                  : 'bg-gray-200 dark:bg-gray-700'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  preferences.browserNotifications ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Sound Notifications
              </label>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Play sound when notifications appear
              </p>
            </div>
            <button
              onClick={() => handleToggle('soundEnabled')}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                preferences.soundEnabled
                  ? 'bg-primary-600'
                  : 'bg-gray-200 dark:bg-gray-700'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  preferences.soundEnabled ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Desktop Notifications
              </label>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Show system desktop notifications
              </p>
            </div>
            <button
              onClick={() => handleToggle('desktopEnabled')}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                preferences.desktopEnabled
                  ? 'bg-primary-600'
                  : 'bg-gray-200 dark:bg-gray-700'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  preferences.desktopEnabled ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>

        {/* Notification Types */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Notification Types</h3>
          
          {(['success', 'error', 'info', 'warning'] as const).map((type) => (
            <div key={type} className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300 capitalize">
                {type} Notifications
              </label>
              <button
                onClick={() => handleTypeToggle(type)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  preferences.types[type]
                    ? 'bg-primary-600'
                    : 'bg-gray-200 dark:bg-gray-700'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    preferences.types[type] ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          ))}
        </div>

        {/* Quiet Hours */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Quiet Hours</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Suppress notifications during these hours
              </p>
            </div>
            <button
              onClick={() => handleQuietHoursToggle('enabled')}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                preferences.quietHours.enabled
                  ? 'bg-primary-600'
                  : 'bg-gray-200 dark:bg-gray-700'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  preferences.quietHours.enabled ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          {preferences.quietHours.enabled && (
            <div className="grid grid-cols-2 gap-4 pl-4 border-l-2 border-gray-200 dark:border-gray-700">
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Start Time
                </label>
                <input
                  type="time"
                  value={preferences.quietHours.start}
                  onChange={(e) => handleQuietHoursToggle('start', e.target.value)}
                  className="input text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                  End Time
                </label>
                <input
                  type="time"
                  value={preferences.quietHours.end}
                  onChange={(e) => handleQuietHoursToggle('end', e.target.value)}
                  className="input text-sm"
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

