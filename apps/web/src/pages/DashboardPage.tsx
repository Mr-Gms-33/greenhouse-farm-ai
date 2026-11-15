import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { request, toErrorMessage } from "../api";
import { useAuth } from "../auth";
import { ErrorState, LoadingState } from "../components/Status";
import { formatCurrency, marginLabel } from "../utils";

export function DashboardPage(): JSX.Element {
  const { t } = useTranslation();
  const { token, user } = useAuth();
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load(): Promise<void> {
      if (!token) return;
      setLoading(true);
      setError("");
      try {
        const result = await request<Record<string, unknown>>("/dashboard", {}, token);
        setData(result);
      } catch (caught) {
        setError(toErrorMessage(caught));
      } finally {
        setLoading(false);
      }
    }
    void load();
  }, [token]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  const activeGreenhouses = Number(data?.active_greenhouses ?? 0);
  const activeCropCycles = Number(data?.active_crop_cycles ?? 0);
  const revenue = Number(data?.revenue ?? 0);
  const expenses = Number(data?.expenses ?? 0);
  const profit = Number(data?.profit ?? 0);
  const margin = data?.margin !== null && data?.margin !== undefined ? Number(data.margin) : null;

  return (
    <section className="stack">
      <h1>{t("dashboard.title")}</h1>
      <p className="muted">
        {user?.role === "owner"
          ? t("dashboard.ownerHint")
          : user?.role === "manager"
            ? t("dashboard.managerHint")
            : t("dashboard.accountantHint")}
      </p>
      <div className="cards">
        <article className="card">
          <h2>{t("dashboard.activeGreenhouses")}</h2>
          <p>{activeGreenhouses}</p>
        </article>
        <article className="card">
          <h2>{t("dashboard.activeCropCycles")}</h2>
          <p>{activeCropCycles}</p>
        </article>
        {user?.role !== "manager" ? (
          <>
            <article className="card">
              <h2>{t("dashboard.revenue")}</h2>
              <p>{formatCurrency(revenue)}</p>
            </article>
            <article className="card">
              <h2>{t("dashboard.expenses")}</h2>
              <p>{formatCurrency(expenses)}</p>
            </article>
            <article className="card">
              <h2>{t("dashboard.profit")}</h2>
              <p>{formatCurrency(profit)}</p>
            </article>
            <article className="card">
              <h2>{t("dashboard.margin")}</h2>
              <p>{margin === null ? t("reports.marginNA") : marginLabel(margin)}</p>
            </article>
          </>
        ) : null}
      </div>
    </section>
  );
}
