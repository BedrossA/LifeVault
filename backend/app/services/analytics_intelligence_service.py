"""Advanced analytics intelligence services"""
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import logging
from scipy import stats
from scipy.stats import pearsonr
import math

logger = logging.getLogger(__name__)

class CorrelationDetectionService:
    """Service for detecting correlations in analytics data"""
    
    @staticmethod
    def calculate_correlation(
        data1: List[float],
        data2: List[float]
    ) -> Dict[str, float]:
        """
        Calculate Pearson correlation coefficient between two datasets
        
        Args:
            data1: First dataset
            data2: Second dataset (must be same length as data1)
            
        Returns:
            Dictionary with correlation coefficient and p-value
        """
        try:
            if len(data1) != len(data2) or len(data1) < 2:
                return {
                    'correlation': 0.0,
                    'p_value': 1.0,
                    'strength': 'none',
                    'significance': False
                }
            
            correlation, p_value = pearsonr(data1, data2)
            
            # Determine strength
            abs_corr = abs(correlation)
            if abs_corr >= 0.7:
                strength = 'strong'
            elif abs_corr >= 0.4:
                strength = 'moderate'
            elif abs_corr >= 0.2:
                strength = 'weak'
            else:
                strength = 'none'
            
            return {
                'correlation': float(correlation),
                'p_value': float(p_value),
                'strength': strength,
                'significance': p_value < 0.05
            }
        except Exception as e:
            logger.error(f"Error calculating correlation: {e}")
            return {
                'correlation': 0.0,
                'p_value': 1.0,
                'strength': 'none',
                'significance': False
            }
    
    @staticmethod
    def find_correlations(
        entries: List[Dict],
        metrics: List[str]
    ) -> List[Dict[str, any]]:
        """
        Find correlations between different metrics
        
        Args:
            entries: List of analytics entries
            metrics: List of metric names to analyze
            
        Returns:
            List of correlation results
        """
        try:
            # Group entries by timestamp
            by_timestamp = defaultdict(lambda: {})
            for entry in entries:
                ts = entry.get('timestamp')
                if ts:
                    for metric in metrics:
                        if metric in entry:
                            by_timestamp[ts][metric] = entry[metric]
            
            # Extract time series for each metric
            time_series = {}
            for metric in metrics:
                values = []
                for ts in sorted(by_timestamp.keys()):
                    if metric in by_timestamp[ts]:
                        values.append(float(by_timestamp[ts][metric]))
                    else:
                        values.append(None)
                # Remove None values
                time_series[metric] = [v for v in values if v is not None]
            
            # Calculate pairwise correlations
            correlations = []
            metric_list = list(time_series.keys())
            
            for i in range(len(metric_list)):
                for j in range(i + 1, len(metric_list)):
                    metric1 = metric_list[i]
                    metric2 = metric_list[j]
                    
                    data1 = time_series[metric1]
                    data2 = time_series[metric2]
                    
                    # Align data lengths
                    min_len = min(len(data1), len(data2))
                    if min_len >= 2:
                        data1_aligned = data1[:min_len]
                        data2_aligned = data2[:min_len]
                        
                        corr_result = CorrelationDetectionService.calculate_correlation(
                            data1_aligned, data2_aligned
                        )
                        
                        if corr_result['significance']:
                            correlations.append({
                                'metric1': metric1,
                                'metric2': metric2,
                                **corr_result
                            })
            
            # Sort by absolute correlation
            correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
            
            return correlations
            
        except Exception as e:
            logger.error(f"Error finding correlations: {e}")
            return []


