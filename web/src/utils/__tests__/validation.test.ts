import { describe, it, expect } from 'vitest';
import { validateEmail, validatePassword, validateUsername } from '../validation';

describe('validateEmail', () => {
  it('accepts valid email addresses', () => {
    expect(validateEmail('test@example.com').isValid).toBe(true);
    expect(validateEmail('user.name+tag@example.co.uk').isValid).toBe(true);
  });

  it('rejects invalid email addresses', () => {
    expect(validateEmail('').isValid).toBe(false);
    expect(validateEmail('invalid').isValid).toBe(false);
    expect(validateEmail('@example.com').isValid).toBe(false);
    expect(validateEmail('test@').isValid).toBe(false);
  });
});

describe('validatePassword', () => {
  it('accepts strong passwords', () => {
    const result = validatePassword('StrongP@ss123');
    expect(result.isValid).toBe(true);
    expect(result.strength).toBe('strong');
  });

  it('rejects weak passwords', () => {
    expect(validatePassword('weak').isValid).toBe(false);
    expect(validatePassword('12345678').isValid).toBe(false);
    expect(validatePassword('NoNumbers!').isValid).toBe(false);
  });
});

describe('validateUsername', () => {
  it('accepts valid usernames', () => {
    expect(validateUsername('user123').isValid).toBe(true);
    expect(validateUsername('test_user').isValid).toBe(true);
  });

  it('rejects invalid usernames', () => {
    expect(validateUsername('ab').isValid).toBe(false); // Too short
    expect(validateUsername('a'.repeat(51)).isValid).toBe(false); // Too long
    expect(validateUsername('user@name').isValid).toBe(false); // Invalid char
  });
});