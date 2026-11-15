import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import en from "./i18n/en.json";
import ar from "./i18n/ar.json";

const LOCALE_KEY = "gh_locale";
const initialLocale = localStorage.getItem(LOCALE_KEY) ?? "en";

void i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    ar: { translation: ar }
  },
  lng: initialLocale,
  fallbackLng: "en",
  interpolation: { escapeValue: false }
});

function applyDirection(language: string): void {
  const dir = language === "ar" ? "rtl" : "ltr";
  document.documentElement.lang = language;
  document.documentElement.dir = dir;
}

applyDirection(i18n.language);

i18n.on("languageChanged", (language) => {
  localStorage.setItem(LOCALE_KEY, language);
  applyDirection(language);
});

export default i18n;
