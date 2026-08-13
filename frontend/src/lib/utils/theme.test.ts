import { beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';

const mockSystemTheme = (matches: boolean) => {
	Object.defineProperty(window, 'matchMedia', {
		configurable: true,
		value: vi.fn().mockImplementation((query: string) => ({
			matches,
			media: query,
			addEventListener: vi.fn(),
			removeEventListener: vi.fn()
		}))
	});
};

describe('theme preferences', () => {
	let theme: typeof import('./theme');

	beforeAll(async () => {
		mockSystemTheme(false);
		theme = await import('./theme');
	});

	beforeEach(() => {
		localStorage.clear();
		document.documentElement.classList.remove('dark');
		mockSystemTheme(false);
	});

	it('initializes the stored preference', () => {
		localStorage.setItem('ciso-theme', 'dark');

		expect(theme.initializeThemePreference()).toBe('dark');
		expect(document.documentElement.classList.contains('dark')).toBe(true);
	});

	it('falls back to the system preference', () => {
		mockSystemTheme(true);

		expect(theme.initializeThemePreference()).toBe('dark');
	});

	it('persists an explicit preference', async () => {
		await theme.setTheme('dark', false);

		expect(localStorage.getItem('ciso-theme')).toBe('dark');
		expect(document.documentElement.classList.contains('dark')).toBe(true);
	});
});
