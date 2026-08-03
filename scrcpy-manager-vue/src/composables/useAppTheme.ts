import { useTheme } from "vuetify";

const STORAGE_KEY = "scrcpy-manager-theme";

type ThemeName = "light" | "dark";

function getInitialTheme(): ThemeName {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored === "light" || stored === "dark") return stored;

  return window.matchMedia?.("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}

export function useAppTheme() {
  const theme = useTheme();

  theme.global.name.value = getInitialTheme();

  function setTheme(name: ThemeName) {
    theme.global.name.value = name;
    localStorage.setItem(STORAGE_KEY, name);
  }

  function toggleTheme() {
    setTheme(theme.global.current.value.dark ? "light" : "dark");
  }

  return { theme, setTheme, toggleTheme };
}
