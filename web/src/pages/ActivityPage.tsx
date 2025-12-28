/**
 * Activity Page
 */
import { useEffect, useState } from 'react';
import { apiClient } from '../services/api';
import type { UserActivity, LoginHistory } from '../types';

export function ActivityPage() {
  const [activities, setActivities] = useState<UserActivity[]>([]);
  const [loginHistory, setLoginHistory] = useState<LoginHistory[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [activitiesData, historyData] = await Promise.all([
          apiClient.getUserActivity(20),
          apiClient.getLoginHistory(10),
        ]);
        setActivities(activitiesData);
        setLoginHistory(historyData);
      } catch (error) {
        console.error('Failed to fetch activity data:', error);
        // Set empty arrays on error to show empty state
        setActivities([]);
        setLoginHistory([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0 space-y-6">
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Activity</h2>
          <div className="space-y-2">
            {activities.length === 0 ? (
              <p className="text-gray-500">No activity recorded yet.</p>
            ) : (
              activities.map((activity, index) => (
                <div key={index} className="border-b border-gray-200 pb-2">
                  <div className="flex justify-between">
                    <span className="font-medium">{activity.action}</span>
                    <span className="text-sm text-gray-500">
                      {new Date(activity.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">{activity.category}</p>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Login History</h2>
          <div className="space-y-2">
            {loginHistory.length === 0 ? (
              <p className="text-gray-500">No login history available.</p>
            ) : (
              loginHistory.map((login, index) => (
                <div key={index} className="border-b border-gray-200 pb-2">
                  <div className="flex justify-between">
                    <span className={login.success ? 'text-green-600' : 'text-red-600'}>
                      {login.success ? 'Successful' : 'Failed'} Login
                    </span>
                    <span className="text-sm text-gray-500">
                      {new Date(login.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">
                    {login.ip_address} • {login.user_agent || 'Unknown device'}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

