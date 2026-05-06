(function () {
  function getScope() {
    return document.documentElement.dataset.themeScope || 'global';
  }

  function getStorageKey() {
    return 'awqaf-theme:' + getScope();
  }

  function getTheme() {
    try {
      const stored = localStorage.getItem(getStorageKey());
      return stored === 'dark' ? 'dark' : 'light';
    } catch (error) {
      return 'light';
    }
  }

  function setTheme(theme) {
    document.documentElement.dataset.theme = theme;
    try {
      localStorage.setItem(getStorageKey(), theme);
    } catch (error) {
      // Ignore storage errors; the current page still updates.
    }

    document.querySelectorAll('[data-theme-toggle]').forEach(function (button) {
      const isDark = theme === 'dark';
      button.setAttribute('aria-pressed', String(isDark));
      button.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');

      const icon = button.querySelector('[data-theme-icon]');
      if (icon) icon.textContent = isDark ? '\u2600' : '\u263e';
    });
  }

  setTheme(getTheme());

  document.addEventListener('click', function (event) {
    const button = event.target.closest('[data-theme-toggle]');
    if (!button) return;

    const nextTheme = getTheme() === 'dark' ? 'light' : 'dark';
    setTheme(nextTheme);
  });
})();
