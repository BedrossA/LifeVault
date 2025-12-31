# LifeVault Intelligence Features Documentation

## Overview

LifeVault now includes advanced AI-powered analytics features that provide deep insights into your personal data. These features include emotion detection, correlation analysis, anomaly detection, pattern recognition, predictive analytics, smart recommendations, goal tracking with milestones, and comprehensive activity logging.

## Features

### 1. Emotion Detection from Face Recognition

**Description:** Automatically detects emotions from facial expressions during face recognition.

**API Endpoint:** `POST /api/v1/face/recognize`

**Response includes:**
- `emotion`: Dominant emotion detected (happy, sad, angry, surprised, fearful, disgusted, neutral)
- `emotion_confidence`: Confidence score (0.0 to 1.0)
- `emotions`: Full probability distribution of all emotions

**Example Response:**
```json
{
  "recognized": true,
  "username": "john_doe",
  "confidence": 0.95,
  "emotion": "happy",
  "emotion_confidence": 0.78,
  "emotions": {
    "happy": 0.78,
    "neutral": 0.15,
    "sad": 0.05,
    "angry": 0.02
  }
}
```

**Usage:**
```bash
curl -X POST "http://localhost:8000/api/v1/face/recognize" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "image=@face.jpg"
```

### 2. Correlation Detection

**Description:** Identifies correlations between different metrics in your analytics data.

**API Endpoint:** `GET /api/v1/intelligence/correlations`

**Parameters:**
- `metrics`: Comma-separated list of metrics to analyze (e.g., "sleep_hours,exercise_minutes")
- `start_date`: Optional start date (ISO format)
- `end_date`: Optional end date (ISO format)

**Response:**
```json
[
  {
    "metric1": "sleep_hours",
    "metric2": "exercise_minutes",
    "correlation": 0.65,
    "p_value": 0.001,
    "strength": "moderate",
    "significance": true
  }
]
```

**Usage:**
```bash
curl "http://localhost:8000/api/v1/intelligence/correlations?metrics=sleep_hours,exercise_minutes" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Anomaly Detection

**Description:** Detects unusual values or patterns in your data that may indicate errors or significant events.

**API Endpoint:** `GET /api/v1/intelligence/anomalies/{metric}`

**Parameters:**
- `metric`: Metric name to analyze
- `method`: Detection method ("zscore" or "iqr")
- `start_date`: Optional start date
- `end_date`: Optional end date

**Response:**
```json
[
  {
    "index": 15,
    "value": 150.0,
    "z_score": 3.5,
    "severity": "high",
    "timestamp": "2024-01-15T10:30:00Z"
  }
]
```

**Usage:**
```bash
curl "http://localhost:8000/api/v1/intelligence/anomalies/sleep_hours?method=zscore" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Pattern Recognition

**Description:** Identifies patterns in your data such as trends, seasonality, and cycles.

**API Endpoint:** `GET /api/v1/intelligence/patterns/{metric}`

**Response:**
```json
{
  "seasonality": {
    "patterns": [
      {
        "type": "daily",
        "pattern": {
          "0": 7.5,
          "6": 8.0,
          "12": 7.0
        },
        "strength": "moderate"
      }
    ]
  },
  "trend": {
    "direction": "increasing",
    "slope": 0.15,
    "r_squared": 0.72,
    "strength": "strong"
  }
}
```

**Usage:**
```bash
curl "http://localhost:8000/api/v1/intelligence/patterns/sleep_hours" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Predictive Analytics

**Description:** Provides forecasts for future values based on historical data.

**API Endpoint:** `GET /api/v1/intelligence/forecast/{metric}`

**Parameters:**
- `metric`: Metric name to forecast
- `periods`: Number of periods to forecast (1-30)
- `method`: Forecast method ("linear" or "moving_average")
- `start_date`: Optional start date
- `end_date`: Optional end date

**Response:**
```json
{
  "forecast": [8.5, 8.6, 8.7, 8.8, 8.9, 9.0, 9.1],
  "confidence_upper": [9.5, 9.6, 9.7, 9.8, 9.9, 10.0, 10.1],
  "confidence_lower": [7.5, 7.6, 7.7, 7.8, 7.9, 8.0, 8.1],
  "method": "linear"
}
```

**Usage:**
```bash
curl "http://localhost:8000/api/v1/intelligence/forecast/sleep_hours?periods=7&method=linear" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6. Smart Recommendations

