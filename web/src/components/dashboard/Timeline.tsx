/**
 * Interactive Timeline Component
 */
import { format, parseISO } from 'date-fns';
import type { AnalyticsEntry } from '../../types/analytics';

interface TimelineProps {
  entries: AnalyticsEntry[];
  onEntryClick?: (entry: AnalyticsEntry) => void;
}

export function Timeline({ entries, onEntryClick }: TimelineProps) {
  const sortedEntries = [...entries].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4">Recent Activity Timeline</h3>
      <div className="space-y-4">
        {sortedEntries.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No entries yet</p>
        ) : (
          sortedEntries.map((entry, index) => (
            <div
              key={entry.id || index}
              className="flex items-start gap-4 pb-4 border-b border-gray-200 last:border-0 cursor-pointer hover:bg-gray-50 p-2 rounded transition-colors"
              onClick={() => onEntryClick?.(entry)}
            >
              <div className="flex-shrink-0 w-2 h-2 rounded-full bg-primary-600 mt-2" />
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {entry.metric.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                    </p>
                    <p className="text-xs text-gray-500 capitalize">{entry.category}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-gray-900">
                      {entry.value} {entry.unit || ''}
                    </p>
                    <p className="text-xs text-gray-500">
                      {format(parseISO(entry.timestamp), 'MMM dd, yyyy HH:mm')}
                    </p>
                  </div>
                </div>
                {entry.notes && (
                  <p className="mt-1 text-sm text-gray-600 line-clamp-2">{entry.notes}</p>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

