import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { request, toErrorMessage } from "../api";
import { useAuth } from "../auth";
import { ErrorState, LoadingState } from "../components/Status";
import { formatCurrency, marginLabel } from "../utils";

type Finance = {
  revenue?: string | number;
  expenses?: string | number;
  profit?: string | number;
  margin_percent?: string | number | null;
};

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

  const greenhouses = Array.isArray(data?.greenhouses) ? data.greenhouses : [];
  const cycles = Array.isArray(data?.crop_cycles) ? data.crop_cycles : [];
  const activeGreenhouses = greenhouses.filter((g) => (g as { status?: string }).status === "active").length;
  const activeCropCycles = cycles.filter((c) => (c as { status?: string }).status === "active").length;
  const harvestTotal = String(data?.harvest_total_kg ?? "0");
  const finance = (data?.finance as Finance | undefined) ?? {};
  const showFinance = user?.role !== "manager";

  return (
    <section className="stack">
      <p className="page-intro">
        {user?.role === "owner"
          ? t("dashboard.ownerHint")
          : user?.role === "manager"
            ? t("dashboard.managerHint")
            : t("dashboard.accountantHint")}
      </p>

      <div className="stats-grid">
        <article className="stat-card green">
          <div className="stat-label">{t("dashboard.activeGreenhouses")}</div>
          <div className="stat-value">{activeGreenhouses}</div>
        </article>
        <article className="stat-card blue">
          <div className="stat-label">{t("dashboard.activeCropCycles")}</div>
          <div className="stat-value">{activeCropCycles}</div>
        </article>
        <article className="stat-card earth">
          <div className="stat-label">{t("dashboard.harvestTotal")}</div>
          <div className="stat-value">
            {harvestTotal} <span className="unit">kg</span>
          </div>
        </article>
        {showFinance ? (
          <>
            <article className="stat-card green">
              <div className="stat-label">{t("dashboard.revenue")}</div>
              <div className="stat-value">{formatCurrency(Number(finance.revenue ?? 0))}</div>
            </article>
            <article className="stat-card amber">
              <div className="stat-label">{t("dashboard.expenses")}</div>
              <div className="stat-value">{formatCurrency(Number(finance.expenses ?? 0))}</div>
            </article>
            <article className="stat-card blue">
              <div className="stat-label">{t("dashboard.profit")}</div>
              <div className="stat-value">{formatCurrency(Number(finance.profit ?? 0))}</div>
              <div className="stat-sub">
                {t("dashboard.margin")}:{" "}
                {finance.margin_percent === null || finance.margin_percent === undefined
                  ? t("reports.marginNA")
                  : marginLabel(Number(finance.margin_percent))}
              </div>
            </article>
          </>
        ) : null}
      </div>

      <div className="card">
        <div className="card-header">
          <div className="card-title">{t("dashboard.recentActivity")}</div>
        </div>
        <div className="card-body table-wrap">
          <table>
            <thead>
              <tr>
                <th>{t("forms.date")}</th>
                <th>{t("dashboard.activity")}</th>
                <th>{t("forms.quantity")}</th>
              </tr>
            </thead>
            <tbody>
              {Array.isArray(data?.recent_harvests) && data.recent_harvests.length > 0 ? (
                (data.recent_harvests as Array<Record<string, unknown>>).map((h) => (
                  <tr key={String(h.id)}>
                    <td>{String(h.harvest_date ?? "")}</td>
                    <td>{t("nav.harvests")}</td>
                    <td className="td-num">{String(h.quantity_kg ?? "")} kg</td>
                  </tr>
                ))
              ) : (
                <tr className="empty-row">
                  <td colSpan={3}>{t("status.empty")}</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
