/**
 * Date Range Picker Component
 */
import { useState } from 'react';
import { format, subDays } from 'date-fns';
import type { DateRange } from '../../types/analytics';

interface DateRangePickerProps {
  onRangeChange: (range: DateRange) => void;
  defaultRange?: DateRange;
}

export function DateRangePicker({ onRangeChange, defaultRange }: DateRangePickerProps) {
  const [startDate, setStartDate] = useState(
    defaultRange?.start || format(subDays(new Date(), 30), 'yyyy-MM-dd')
  );
  const [endDate, setEndDate] = useState(
    defaultRange?.end || format(new Date(), 'yyyy-MM-dd')
  );

  const handleQuickSelect = (days: number) => {
    const end = new Date();
    const start = subDays(end, days);
    const range = {
      start: format(start, 'yyyy-MM-dd'),
      end: format(end, 'yyyy-MM-dd'),
    };
    setStartDate(range.start);
    setEndDate(range.end);
    onRangeChange(range);
  };

  const handleCustomRange = () => {
    onRangeChange({ start: startDate, end: endDate });
  };

  return (
    <div className="flex flex-col sm:flex-row flex-wrap items-start sm:items-center gap-4">
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => handleQuickSelect(7)}
          className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
        >
          Last 7 days
        </button>
        <button
          onClick={() => handleQuickSelect(30)}
          className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
        >
          Last 30 days
        </button>
        <button
          onClick={() => handleQuickSelect(90)}
          className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
        >
          Last 90 days
        </button>
        <button
          onClick={() => handleQuickSelect(365)}
          className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
        >
          Last year
        </button>
      </div>
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 w-full sm:w-auto">
        <div className="flex items-center gap-2 flex-1 sm:flex-initial">
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded flex-1 sm:flex-initial min-w-0 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          />
          <span className="text-gray-500 dark:text-gray-400 whitespace-nowrap">to</span>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded flex-1 sm:flex-initial min-w-0 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          />
        </div>
        <button
          onClick={handleCustomRange}
          className="px-3 py-1 text-sm bg-primary-600 text-white rounded hover:bg-primary-700 whitespace-nowrap w-full sm:w-auto"
        >
          Apply
        </button>
      </div>
    </div>
  );
}

