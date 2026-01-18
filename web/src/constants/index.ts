export const NOTIFICATION_DEFAULTS = {
    DURATION: 5000,
    MAX_VISIBLE: 5,
  } as const;
  
  export const API_LIMITS = {
    DEFAULT_PAGE_SIZE: 10,
    MAX_PAGE_SIZE: 100,
  } as const;
  
  export const FILE_CONSTRAINTS = {
    MAX_IMAGE_SIZE: 10 * 1024 * 1024, // 10MB
    ALLOWED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/jpg', 'image/webp'],
  } as const;
  
  export const VALIDATION_RULES = {
    MIN_USERNAME_LENGTH: 3,
    MAX_USERNAME_LENGTH: 50,
    MIN_PASSWORD_LENGTH: 8,
    MAX_PASSWORD_LENGTH: 128,
  } as const;
  
  export const ROUTES = {
    HOME: '/',
    LOGIN: '/login',
    REGISTER: '/register',
    DASHBOARD: '/dashboard',
    PROFILE: '/profile',
    ACTIVITY: '/activity',
    FACE_RECOGNITION: '/face-recognition',
  } as const;