/**
 * Input Validation Utilities
 * Client-side validation for forms and user inputs
 */

export interface ValidationResult {
    isValid: boolean;
    errors: Record<string, string>;
  }
  
  /**
   * Email validation
   */
  export function validateEmail(email: string): { isValid: boolean; error?: string } {
    if (!email) {
      return { isValid: false, error: 'Email is required' };
    }
  
    if (email.length > 254) {
      return { isValid: false, error: 'Email is too long' };
    }
  
    const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
    
    if (!emailRegex.test(email)) {
      return { isValid: false, error: 'Invalid email format' };
    }
  
    return { isValid: true };
  }
  
  /**
   * Password validation with strength checking
   */
  export function validatePassword(password: string): {
    isValid: boolean;
    error?: string;
    strength?: 'weak' | 'medium' | 'strong';
  } {
    if (!password) {
      return { isValid: false, error: 'Password is required' };
    }
  
    if (password.length < 8) {
      return { isValid: false, error: 'Password must be at least 8 characters long' };
    }
  
    if (password.length > 128) {
      return { isValid: false, error: 'Password is too long' };
    }
  
    let strength = 0;
    const checks = {
      lowercase: /[a-z]/.test(password),
      uppercase: /[A-Z]/.test(password),
      number: /[0-9]/.test(password),
      special: /[^A-Za-z0-9]/.test(password),
    };
  
    // Check requirements
    if (!checks.lowercase) {
      return { isValid: false, error: 'Password must contain at least one lowercase letter' };
    }
    if (!checks.uppercase) {
      return { isValid: false, error: 'Password must contain at least one uppercase letter' };
    }
    if (!checks.number) {
      return { isValid: false, error: 'Password must contain at least one number' };
    }
    if (!checks.special) {
      return { isValid: false, error: 'Password must contain at least one special character' };
    }
  
    // Calculate strength
    strength += checks.lowercase ? 1 : 0;
    strength += checks.uppercase ? 1 : 0;
    strength += checks.number ? 1 : 0;
    strength += checks.special ? 1 : 0;
    strength += password.length >= 12 ? 1 : 0;
    strength += password.length >= 16 ? 1 : 0;
  
    const strengthLevel = strength >= 5 ? 'strong' : strength >= 4 ? 'medium' : 'weak';
  
    return { isValid: true, strength: strengthLevel };
  }
  
  /**
   * Username validation
   */
  export function validateUsername(username: string): { isValid: boolean; error?: string } {
    if (!username) {
      return { isValid: false, error: 'Username is required' };
    }
  
    if (username.length < 3) {
      return { isValid: false, error: 'Username must be at least 3 characters long' };
    }
  
    if (username.length > 50) {
      return { isValid: false, error: 'Username must be less than 50 characters' };
    }
  
    // Allow letters, numbers, underscores, and hyphens
    const usernameRegex = /^[a-zA-Z0-9_-]+$/;
    if (!usernameRegex.test(username)) {
      return {
        isValid: false,
        error: 'Username can only contain letters, numbers, underscores, and hyphens',
      };
    }
  
    // Don't allow username to start or end with special characters
    if (/^[_-]|[_-]$/.test(username)) {
      return {
        isValid: false,
        error: 'Username cannot start or end with underscore or hyphen',
      };
    }
  
    return { isValid: true };
  }
  
  /**
   * Full name validation
   */
  export function validateFullName(fullName: string): { isValid: boolean; error?: string } {
    if (!fullName) {
      return { isValid: true }; // Optional field
    }
  
    if (fullName.length < 2) {
      return { isValid: false, error: 'Name must be at least 2 characters long' };
    }
  
    if (fullName.length > 100) {
      return { isValid: false, error: 'Name is too long' };
    }
  
    // Allow letters, spaces, hyphens, apostrophes
    const nameRegex = /^[a-zA-Z\s'-]+$/;
    if (!nameRegex.test(fullName)) {
      return { isValid: false, error: 'Name contains invalid characters' };
    }
  
    return { isValid: true };
  }
  
  /**
   * Number validation
   */
  export function validateNumber(
    value: string | number,
    options: {
      min?: number;
      max?: number;
      integer?: boolean;
      positive?: boolean;
    } = {}
  ): { isValid: boolean; error?: string } {
    const num = typeof value === 'string' ? parseFloat(value) : value;
  
    if (isNaN(num)) {
      return { isValid: false, error: 'Must be a valid number' };
    }
  
    if (options.integer && !Number.isInteger(num)) {
      return { isValid: false, error: 'Must be a whole number' };
    }
  
    if (options.positive && num <= 0) {
      return { isValid: false, error: 'Must be a positive number' };
    }
  
    if (options.min !== undefined && num < options.min) {
      return { isValid: false, error: `Must be at least ${options.min}` };
    }
  
    if (options.max !== undefined && num > options.max) {
      return { isValid: false, error: `Must be at most ${options.max}` };
    }
  
    return { isValid: true };
  }
  
  /**
   * Date validation
   */
  export function validateDate(
    date: string | Date,
    options: {
      min?: Date;
      max?: Date;
      future?: boolean;
      past?: boolean;
    } = {}
  ): { isValid: boolean; error?: string } {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
  
    if (isNaN(dateObj.getTime())) {
      return { isValid: false, error: 'Invalid date' };
    }
  
    const now = new Date();
  
    if (options.future && dateObj <= now) {
      return { isValid: false, error: 'Date must be in the future' };
    }
  
    if (options.past && dateObj >= now) {
      return { isValid: false, error: 'Date must be in the past' };
    }
  
    if (options.min && dateObj < options.min) {
      return { isValid: false, error: `Date must be after ${options.min.toLocaleDateString()}` };
    }
  
    if (options.max && dateObj > options.max) {
      return { isValid: false, error: `Date must be before ${options.max.toLocaleDateString()}` };
    }
  
    return { isValid: true };
  }
  
  /**
   * File validation
   */
  export function validateFile(
    file: File,
    options: {
      maxSize?: number; // in bytes
      allowedTypes?: string[]; // MIME types
      allowedExtensions?: string[];
    } = {}
  ): { isValid: boolean; error?: string } {
    if (!file) {
      return { isValid: false, error: 'No file selected' };
    }
  
    if (options.maxSize && file.size > options.maxSize) {
      const sizeMB = (options.maxSize / (1024 * 1024)).toFixed(2);
      return { isValid: false, error: `File size must be less than ${sizeMB}MB` };
    }
  
    if (options.allowedTypes && !options.allowedTypes.includes(file.type)) {
      return {
        isValid: false,
        error: `File type must be one of: ${options.allowedTypes.join(', ')}`,
      };
    }
  
    if (options.allowedExtensions) {
      const extension = file.name.split('.').pop()?.toLowerCase();
      if (!extension || !options.allowedExtensions.includes(extension)) {
        return {
          isValid: false,
          error: `File extension must be one of: ${options.allowedExtensions.join(', ')}`,
        };
      }
    }
  
    return { isValid: true };
  }
  
  /**
   * Image file validation
   */
  export function validateImageFile(file: File): { isValid: boolean; error?: string } {
    return validateFile(file, {
      maxSize: 10 * 1024 * 1024, // 10MB
      allowedTypes: ['image/jpeg', 'image/png', 'image/jpg', 'image/webp'],
      allowedExtensions: ['jpg', 'jpeg', 'png', 'webp'],
    });
  }
  
  /**
   * Form validation helper
   */
  export function validateForm<T extends Record<string, any>>(
    data: T,
    validators: {
      [K in keyof T]?: (value: T[K]) => { isValid: boolean; error?: string };
    }
  ): ValidationResult {
    const errors: Record<string, string> = {};
  
    for (const [field, validator] of Object.entries(validators)) {
      if (validator) {
        const result = validator(data[field as keyof T]);
        if (!result.isValid && result.error) {
          errors[field] = result.error;
        }
      }
    }
  
    return {
      isValid: Object.keys(errors).length === 0,
      errors,
    };
  }
  
  /**
   * Sanitize input to prevent XSS
   */
  export function sanitizeInput(input: string): string {
    // Basic HTML entity encoding
    return input
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;')
      .replace(/\//g, '&#x2F;');
  }
  
  /**
   * Sanitize HTML to allow only safe tags
   */
  export function sanitizeHtml(html: string): string {
    const allowedTags = ['b', 'i', 'em', 'strong', 'a', 'p', 'br'];
    const div = document.createElement('div');
    div.innerHTML = html;
  
    // Remove script tags and event handlers
    const scripts = div.querySelectorAll('script');
    scripts.forEach((script) => script.remove());
  
    // Remove event handlers
    const allElements = div.querySelectorAll('*');
    allElements.forEach((element) => {
      Array.from(element.attributes).forEach((attr) => {
        if (attr.name.startsWith('on')) {
          element.removeAttribute(attr.name);
        }
      });
    });
  
    // Remove disallowed tags
    allElements.forEach((element) => {
      if (!allowedTags.includes(element.tagName.toLowerCase())) {
        element.replaceWith(...Array.from(element.childNodes));
      }
    });
  
    return div.innerHTML;
  }
  
  /**
   * Validate URL
   */
  export function validateUrl(url: string): { isValid: boolean; error?: string } {
    if (!url) {
      return { isValid: false, error: 'URL is required' };
    }
  
    try {
      const urlObj = new URL(url);
      
      // Only allow http and https protocols
      if (!['http:', 'https:'].includes(urlObj.protocol)) {
        return { isValid: false, error: 'Only HTTP and HTTPS URLs are allowed' };
      }
  
      return { isValid: true };
    } catch {
      return { isValid: false, error: 'Invalid URL format' };
    }
  }
  
  /**
   * Debounced validation
   */
  export function createDebouncedValidator<T>(
    validator: (value: T) => { isValid: boolean; error?: string },
    delay: number = 300
  ): (value: T, callback: (result: { isValid: boolean; error?: string }) => void) => void {
    let timeoutId: NodeJS.Timeout;
  
    return (value: T, callback: (result: { isValid: boolean; error?: string }) => void) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        const result = validator(value);
        callback(result);
      }, delay);
    };
  }