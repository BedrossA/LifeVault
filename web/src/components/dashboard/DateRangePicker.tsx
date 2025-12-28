/**
 * Date Range Picker Component
 */
import { useState } from 'react';
import { format, subDays, subMonths, subWeeks } from 'date-fns';
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
    <div className="flex flex-wrap items-center gap-4">
      <div className="flex gap-2">
        <button
          onClick={() => handleQuickSelect(7)}
          className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
        >
          Last 7 days
        </button>
        <button
          onClick={() => handleQuickSelect(30)}
          className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
        >
          Last 30 days
        </button>
        <button
          onClick={() => handleQuickSelect(90)}
          className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
        >
          Last 90 days
        </button>
        <button
          onClick={() => handleQuickSelect(365)}
          className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
        >
          Last year
        </button>
      </div>
      <div className="flex items-center gap-2">
        <input
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
          className="px-3 py-1 text-sm border border-gray-300 rounded"
        />
        <span className="text-gray-500">to</span>
        <input
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
          className="px-3 py-1 text-sm border border-gray-300 rounded"
        />
        <button
          onClick={handleCustomRange}
          className="px-3 py-1 text-sm bg-primary-600 text-white rounded hover:bg-primary-700"
        >
          Apply
        </button>
      </div>
    </div>
  );
}

