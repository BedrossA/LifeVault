/**
 * Theme Store (Zustand) for dark mode management
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type ThemeMode = 'light' | 'dark' | 'system';

interface ThemeState {
  theme: ThemeMode;
  resolvedTheme: 'light' | 'dark'; // The actual theme being used
  setTheme: (theme: ThemeMode) => void;
  initializeTheme: () => void;
}

// Get system theme preference
const getSystemTheme = (): 'light' | 'dark' => {
  if (typeof window === 'undefined') return 'light';
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
};

// Apply theme to document
const applyTheme = (theme: 'light' | 'dark') => {
  if (typeof document === 'undefined') return;
  
  const root = document.documentElement;
  if (theme === 'dark') {
    root.classList.add('dark');
  } else {
    root.classList.remove('dark');
  }
};

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      theme: 'system',
      resolvedTheme: 'light',

      setTheme: (theme: ThemeMode) => {
        let resolvedTheme: 'light' | 'dark';
        
        if (theme === 'system') {
          resolvedTheme = getSystemTheme();
        } else {
          resolvedTheme = theme;
        }

        applyTheme(resolvedTheme);
        set({ theme, resolvedTheme });
      },

      initializeTheme: () => {
        const { theme } = get();
        let resolvedTheme: 'light' | 'dark';
        
        if (theme === 'system') {
          resolvedTheme = getSystemTheme();
        } else {
          resolvedTheme = theme;
        }

        applyTheme(resolvedTheme);
        set({ resolvedTheme });

        // Listen for system theme changes
        if (theme === 'system' && typeof window !== 'undefined') {
          const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
          const handleChange = (e: MediaQueryListEvent) => {
            const newResolvedTheme = e.matches ? 'dark' : 'light';
            applyTheme(newResolvedTheme);
            set({ resolvedTheme: newResolvedTheme });
          };
          
          // Modern browsers
          if (mediaQuery.addEventListener) {
            mediaQuery.addEventListener('change', handleChange);
          } else {
            // Fallback for older browsers
            mediaQuery.addListener(handleChange);
          }
        }
      },
    }),
    {
      name: 'theme-storage',
      partialize: (state) => ({
        theme: state.theme,
      }),
    }
  )
);

