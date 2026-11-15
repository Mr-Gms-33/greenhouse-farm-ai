import { useTranslation } from "react-i18next";

export function LanguageSwitcher(): JSX.Element {
  const { i18n, t } = useTranslation();

  return (
    <label className="locale-switcher">
      <span>{t("locale.switch")}</span>
      <select
        aria-label={t("locale.switch")}
        value={i18n.language}
        onChange={(event) => {
          void i18n.changeLanguage(event.target.value);
        }}
      >
        <option value="en">{t("locale.en")}</option>
        <option value="ar">{t("locale.ar")}</option>
      </select>
    </label>
  );
}
