# LifeVault Comprehensive Guide

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Setup Instructions](#setup-instructions)
5. [API Documentation](#api-documentation)
6. [Testing](#testing)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)

## Overview

LifeVault is a privacy-first personal analytics platform with advanced AI-powered features including face recognition, emotion detection, predictive analytics, and intelligent recommendations. It runs on multiple platforms including web, mobile (Flutter), desktop, and Raspberry Pi.

## Architecture

### Backend (Python/FastAPI)
- **Framework**: FastAPI
- **Database**: PostgreSQL (user data), MongoDB (analytics), Redis (caching)
- **Face Recognition**: dlib + face_recognition
- **Analytics**: scipy, numpy for statistical analysis
- **Location**: `backend/`

### Mobile (Flutter)
- **Framework**: Flutter
- **State Management**: Riverpod
- **Navigation**: GoRouter
- **Storage**: Hive (offline), flutter_secure_storage (secure)
- **Location**: `mobile/`

### Web (React/TypeScript)
- **Framework**: React + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Location**: `web/`

## Features

### Core Features
1. **Authentication** - JWT-based auth with refresh tokens
2. **Face Recognition** - Biometric authentication and recognition
3. **Analytics** - Personal data tracking and insights
4. **Offline Support** - Local storage with sync
5. **Push Notifications** - Firebase Cloud Messaging

### Intelligence Features (NEW)
1. **Emotion Detection** - Detects emotions from facial expressions
2. **Correlation Detection** - Finds relationships between metrics
3. **Anomaly Detection** - Identifies unusual patterns
4. **Pattern Recognition** - Detects trends and seasonality
5. **Predictive Analytics** - Forecasts future values
6. **Smart Recommendations** - Personalized suggestions
7. **Goal Milestones** - Break goals into trackable milestones
8. **Activity Logging** - Comprehensive activity tracking

## Setup Instructions

### Backend Setup

1. **Prerequisites**
   ```bash
   # Python 3.13.5
   # PostgreSQL
   # MongoDB
   # Redis
   ```

2. **Install Dependencies**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Initialize Database**
   ```bash
   # PostgreSQL
   sudo -u postgres psql
   CREATE DATABASE lifevault_db;
   CREATE USER lifevault WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE lifevault_db TO lifevault;
   \q
   
   # MongoDB and Redis should be running
   ```

5. **Run Migrations** (if using Alembic)
   ```bash
   alembic upgrade head
   ```

6. **Start Server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Mobile Setup (Flutter)

1. **Install Flutter**
   ```bash
   # Follow Flutter installation guide for your OS
   flutter doctor
   ```

2. **Install Dependencies**
   ```bash
   cd mobile
   flutter pub get
   ```

3. **Configure Firebase** (for push notifications)
   - Add `google-services.json` to `android/app/`
   - Add `GoogleService-Info.plist` to `ios/Runner/`

4. **Run App**
   ```bash
   flutter run
   ```

### Web Setup

1. **Install Node.js** (v18+)

2. **Install Dependencies**
   ```bash
   cd web
   npm install
   ```

3. **Configure API URL**
   ```bash
   # Edit src/services/api.ts or environment variables
   ```

4. **Run Development Server**
   ```bash
   npm run dev
   ```

## API Documentation

### Base URL
- Development: `http://localhost:8000/api/v1`
- Production: `https://your-domain.com/api/v1`

### Authentication
All endpoints (except auth endpoints) require a Bearer token:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Key Endpoints

#### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login
- `POST /auth/refresh` - Refresh token
- `POST /auth/logout` - Logout

#### Face Recognition
- `POST /face/enroll` - Enroll face
- `POST /face/recognize` - Recognize face (with emotion detection)
- `GET /face/my-faces` - List enrolled faces
- `DELETE /face/{face_id}` - Delete face

#### Analytics
- `POST /analytics/entries` - Create entry
- `GET /analytics/entries` - List entries
- `GET /analytics/stats` - Get statistics
- `GET /analytics/goals` - List goals
- `POST /analytics/goals` - Create goal

#### Intelligence (NEW)
- `GET /intelligence/correlations` - Get correlations
- `GET /intelligence/anomalies/{metric}` - Detect anomalies
- `GET /intelligence/patterns/{metric}` - Detect patterns
- `GET /intelligence/forecast/{metric}` - Get forecast
- `GET /intelligence/recommendations` - Get recommendations
- `GET /intelligence/activities` - Get activity logs

#### Goal Milestones (NEW)
- `POST /goals/{goal_id}/milestones` - Create milestone
- `GET /goals/{goal_id}/milestones` - List milestones
- `PATCH /milestones/{milestone_id}/progress` - Update progress

Full API documentation available at `/docs` when server is running.

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
pytest tests/test_intelligence_features.py -v
```

### Integration Tests
```bash
cd backend
TOKEN=your_token ./scripts/test_all_intelligence.sh
```

### Mobile Tests
```bash
cd mobile
flutter test
```

### Web Tests
```bash
cd web
npm test
```

## Deployment

### Backend (Raspberry Pi)
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-pip postgresql mongodb redis

# Setup systemd service
sudo nano /etc/systemd/system/lifevault.service
```

Service file:
```ini
[Unit]
Description=LifeVault API
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/LifeVault/backend
Environment="PATH=/home/pi/LifeVault/backend/venv/bin"
ExecStart=/home/pi/LifeVault/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable lifevault
sudo systemctl start lifevault
```

### Mobile (Android/iOS)
```bash
cd mobile
flutter build apk  # Android
flutter build ios  # iOS
```

### Web (Production)
```bash
cd web
npm run build
# Deploy dist/ folder to your hosting service
```

## Troubleshooting

### Common Issues

1. **Face Recognition Not Working**
   - Ensure dlib is properly installed
   - Check camera permissions
   - Verify image format (JPG/PNG)

2. **Database Connection Errors**
   - Verify database credentials in .env
   - Check if databases are running
   - Verify network connectivity

3. **Mobile Build Errors**
   - Run `flutter clean`
   - Delete `pubspec.lock` and run `flutter pub get`
   - Check Firebase configuration files

4. **Intelligence Features Not Working**
   - Ensure scipy is installed: `pip install scipy`
   - Check that you have sufficient data points (10+)
   - Verify API endpoints are accessible

### Debug Mode

Enable debug logging:
```bash
# Backend
export DEBUG=True
uvicorn app.main:app --reload --log-level debug

# Mobile
flutter run --debug

# Web
npm run dev
```

## Platform-Specific Notes

### Raspberry Pi
- Use `opencv-python-headless` (already in requirements)
- Face recognition may be slower - consider using HOG model instead of CNN
- Ensure sufficient RAM (2GB+ recommended)

### Mobile
- Biometric authentication requires physical device
- Camera features require camera permission
- Background sync requires WorkManager setup

### Web
- Face recognition via file upload
- Real-time features via WebSocket (if implemented)
- Responsive design for mobile browsers

## Security Considerations

1. **Tokens**: Stored securely using flutter_secure_storage
2. **Passwords**: Hashed using bcrypt
3. **Face Data**: Encrypted in MongoDB
4. **API**: Rate limiting enabled
5. **HTTPS**: Use in production

## Performance Optimization

1. **Database Indexing**: Ensure indexes on frequently queried fields
2. **Caching**: Redis used for session and frequently accessed data
3. **Pagination**: Use limit/offset for large datasets
4. **Background Tasks**: Use WorkManager for mobile sync

## Contributing

1. Follow code style guidelines
2. Write tests for new features
3. Update documentation
4. Use conventional commits

## License

MIT License

## Support

For issues and questions:
- GitHub Issues: [Your Repo URL]
- Documentation: `/docs` folder
- API Docs: `http://localhost:8000/docs`

