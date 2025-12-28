/**
 * Statistics Card Component
 */
interface StatCardProps {
  title: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon?: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
}

export function StatCard({ title, value, change, changeLabel, icon, trend }: StatCardProps) {
  const trendColor =
    trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-600';
  const trendIcon =
    trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→';

  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">{value}</p>
          {change !== undefined && (
            <div className="mt-2 flex items-center">
              <span className={`text-sm font-medium ${trendColor}`}>
                {trendIcon} {Math.abs(change)}%
              </span>
              {changeLabel && (
                <span className="ml-2 text-sm text-gray-500">{changeLabel}</span>
              )}
            </div>
          )}
        </div>
        {icon && <div className="ml-4 text-gray-400">{icon}</div>}
      </div>
    </div>
  );
}

