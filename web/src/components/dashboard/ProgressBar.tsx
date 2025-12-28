/**
 * Goal Progress Bar Component
 */
interface ProgressBarProps {
  label: string;
  current: number;
  target: number;
  unit?: string;
  color?: string;
}

export function ProgressBar({ label, current, target, unit = '', color = 'bg-primary-600' }: ProgressBarProps) {
  const percentage = Math.min((current / target) * 100, 100);
  const isComplete = current >= target;

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-gray-700">{label}</span>
        <span className="text-sm font-semibold text-gray-900">
          {current.toLocaleString()} / {target.toLocaleString()} {unit}
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-4">
        <div
          className={`h-4 rounded-full transition-all duration-300 ${
            isComplete ? 'bg-green-600' : color
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <div className="mt-2 flex items-center justify-between">
        <span className="text-xs text-gray-500">{percentage.toFixed(1)}% complete</span>
        {isComplete && (
          <span className="text-xs font-medium text-green-600">Goal achieved! 🎉</span>
        )}
      </div>
    </div>
  );
}

