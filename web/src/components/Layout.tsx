/**
 * Main Layout Component
 */
import { useState } from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { ThemeToggle } from './ThemeToggle';

export function Layout() {
  const { isAuthenticated, user, logout } = useAuthStore();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
    setMobileMenuOpen(false);
  };

  const navLinks = [
    { to: '/dashboard', label: 'Dashboard' },
    { to: '/activity', label: 'Activity' },
    { to: '/face-recognition', label: 'Face Recognition' },
    { to: '/profile', label: 'Profile' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {isAuthenticated && (
        <nav className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex">
                <div className="flex-shrink-0 flex items-center">
                  <Link to="/dashboard" className="text-lg sm:text-xl font-bold text-primary-600">
                    LifeVault
                  </Link>
                </div>
                {/* Desktop Navigation */}
                <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                  {navLinks.map((link) => (
                    <Link
                      key={link.to}
                      to={link.to}
                      className="border-transparent text-gray-500 dark:text-gray-400 hover:border-gray-300 dark:hover:border-gray-600 hover:text-gray-700 dark:hover:text-gray-200 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                    >
                      {link.label}
                    </Link>
                  ))}
                </div>
              </div>
              <div className="flex items-center gap-2">
                {/* Theme Toggle */}
                <ThemeToggle />
                {/* Desktop User Info */}
                <span className="hidden sm:block text-sm text-gray-700 dark:text-gray-300 mr-2">
                  {user?.username}
                </span>
                <button
                  onClick={handleLogout}
                  className="hidden sm:block btn btn-secondary text-sm"
                >
                  Logout
                </button>
                {/* Mobile Menu Button */}
                <button
                  onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                  className="sm:hidden p-2 rounded-md text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
                  aria-label="Toggle menu"
                >
                  <svg
                    className="h-6 w-6"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    {mobileMenuOpen ? (
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    ) : (
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4 6h16M4 12h16M4 18h16"
                      />
                    )}
                  </svg>
                </button>
              </div>
            </div>
          </div>
          {/* Mobile Navigation Menu */}
          {mobileMenuOpen && (
            <div className="sm:hidden border-t border-gray-200 dark:border-gray-700">
              <div className="px-2 pt-2 pb-3 space-y-1">
                {navLinks.map((link) => (
                  <Link
                    key={link.to}
                    to={link.to}
                    onClick={() => setMobileMenuOpen(false)}
                    className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    {link.label}
                  </Link>
                ))}
                <div className="px-3 py-2 border-t border-gray-200 dark:border-gray-700 mt-2">
                  <div className="text-sm text-gray-700 dark:text-gray-300 mb-2">{user?.username}</div>
                  <button
                    onClick={handleLogout}
                    className="w-full btn btn-secondary text-sm"
                  >
                    Logout
                  </button>
                </div>
              </div>
            </div>
          )}
        </nav>
      )}
      <main className="w-full overflow-x-hidden">
        <Outlet />
      </main>
    </div>
  );
}
