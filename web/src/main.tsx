import React from 'react'
import ReactDOM from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import { router } from './router'
import { useThemeStore } from './store/themeStore'
import { useNotificationStore } from './store/notificationStore'
import './index.css'

// Initialize theme on app start
useThemeStore.getState().initializeTheme();

// Initialize notification permission check
if (typeof window !== 'undefined') {
  useNotificationStore.getState().checkPermission();
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
)

