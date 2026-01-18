/**
 * Predictive Chart Component (with trend line)
 */
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import type { ChartDataPoint } from '../../types/analytics';


interface PredictiveChartProps {
  historicalData: ChartDataPoint[];
  predictedData?: ChartDataPoint[];
  title?: string;
  color?: string;
  dataKey?: string;
  predictionColor?: string;
}

export function PredictiveChart({
  historicalData,
  predictedData,
  title,
  color = '#0ea5e9',
  predictionColor = '#f59e0b',
}: PredictiveChartProps) {
  // Combine historical and predicted data
  const allData = [...historicalData];
  if (predictedData) {
    allData.push(...predictedData);
  }

  // Calculate trend line (simple linear regression)
  const calculateTrend = (data: ChartDataPoint[]) => {
    if (data.length < 2) return [];
    const n = data.length;
    const xValues = data.map((_, i) => i);
    const yValues = data.map((d) => d.value);
    
    const sumX = xValues.reduce((a, b) => a + b, 0);
    const sumY = yValues.reduce((a, b) => a + b, 0);
    const sumXY = xValues.reduce((sum, x, i) => sum + x * yValues[i], 0);
    const sumXX = xValues.reduce((sum, x) => sum + x * x, 0);
    
    const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;
    
    return data.map((d, i) => ({
      date: d.date,
      value: slope * i + intercept,
    }));
  };

  const trendData = calculateTrend(historicalData);
  const lastHistoricalIndex = historicalData.length - 1;

  return (
    <div className="card">
      {title && <h3 className="text-lg font-semibold mb-4">{title}</h3>}
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={allData}>
          <CartesianGrid strokeDasharray="3 3" />
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
            dataKey="value"
            stroke={color}
            strokeWidth={2}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
            name="Historical"
          />
          {predictedData && predictedData.length > 0 && (
            <Line
              type="monotone"
              dataKey="value"
              stroke={predictionColor}
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={{ r: 4 }}
              name="Predicted"
              data={predictedData}
            />
          )}
          <Line
            type="monotone"
            dataKey="value"
            stroke="#94a3b8"
            strokeWidth={1}
            strokeDasharray="3 3"
            dot={false}
            name="Trend"
            data={trendData}
          />
          {lastHistoricalIndex >= 0 && (
            <ReferenceLine
              x={historicalData[lastHistoricalIndex]?.date}
              stroke="#64748b"
              strokeDasharray="2 2"
            />
          )}
        </LineChart>
      </ResponsiveContainer>
      <div className="mt-2 text-xs text-gray-500 text-center">
        {predictedData && predictedData.length > 0 && (
          <p>Dashed line indicates predicted values based on historical trends</p>
        )}
      </div>
    </div>
  );
}

