export type ThemePreference = 'light' | 'dark';

export const THEME_STORAGE_KEY = 'ciso:theme';

export function systemPrefersDark(): boolean {
	return window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false;
}

export function resolveThemePreference(): ThemePreference {
	let storedPreference: string | null = null;
	try {
		storedPreference = localStorage.getItem(THEME_STORAGE_KEY);
	} catch {
		storedPreference = null;
	}
	if (storedPreference === 'light' || storedPreference === 'dark') {
		return storedPreference;
	}
	return systemPrefersDark() ? 'dark' : 'light';
}

export function applyThemePreference(preference: ThemePreference): ThemePreference {
	document.documentElement.classList.toggle('dark', preference === 'dark');
	return preference;
}

export function persistThemePreference(preference: ThemePreference): ThemePreference {
	try {
		localStorage.setItem(THEME_STORAGE_KEY, preference);
	} catch {
		// Continue applying the in-memory theme when browser storage is unavailable.
	}
	return preference;
}

export function initializeThemePreference(): ThemePreference {
	return applyThemePreference(resolveThemePreference());
}

export function toggleThemePreference(currentPreference: ThemePreference): ThemePreference {
	const nextPreference = currentPreference === 'dark' ? 'light' : 'dark';
	persistThemePreference(nextPreference);
	return applyThemePreference(nextPreference);
}
