/**
 * Line Chart Component using Recharts
 */
import { LineChart as RechartsLineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { ChartDataPoint } from '../../types/analytics';

interface LineChartProps {
  data: ChartDataPoint[];
  title?: string;
  dataKey?: string;
  color?: string;
  showGrid?: boolean;
}

export function LineChart({
  data,
  title,
  dataKey = 'value',
  color = '#0ea5e9',
  showGrid = true,
}: LineChartProps) {
  return (
    <div className="card">
      {title && <h3 className="text-lg font-semibold mb-4">{title}</h3>}
      <ResponsiveContainer width="100%" height={300}>
        <RechartsLineChart data={data}>
          {showGrid && <CartesianGrid strokeDasharray="3 3" />}
          <XAxis
            dataKey="date"
            tickFormatter={(value) => {
              const date = new Date(value);
              return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            }}
          />
          <YAxis />
          <Tooltip
            labelFormatter={(value) => {
              const date = new Date(value);
              return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey={dataKey}
            stroke={color}
            strokeWidth={2}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
          />
        </RechartsLineChart>
      </ResponsiveContainer>
    </div>
  );
}

