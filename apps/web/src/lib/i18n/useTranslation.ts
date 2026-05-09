"use client";

import { useState, useEffect, useCallback } from "react";
import {
  translations,
  defaultLanguage,
  t as translate,
  languageNames,
  LANGUAGES,
} from "./translations";

// Language type derived from translations
export type Language = "en" | "sq" | "de" | "it" | "fr" | "es";

const STORAGE_KEY = "kloud_language";

export function useTranslation() {
  const [language, setLanguageState] = useState<Language>(defaultLanguage);
  const [isLoaded, setIsLoaded] = useState(false);

  // Load language from localStorage on mount
  useEffect(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem(STORAGE_KEY) as Language;
      if (stored && translations[stored]) {
        setLanguageState(stored);
      }
      setIsLoaded(true);
    }
  }, []);

  // Set language and persist
  const setLanguage = useCallback((lang: Language) => {
    if (translations[lang]) {
      setLanguageState(lang);
      if (typeof window !== "undefined") {
        localStorage.setItem(STORAGE_KEY, lang);
      }
    }
  }, []);

  // Translation function
  const t = useCallback(
    (key: string): string => {
      return translate(key, language);
    },
    [language],
  );

  return {
    language,
    setLanguage,
    t,
    isLoaded,
    languages: languageNames,
    availableLanguages: LANGUAGES,
  };
}

// Static translation function (for server-side or non-hook usage)
export { translate as t, languageNames, defaultLanguage };

