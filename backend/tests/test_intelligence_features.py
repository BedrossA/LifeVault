"""Test scripts for intelligence features"""
import pytest
import numpy as np
from datetime import datetime, timedelta
from app.services.analytics_intelligence_service import (
    CorrelationDetectionService,
    AnomalyDetectionService,
    PatternRecognitionService,
    PredictiveAnalyticsService,
    RecommendationService
)
from app.services.emotion_detection_service import EmotionDetectionService

class TestCorrelationDetection:
    """Test correlation detection"""
    
    def test_positive_correlation(self):
        """Test positive correlation detection"""
        data1 = [1, 2, 3, 4, 5]
        data2 = [2, 4, 6, 8, 10]
        
        result = CorrelationDetectionService.calculate_correlation(data1, data2)
        
        assert result['correlation'] > 0.9
        assert result['strength'] == 'strong'
        assert result['significance'] == True
    
    def test_negative_correlation(self):
        """Test negative correlation detection"""
        data1 = [1, 2, 3, 4, 5]
        data2 = [10, 8, 6, 4, 2]
        
        result = CorrelationDetectionService.calculate_correlation(data1, data2)
        
        assert result['correlation'] < -0.9
        assert result['strength'] == 'strong'
    
    def test_no_correlation(self):
        """Test no correlation"""
        data1 = [1, 2, 3, 4, 5]
        data2 = [5, 2, 8, 1, 9]  # Random
        
        result = CorrelationDetectionService.calculate_correlation(data1, data2)
        
        assert abs(result['correlation']) < 0.5


class TestAnomalyDetection:
    """Test anomaly detection"""
    
    def test_zscore_anomaly_detection(self):
        """Test Z-score anomaly detection"""
        values = [1, 2, 3, 4, 5, 100]  # 100 is an anomaly
        
        anomalies = AnomalyDetectionService.detect_anomalies_zscore(values, threshold=2.0)
        
        assert len(anomalies) > 0
        assert anomalies[0]['value'] == 100.0
    
    def test_iqr_anomaly_detection(self):
        """Test IQR anomaly detection"""
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 50]  # 50 is an anomaly
        
        anomalies = AnomalyDetectionService.detect_anomalies_iqr(values)
        
        assert len(anomalies) > 0


class TestPatternRecognition:
    """Test pattern recognition"""
    
    def test_trend_detection_increasing(self):
        """Test increasing trend detection"""
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        timestamps = [datetime.now() + timedelta(days=i) for i in range(10)]
        
        trend = PatternRecognitionService.detect_trend(values, timestamps)
        
        assert trend['direction'] == 'increasing'
        assert trend['slope'] > 0
    
    def test_trend_detection_decreasing(self):
        """Test decreasing trend detection"""
        values = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        timestamps = [datetime.now() + timedelta(days=i) for i in range(10)]
        
        trend = PatternRecognitionService.detect_trend(values, timestamps)
        
        assert trend['direction'] == 'decreasing'
        assert trend['slope'] < 0


class TestPredictiveAnalytics:
    """Test predictive analytics"""
    
    def test_linear_forecast(self):
        """Test linear forecast"""
        values = [1, 2, 3, 4, 5]
        
        forecast = PredictiveAnalyticsService.simple_linear_forecast(values, periods=3)
        
        assert len(forecast) == 3
        assert forecast[0] > values[-1]  # Should be increasing
    
    def test_moving_average_forecast(self):
        """Test moving average forecast"""
        values = [1, 2, 3, 4, 5, 6, 7]
        
        forecast = PredictiveAnalyticsService.moving_average_forecast(values, periods=3, window=3)
        
        assert len(forecast) == 3
        assert all(f > 0 for f in forecast)


class TestEmotionDetection:
    """Test emotion detection"""
    
    def test_emotion_detection_landmarks(self):
        """Test emotion detection from landmarks"""
        # Mock facial landmarks
        landmarks = {
            'left_eye': [(10, 20), (15, 20), (20, 20), (15, 25)],
            'right_eye': [(30, 20), (35, 20), (40, 20), (35, 25)],
            'nose_tip': [(25, 30)],
            'top_lip': [(20, 35), (25, 35), (30, 35)],
            'bottom_lip': [(20, 40), (25, 40), (30, 40)],
            'left_eyebrow': [(10, 15), (15, 15), (20, 15)],
            'right_eyebrow': [(30, 15), (35, 15), (40, 15)]
        }
        
        emotions = EmotionDetectionService.detect_emotion_from_landmarks(landmarks)
        
        assert 'happy' in emotions
        assert 'sad' in emotions
        assert 'neutral' in emotions
        assert sum(emotions.values()) > 0.9  # Should sum to ~1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

