/**
 * Goal Manager Component
 */
import { useState, FormEvent } from 'react';
import type { Goal, GoalCreate } from '../../types/analytics';

interface GoalManagerProps {
  goals: Goal[];
  onCreate: (goal: GoalCreate) => Promise<void>;
  onUpdate: (id: string, goal: Partial<GoalCreate>) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
}

export function GoalManager({ goals, onCreate, onUpdate, onDelete }: GoalManagerProps) {
  const [showForm, setShowForm] = useState(false);
  const [editingGoal, setEditingGoal] = useState<Goal | null>(null);
  const [formData, setFormData] = useState<GoalCreate>({
    metric: '',
    category: '',
    target_value: 0,
    unit: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      if (editingGoal) {
        await onUpdate(editingGoal.id!, formData);
        setEditingGoal(null);
      } else {
        await onCreate(formData);
      }
      setShowForm(false);
      setFormData({ metric: '', category: '', target_value: 0, unit: '' });
    } catch (error) {
      console.error('Failed to save goal:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Goals</h3>
        <button
          onClick={() => {
            setShowForm(!showForm);
            setEditingGoal(null);
          }}
          className="btn btn-primary text-sm"
        >
          {showForm ? 'Cancel' : '+ New Goal'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-4 p-4 bg-gray-50 rounded-lg space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Metric</label>
              <input
                type="text"
                value={formData.metric}
                onChange={(e) => setFormData({ ...formData, metric: e.target.value })}
                className="input text-sm"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
              <input
                type="text"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="input text-sm"
                required
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Target Value</label>
              <input
                type="number"
                value={formData.target_value}
                onChange={(e) => setFormData({ ...formData, target_value: parseFloat(e.target.value) || 0 })}
                className="input text-sm"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Unit</label>
              <input
                type="text"
                value={formData.unit}
                onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
                className="input text-sm"
                placeholder="kg, km, etc."
              />
            </div>
          </div>
          <button type="submit" disabled={isSubmitting} className="btn btn-primary w-full text-sm">
            {isSubmitting ? 'Saving...' : editingGoal ? 'Update Goal' : 'Create Goal'}
          </button>
        </form>
      )}

      <div className="space-y-2">
        {goals.length === 0 ? (
          <p className="text-gray-500 text-center py-4">No goals set yet</p>
        ) : (
          goals.map((goal) => (
            <div key={goal.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
              <div className="flex-1">
                <p className="font-medium text-sm">{goal.metric}</p>
                <p className="text-xs text-gray-500 capitalize">{goal.category}</p>
              </div>
              <div className="text-right mr-4">
                <p className="text-sm font-semibold">
                  {goal.current_value} / {goal.target_value} {goal.unit}
                </p>
                <p className="text-xs text-gray-500">
                  {((goal.current_value / goal.target_value) * 100).toFixed(0)}%
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    setEditingGoal(goal);
                    setFormData({
                      metric: goal.metric,
                      category: goal.category,
                      target_value: goal.target_value,
                      unit: goal.unit || '',
                    });
                    setShowForm(true);
                  }}
                  className="text-xs text-primary-600 hover:text-primary-700"
                >
                  Edit
                </button>
                <button
                  onClick={() => onDelete(goal.id!)}
                  className="text-xs text-red-600 hover:text-red-700"
                >
                  Delete
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

