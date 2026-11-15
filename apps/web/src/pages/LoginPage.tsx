import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../auth";
import { toErrorMessage } from "../api";

export function LoginPage(): JSX.Element {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { login, isAuthenticated } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (isAuthenticated) return <Navigate to="/" replace />;

  async function onSubmit(event: React.FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(email, password);
      navigate("/");
    } catch (caught) {
      setError(toErrorMessage(caught) || t("auth.error"));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="login-card">
      <h1>{t("auth.title")}</h1>
      <form onSubmit={onSubmit} className="form-grid">
        <label>
          {t("auth.email")}
          <input
            value={email}
            type="email"
            onChange={(event) => setEmail(event.target.value)}
            required
            autoComplete="email"
          />
        </label>
        <label>
          {t("auth.password")}
          <input
            value={password}
            type="password"
            onChange={(event) => setPassword(event.target.value)}
            required
            autoComplete="current-password"
          />
        </label>
        {error ? <p className="status error">{error}</p> : null}
        <button type="submit" disabled={submitting}>
          {t("auth.submit")}
        </button>
      </form>
    </div>
  );
}