**Description:** Generates personalized recommendations based on your goals, trends, and activity patterns.

**API Endpoint:** `GET /api/v1/intelligence/recommendations`

**Response:**
```json
[
  {
    "type": "goal_progress",
    "priority": "high",
    "title": "Goal Progress Alert: exercise_minutes",
    "message": "You are at 45.2% of your goal. Consider increasing activity.",
    "action": "increase_activity",
    "metric": "exercise_minutes"
  }
]
```

**Usage:**
```bash
curl "http://localhost:8000/api/v1/intelligence/recommendations" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 7. Goal Tracking with Milestones

**Description:** Break down goals into smaller milestones for better tracking and motivation.

**Endpoints:**
- `POST /api/v1/goals/{goal_id}/milestones` - Create milestone
- `GET /api/v1/goals/{goal_id}/milestones` - Get milestones
- `PATCH /api/v1/milestones/{milestone_id}/progress` - Update progress
- `POST /api/v1/milestones/{milestone_id}/achieve` - Mark as achieved
- `DELETE /api/v1/milestones/{milestone_id}` - Delete milestone

**Create Milestone:**
```bash
curl -X POST "http://localhost:8000/api/v1/goals/{goal_id}/milestones" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "First 25%",
    "description": "Reach 25% of goal",
    "target_value": 25.0,
    "order": 1
  }'
```

### 8. Activity Logging System

**Description:** Comprehensive logging of all user activities for audit and analysis.

**Endpoints:**
- `GET /api/v1/intelligence/activities` - Get activity logs
- `GET /api/v1/intelligence/activities/stats` - Get activity statistics

**Get Activities:**
```bash
curl "http://localhost:8000/api/v1/intelligence/activities?limit=50&activity_type=face_enroll" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Get Activity Stats:**
```bash
curl "http://localhost:8000/api/v1/intelligence/activities/stats?days=30" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Implementation Details

### Backend Services

All intelligence features are implemented as services in `backend/app/services/`:

- `emotion_detection_service.py` - Emotion detection from facial landmarks
- `analytics_intelligence_service.py` - Correlation, anomaly, pattern, prediction, and recommendation services
- `activity_logging_service.py` - Activity logging and statistics

### Dependencies

New dependencies added:
- `scipy==1.11.4` - For statistical analysis (correlations, etc.)

### Database Models

New models:
- `GoalMilestone` - For goal milestone tracking
- `ActivityLog` - For comprehensive activity logging (optional, uses existing UserActivity)

## Testing

Run the test script:
```bash
cd backend
TOKEN=your_auth_token ./scripts/test_all_intelligence.sh
```

Or run pytest:
```bash
cd backend
pytest tests/test_intelligence_features.py -v
```

## Platform Support

All features are available across all platforms:
- **Web**: Access via REST API
- **Mobile (Flutter)**: Can be integrated via API calls
- **Desktop**: Same REST API
- **Raspberry Pi**: Backend runs natively on RPi

## Best Practices

1. **Correlation Analysis**: Use at least 10-20 data points for meaningful correlations
2. **Anomaly Detection**: Review anomalies in context - they may be legitimate outliers
3. **Forecasts**: Forecasts are more accurate for metrics with consistent patterns
4. **Recommendations**: Recommendations improve as more data is collected
5. **Activity Logging**: Activities are automatically logged for most operations

## Future Enhancements

- Machine learning models for more accurate predictions
- Advanced emotion detection using deep learning
- Real-time anomaly alerts
- Custom recommendation rules
- Activity pattern analysis