class AnomalyDetectionService:
    """Service for detecting anomalies in analytics data"""
    
    @staticmethod
    def detect_anomalies_zscore(
        values: List[float],
        threshold: float = 3.0
    ) -> List[Dict[str, any]]:
        """
        Detect anomalies using Z-score method
        
        Args:
            values: List of values to analyze
            threshold: Z-score threshold (default 3.0)
            
        Returns:
            List of detected anomalies with indices and scores
        """
        try:
            if len(values) < 3:
                return []
            
            mean = np.mean(values)
            std = np.std(values)
            
            if std == 0:
                return []
            
            anomalies = []
            for i, value in enumerate(values):
                z_score = abs((value - mean) / std)
                if z_score > threshold:
                    anomalies.append({
                        'index': i,
                        'value': float(value),
                        'z_score': float(z_score),
                        'severity': 'high' if z_score > 4.0 else 'medium'
                    })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []
    
    @staticmethod
    def detect_anomalies_iqr(
        values: List[float]
    ) -> List[Dict[str, any]]:
        """
        Detect anomalies using Interquartile Range (IQR) method
        
        Args:
            values: List of values to analyze
            
        Returns:
            List of detected anomalies
        """
        try:
            if len(values) < 4:
                return []
            
            q1 = np.percentile(values, 25)
            q3 = np.percentile(values, 75)
            iqr = q3 - q1
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            anomalies = []
            for i, value in enumerate(values):
                if value < lower_bound or value > upper_bound:
                    anomalies.append({
                        'index': i,
                        'value': float(value),
                        'lower_bound': float(lower_bound),
                        'upper_bound': float(upper_bound),
                        'severity': 'medium'
                    })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting IQR anomalies: {e}")
            return []
    
    @staticmethod
    def detect_anomalies_in_entries(
        entries: List[Dict],
        metric: str,
        method: str = 'zscore'
    ) -> List[Dict[str, any]]:
        """
        Detect anomalies in analytics entries for a specific metric
        
        Args:
            entries: List of analytics entries
            metric: Metric name to analyze
            method: Detection method ('zscore' or 'iqr')
            
        Returns:
            List of anomalies with entry details
        """
        try:
            # Extract values
            values = []
            entry_map = []
            for entry in entries:
                if metric in entry:
                    try:
                        value = float(entry[metric])
                        values.append(value)
                        entry_map.append(entry)
                    except (ValueError, TypeError):
                        continue
            
            if len(values) < 3:
                return []
            
            # Detect anomalies
            if method == 'iqr':
                anomaly_indices = AnomalyDetectionService.detect_anomalies_iqr(values)
            else:
                anomaly_indices = AnomalyDetectionService.detect_anomalies_zscore(values)
            
            # Map back to entries
            anomalies = []
            for anomaly in anomaly_indices:
                idx = anomaly['index']
                if idx < len(entry_map):
                    anomaly_entry = {
                        **anomaly,
                        'entry': entry_map[idx],
                        'timestamp': entry_map[idx].get('timestamp')
                    }
                    anomalies.append(anomaly_entry)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies in entries: {e}")
            return []


