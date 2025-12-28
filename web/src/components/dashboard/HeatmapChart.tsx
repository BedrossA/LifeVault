/**
 * Heatmap Chart Component
 */
import { format, eachDayOfInterval, startOfWeek, endOfWeek, isSameDay } from 'date-fns';
import type { ChartDataPoint } from '../../types/analytics';

interface HeatmapChartProps {
  data: ChartDataPoint[];
  title?: string;
  startDate: Date;
  endDate: Date;
}

export function HeatmapChart({ data, title, startDate, endDate }: HeatmapChartProps) {
  const days = eachDayOfInterval({ start: startDate, end: endDate });
  const weeks: Date[][] = [];
  
  // Group days into weeks
  let currentWeek: Date[] = [];
  days.forEach((day) => {
    if (currentWeek.length === 0 || day.getDay() === 0) {
      if (currentWeek.length > 0) weeks.push(currentWeek);
      currentWeek = [day];
    } else {
      currentWeek.push(day);
    }
  });
  if (currentWeek.length > 0) weeks.push(currentWeek);

  const getIntensity = (date: Date): number => {
    const entry = data.find((d) => isSameDay(new Date(d.date), date));
    if (!entry) return 0;
    const maxValue = Math.max(...data.map((d) => d.value));
    return maxValue > 0 ? (entry.value / maxValue) * 100 : 0;
  };

  const getColor = (intensity: number): string => {
    if (intensity === 0) return 'bg-gray-100';
    if (intensity < 25) return 'bg-blue-200';
    if (intensity < 50) return 'bg-blue-400';
    if (intensity < 75) return 'bg-blue-600';
    return 'bg-blue-800';
  };

  return (
    <div className="card">
      {title && <h3 className="text-lg font-semibold mb-4">{title}</h3>}
      <div className="overflow-x-auto">
        <div className="inline-block min-w-full">
          <div className="flex gap-1">
            {weeks.map((week, weekIndex) => (
              <div key={weekIndex} className="flex flex-col gap-1">
                {week.map((day, dayIndex) => {
                  const intensity = getIntensity(day);
                  return (
                    <div
                      key={dayIndex}
                      className={`w-3 h-3 rounded ${getColor(intensity)}`}
                      title={`${format(day, 'MMM dd')}: ${intensity.toFixed(0)}%`}
                    />
                  );
                })}
              </div>
            ))}
          </div>
        </div>
      </div>
      <div className="mt-4 flex items-center justify-between text-xs text-gray-500">
        <span>Less</span>
        <div className="flex gap-1">
          <div className="w-3 h-3 rounded bg-gray-100" />
          <div className="w-3 h-3 rounded bg-blue-200" />
          <div className="w-3 h-3 rounded bg-blue-400" />
          <div className="w-3 h-3 rounded bg-blue-600" />
          <div className="w-3 h-3 rounded bg-blue-800" />
        </div>
        <span>More</span>
      </div>
    </div>
  );
}

