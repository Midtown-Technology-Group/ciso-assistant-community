import { beforeEach, describe, expect, it, vi } from 'vitest';

import { applyThemePreference, resolveThemePreference, toggleThemePreference } from './theme';

const mockSystemTheme = (matches: boolean) => {
	Object.defineProperty(window, 'matchMedia', {
		writable: true,
		value: vi.fn().mockImplementation((query: string) => ({
			matches,
			media: query,
			onchange: null,
			addEventListener: vi.fn(),
			removeEventListener: vi.fn(),
			addListener: vi.fn(),
			removeListener: vi.fn(),
			dispatchEvent: vi.fn()
		}))
	});
};

describe('theme preferences', () => {
	beforeEach(() => {
		localStorage.clear();
		document.documentElement.classList.remove('dark');
		mockSystemTheme(false);
	});

	it('uses the stored preference before the system preference', () => {
		localStorage.setItem('ciso:theme', 'dark');
		mockSystemTheme(false);

		expect(resolveThemePreference()).toBe('dark');
	});

	it('falls back to the system preference when no stored preference exists', () => {
		mockSystemTheme(true);

		expect(resolveThemePreference()).toBe('dark');
	});

	it('applies the selected theme to the document root', () => {
		applyThemePreference('dark');

		expect(document.documentElement.classList.contains('dark')).toBe(true);

		applyThemePreference('light');

		expect(document.documentElement.classList.contains('dark')).toBe(false);
	});

	it('toggles and persists the next explicit preference', () => {
		const next = toggleThemePreference('light');

		expect(next).toBe('dark');
		expect(localStorage.getItem('ciso:theme')).toBe('dark');
		expect(document.documentElement.classList.contains('dark')).toBe(true);
	});
});
