import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../auth";
import { toErrorMessage } from "../api";
import { LanguageSwitcher } from "../components/LanguageSwitcher";

const demos = [
  { email: "owner@farm.ma", password: "Owner123!", className: "", labelKey: "auth.demoOwner" },
  { email: "manager@farm.ma", password: "Manager123!", className: "staff", labelKey: "auth.demoManager" },
  { email: "accountant@farm.ma", password: "Accountant123!", className: "finance", labelKey: "auth.demoAccountant" }
] as const;

export function LoginPage(): JSX.Element {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { login, isAuthenticated } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (isAuthenticated) return <Navigate to="/" replace />;

  async function doLogin(nextEmail: string, nextPassword: string): Promise<void> {
    setError("");
    setSubmitting(true);
    try {
      await login(nextEmail, nextPassword);
      navigate("/");
    } catch (caught) {
      setError(toErrorMessage(caught) || t("auth.error"));
    } finally {
      setSubmitting(false);
    }
  }

  async function onSubmit(event: React.FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    await doLogin(email, password);
  }

  return (
    <div className="login-page">
      <div className="login-shape ls1" />
      <div className="login-shape ls2" />
      <div className="login-box">
        <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 8 }}>
          <LanguageSwitcher />
        </div>
        <div className="login-brand">
          <div className="login-logo">ف</div>
          <div className="name">
            {t("brand.short")} <span>Pro</span>
          </div>
          <div className="sub">{t("brand.tagline")}</div>
        </div>
        <h1 className="login-title">{t("auth.title")}</h1>
        <p className="login-desc">{t("auth.subtitle")}</p>
        <form onSubmit={onSubmit}>
          <div className="lf">
            <label htmlFor="login-email">{t("auth.email")}</label>
            <input
              id="login-email"
              value={email}
              type="email"
              onChange={(event) => setEmail(event.target.value)}
              required
              autoComplete="email"
            />
          </div>
          <div className="lf">
            <label htmlFor="login-password">{t("auth.password")}</label>
            <input
              id="login-password"
              value={password}
              type="password"
              onChange={(event) => setPassword(event.target.value)}
              required
              autoComplete="current-password"
            />
          </div>
          {error ? <div className="login-err">{error}</div> : null}
          <button className="btn-login" type="submit" disabled={submitting}>
            {t("auth.submit")}
          </button>
        </form>
        <div className="login-demo">
          <div>
            <strong>{t("auth.demoTitle")}</strong>
          </div>
          <div className="demo-accounts">
            {demos.map((demo) => (
              <button
                key={demo.email}
                type="button"
                className={`btn-demo ${demo.className}`.trim()}
                disabled={submitting}
                onClick={() => {
                  setEmail(demo.email);
                  setPassword(demo.password);
                  void doLogin(demo.email, demo.password);
                }}
              >
                {t(demo.labelKey)}
              </button>
            ))}
          </div>
        </div>
        <div className="login-footer">{t("brand.footer")}</div>
      </div>
    </div>
  );
}