class PatternRecognitionService:
    """Service for recognizing patterns in analytics data"""
    
    @staticmethod
    def detect_seasonality(
        values: List[float],
        timestamps: List[datetime]
    ) -> Dict[str, any]:
        """
        Detect seasonal patterns (daily, weekly, monthly)
        
        Args:
            values: List of values
            timestamps: Corresponding timestamps
            
        Returns:
            Dictionary with detected patterns
        """
        try:
            if len(values) < 7:
                return {'patterns': []}
            
            patterns = []
            
            # Daily pattern (hour of day)
            hour_values = defaultdict(list)
            for i, ts in enumerate(timestamps):
                if i < len(values):
                    hour_values[ts.hour].append(values[i])
            
            if len(hour_values) >= 3:
                hour_avg = {h: np.mean(vals) for h, vals in hour_values.items()}
                patterns.append({
                    'type': 'daily',
                    'pattern': hour_avg,
                    'strength': 'moderate'
                })
            
            # Weekly pattern (day of week)
            day_values = defaultdict(list)
            for i, ts in enumerate(timestamps):
                if i < len(values):
                    day_values[ts.weekday()].append(values[i])
            
            if len(day_values) >= 3:
                day_avg = {d: np.mean(vals) for d, vals in day_values.items()}
                patterns.append({
                    'type': 'weekly',
                    'pattern': day_avg,
                    'strength': 'moderate'
                })
            
            return {'patterns': patterns}
            
        except Exception as e:
            logger.error(f"Error detecting seasonality: {e}")
            return {'patterns': []}
    
    @staticmethod
    def detect_trend(
        values: List[float],
        timestamps: List[datetime]
    ) -> Dict[str, any]:
        """
        Detect trend (increasing, decreasing, stable)
        
        Args:
            values: List of values
            timestamps: Corresponding timestamps
            
        Returns:
            Dictionary with trend information
        """
        try:
            if len(values) < 2:
                return {'direction': 'stable', 'slope': 0.0}
            
            # Simple linear regression
            x = np.arange(len(values))
            slope, intercept = np.polyfit(x, values, 1)
            
            # Calculate R-squared
            y_pred = slope * x + intercept
            ss_res = np.sum((values - y_pred) ** 2)
            ss_tot = np.sum((values - np.mean(values)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            # Determine direction
            if abs(slope) < 0.01:
                direction = 'stable'
            elif slope > 0:
                direction = 'increasing'
            else:
                direction = 'decreasing'
            
            return {
                'direction': direction,
                'slope': float(slope),
                'r_squared': float(r_squared),
                'strength': 'strong' if r_squared > 0.7 else 'moderate' if r_squared > 0.4 else 'weak'
            }
            
        except Exception as e:
            logger.error(f"Error detecting trend: {e}")
            return {'direction': 'stable', 'slope': 0.0}


class PredictiveAnalyticsService:
    """Service for basic predictive analytics"""
    
    @staticmethod
    def simple_linear_forecast(
        values: List[float],
        periods: int = 7
    ) -> List[float]:
        """
        Simple linear forecast using linear regression
        
        Args:
            values: Historical values
            periods: Number of periods to forecast
            
        Returns:
            List of forecasted values
        """
        try:
            if len(values) < 2:
                # If not enough data, return last value repeated
                return [values[-1] if values else 0.0] * periods
            
            x = np.arange(len(values))
            slope, intercept = np.polyfit(x, values, 1)
            
            # Forecast future values
            forecast = []
            for i in range(periods):
                future_x = len(values) + i
                forecast.append(slope * future_x + intercept)
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error in linear forecast: {e}")
            return [0.0] * periods
    
    @staticmethod
    def moving_average_forecast(
        values: List[float],
        periods: int = 7,
        window: int = 3
    ) -> List[float]:
        """
        Forecast using moving average
        
        Args:
            values: Historical values
            periods: Number of periods to forecast
            window: Moving average window size
            
        Returns:
            List of forecasted values
        """
        try:
            if len(values) < window:
                return [np.mean(values) if values else 0.0] * periods
            
            # Calculate moving average
            ma = np.convolve(values, np.ones(window)/window, mode='valid')
            last_ma = ma[-1] if len(ma) > 0 else np.mean(values)
            
            # Forecast as constant (last moving average)
            return [last_ma] * periods
            
        except Exception as e:
            logger.error(f"Error in moving average forecast: {e}")
            return [0.0] * periods
    
    @staticmethod
    def forecast_with_confidence(
        values: List[float],
        periods: int = 7,
        method: str = 'linear'
    ) -> Dict[str, any]:
        """
        Forecast with confidence intervals
        
        Args:
            values: Historical values
            periods: Number of periods to forecast
            method: Forecast method ('linear' or 'moving_average')
            
        Returns:
            Dictionary with forecast and confidence intervals
        """
        try:
            if method == 'moving_average':
                forecast = PredictiveAnalyticsService.moving_average_forecast(values, periods)
            else:
                forecast = PredictiveAnalyticsService.simple_linear_forecast(values, periods)
            
            # Calculate confidence intervals (simple approach)
            std_dev = np.std(values) if len(values) > 1 else 0.0
            confidence_upper = [f + 1.96 * std_dev for f in forecast]
            confidence_lower = [f - 1.96 * std_dev for f in forecast]
            
            return {
                'forecast': forecast,
                'confidence_upper': confidence_upper,
                'confidence_lower': confidence_lower,
                'method': method
            }
            
        except Exception as e:
            logger.error(f"Error in forecast with confidence: {e}")
            return {
                'forecast': [0.0] * periods,
                'confidence_upper': [0.0] * periods,
                'confidence_lower': [0.0] * periods,
                'method': method
            }


class RecommendationService:
    """Service for generating smart recommendations"""
    
    @staticmethod
    def generate_recommendations(
        entries: List[Dict],
        goals: List[Dict],
        trends: List[Dict]
    ) -> List[Dict[str, any]]:
        """
        Generate smart recommendations based on data
        
        Args:
            entries: Analytics entries
            goals: User goals
            trends: Trend analysis results
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        try:
            # Analyze goals progress
            for goal in goals:
                metric = goal.get('metric')
                target = goal.get('target_value', 0)
                deadline = goal.get('deadline')
                
                if not metric:
                    continue
                
                # Get recent entries for this metric
                recent_entries = [
                    e for e in entries
                    if e.get('metric') == metric
                ][-7:]  # Last 7 entries
                
                if not recent_entries:
                    continue
                
                current_avg = np.mean([float(e.get('value', 0)) for e in recent_entries])
                progress = (current_avg / target * 100) if target > 0 else 0
                
                # Generate recommendations based on progress
                if progress < 50:
                    recommendations.append({
                        'type': 'goal_progress',
                        'priority': 'high',
                        'title': f'Goal Progress Alert: {metric}',
                        'message': f'You are at {progress:.1f}% of your goal. Consider increasing activity.',
                        'action': 'increase_activity',
                        'metric': metric
                    })
                elif progress > 90:
                    recommendations.append({
                        'type': 'goal_progress',
                        'priority': 'low',
                        'title': f'Great Progress: {metric}',
                        'message': f'You are at {progress:.1f}% of your goal! Keep it up!',
                        'action': 'maintain',
                        'metric': metric
                    })
            
            # Analyze trends
            for trend in trends:
                direction = trend.get('direction')
                metric = trend.get('metric')
                
                if direction == 'decreasing' and trend.get('strength') == 'strong':
                    recommendations.append({
                        'type': 'trend_alert',
                        'priority': 'medium',
                        'title': f'Declining Trend: {metric}',
                        'message': f'{metric} is showing a strong decreasing trend. Consider reviewing your habits.',
                        'action': 'review_habits',
                        'metric': metric
                    })
            
            # Sort by priority
            priority_order = {'high': 3, 'medium': 2, 'low': 1}
            recommendations.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 0), reverse=True)
            
            return recommendations[:10]  # Return top 10
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []

