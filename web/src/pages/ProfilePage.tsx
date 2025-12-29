/**
 * Profile Page
 */
import { useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { NotificationSettings } from '../components/NotificationSettings';

type TabType = 'profile' | 'notifications';

export function ProfilePage() {
  const { user } = useAuthStore();
  const [activeTab, setActiveTab] = useState<TabType>('profile');

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        {/* Tabs */}
        <div className="mb-6 border-b border-gray-200 dark:border-gray-700">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('profile')}
              className={`${
                activeTab === 'profile'
                  ? 'border-primary-500 dark:border-primary-400 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Profile
            </button>
            <button
              onClick={() => setActiveTab('notifications')}
              className={`${
                activeTab === 'notifications'
                  ? 'border-primary-500 dark:border-primary-400 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Notifications
            </button>
          </nav>
        </div>

        {activeTab === 'profile' ? (
          <div className="card">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-6">Profile</h1>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Username</label>
                <p className="mt-1 text-sm text-gray-900 dark:text-gray-100">{user?.username}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Email</label>
                <p className="mt-1 text-sm text-gray-900 dark:text-gray-100">{user?.email}</p>
              </div>
              {user?.full_name && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Full Name</label>
                  <p className="mt-1 text-sm text-gray-900 dark:text-gray-100">{user.full_name}</p>
                </div>
              )}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Status</label>
                <p className="mt-1 text-sm text-gray-900 dark:text-gray-100">
                  {user?.is_active ? (
                    <span className="text-green-600 dark:text-green-400">Active</span>
                  ) : (
                    <span className="text-red-600 dark:text-red-400">Inactive</span>
                  )}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Verified</label>
                <p className="mt-1 text-sm text-gray-900 dark:text-gray-100">
                  {user?.is_verified ? (
                    <span className="text-green-600 dark:text-green-400">Verified</span>
                  ) : (
                    <span className="text-yellow-600 dark:text-yellow-400">Not Verified</span>
                  )}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Member Since</label>
                <p className="mt-1 text-sm text-gray-900 dark:text-gray-100">
                  {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                </p>
              </div>
            </div>
          </div>
        ) : (
          <NotificationSettings />
        )}
      </div>
    </div>
  );
}

