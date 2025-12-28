/**
 * Dashboard Page
 */
import { useAuthStore } from '../store/authStore';

export function DashboardPage() {
  const { user } = useAuthStore();

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <div className="card">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Welcome back, {user?.username || 'User'}!
          </h1>
          <p className="text-gray-600">
            This is your LifeVault dashboard. Your encrypted personal analytics platform.
          </p>
        </div>
      </div>
    </div>
  );
}

