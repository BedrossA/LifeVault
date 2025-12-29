/**
 * Analytics Data Entry Form
 */
import { useState, FormEvent } from 'react';
import type { AnalyticsEntryCreate } from '../../types/analytics';

interface DataEntryFormProps {
  onSubmit: (data: AnalyticsEntryCreate) => Promise<void>;
  onCancel?: () => void;
  categories?: string[];
  metrics?: string[];
}

export function DataEntryForm({
  onSubmit,
  onCancel,
  categories = ['health', 'fitness', 'productivity', 'finance', 'mood'],
  metrics = ['steps', 'calories', 'weight', 'hours', 'mood_score', 'expense'],
}: DataEntryFormProps) {
  const [formData, setFormData] = useState<AnalyticsEntryCreate>({
    category: categories[0] || '',
    metric: metrics[0] || '',
    value: 0,
    unit: '',
    notes: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await onSubmit(formData);
      // Reset form
      setFormData({
        category: categories[0] || '',
        metric: metrics[0] || '',
        value: 0,
        unit: '',
        notes: '',
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save entry');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">Add Analytics Entry</h3>
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label htmlFor="category" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Category
            </label>
            <select
              id="category"
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              className="input"
              required
            >
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat.charAt(0).toUpperCase() + cat.slice(1)}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="metric" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Metric
            </label>
            <select
              id="metric"
              value={formData.metric}
              onChange={(e) => setFormData({ ...formData, metric: e.target.value })}
              className="input"
              required
            >
              {metrics.map((m) => (
                <option key={m} value={m}>
                  {m.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label htmlFor="value" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Value
            </label>
            <input
              id="value"
              type="number"
              step="any"
              value={formData.value}
              onChange={(e) => setFormData({ ...formData, value: parseFloat(e.target.value) || 0 })}
              className="input"
              required
            />
          </div>

          <div>
            <label htmlFor="unit" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Unit (optional)
            </label>
            <input
              id="unit"
              type="text"
              value={formData.unit}
              onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
              className="input"
              placeholder="kg, km, hours, etc."
            />
          </div>
        </div>

        <div>
          <label htmlFor="notes" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Notes (optional)
          </label>
          <textarea
            id="notes"
            value={formData.notes}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            className="input"
            rows={3}
            placeholder="Additional notes about this entry..."
          />
        </div>

        <div className="flex flex-col sm:flex-row gap-2">
          <button
            type="submit"
            disabled={isSubmitting}
            className="btn btn-primary flex-1 w-full sm:w-auto"
          >
            {isSubmitting ? 'Saving...' : 'Save Entry'}
          </button>
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="btn btn-secondary w-full sm:w-auto"
            >
              Cancel
            </button>
          )}
        </div>
      </form>
    </div>
  );
}

