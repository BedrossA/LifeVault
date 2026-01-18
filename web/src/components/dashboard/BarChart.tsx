/**
 * Bar Chart Component using Recharts
 */
import { BarChart as RechartsBarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { memo } from 'react';

interface BarChartProps {
  data: Array<Record<string, string | number>>;
  title?: string;
  dataKey: string;
  xKey: string;
  colors?: string[];
  showGrid?: boolean;
}

export const BarChart = memo(function BarChart({
  data,
  title,
  dataKey,
  xKey,
  colors = ['#0ea5e9', '#10b981', '#f59e0b'],
  showGrid = true,
}: BarChartProps) {
  return (
    <div className="card">
      {title && <h3 className="text-lg font-semibold mb-4">{title}</h3>}
      <ResponsiveContainer width="100%" height={300}>
        <RechartsBarChart data={data}>
          {showGrid && <CartesianGrid strokeDasharray="3 3" />}
          <XAxis dataKey={xKey} />
          <YAxis />
          <Tooltip />
          <Legend />
          {Array.isArray(dataKey) ? (
            dataKey.map((key, index) => (
              <Bar key={key} dataKey={key} fill={colors[index % colors.length]} />
            ))
          ) : (
            <Bar dataKey={dataKey} fill={colors[0]} />
          )}
        </RechartsBarChart>
      </ResponsiveContainer>
    </div>
  );
}, (prevProps, nextProps) => {
  // Custom comparison
  return (
    JSON.stringify(prevProps.data) === JSON.stringify(nextProps.data) &&
    prevProps.title === nextProps.title &&
    prevProps.dataKey === nextProps.dataKey
  );
});

