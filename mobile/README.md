# LifeVault Mobile App

Flutter mobile application for LifeVault - Personal analytics and face recognition platform.

## Features

- ✅ Authentication (Login, Register, Token Refresh)
- ✅ State Management with Riverpod
- ✅ Navigation with GoRouter
- ✅ Theme Configuration (Light/Dark mode)
- ✅ API Service Layer
- ✅ Secure Token Storage

## Project Structure

```
lib/
├── core/                    # Core functionality
│   ├── config/             # App configuration
│   ├── constants/          # App constants
│   ├── navigation/         # Navigation setup
│   ├── network/            # API client & exceptions
│   ├── providers/          # Global providers
│   ├── theme/              # Theme configuration
│   └── utils/              # Utility services
├── features/                # Feature modules
│   ├── auth/               # Authentication
│   ├── dashboard/          # Dashboard
│   ├── analytics/          # Analytics
│   ├── face/               # Face recognition
│   ├── home/               # Home screen
│   └── profile/            # User profile
└── main.dart               # App entry point
```

## Setup

1. **Install Flutter dependencies:**
   ```bash
   flutter pub get
   ```

2. **Configure API base URL:**
   Edit `lib/core/config/app_config.dart` and update the `baseUrl` to match your backend server.

3. **Run the app:**
   ```bash
   flutter run
   ```

## Dependencies

- **State Management:** `flutter_riverpod` - Modern state management
- **Navigation:** `go_router` - Declarative routing
- **HTTP Client:** `dio` - Powerful HTTP client
- **Storage:** 
  - `flutter_secure_storage` - Secure token storage
  - `shared_preferences` - General preferences
- **UI:** Material Design 3 with custom theming

## API Integration

The app integrates with the LifeVault backend API:
- Base URL: `http://192.168.0.109:8000/api/v1`
- Authentication: Bearer token (JWT)
- Auto token refresh on 401 errors

## Development

### Code Generation

If using code generation (freezed, json_serializable):
```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

### Linting

```bash
flutter analyze
```

## Next Steps

- [ ] Implement Analytics features
- [ ] Implement Face Recognition features
- [ ] Add offline support
- [ ] Add push notifications
- [ ] Add biometric authentication
- [ ] Add data export functionality

