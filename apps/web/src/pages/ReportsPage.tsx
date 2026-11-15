import { useState } from "react";
import { useTranslation } from "react-i18next";
import { request, toErrorMessage } from "../api";
import { useAuth } from "../auth";
import { ErrorState, LoadingState } from "../components/Status";
import { extractArray, formatCurrency, marginLabel } from "../utils";

type ReportState = {
  summary: Record<string, unknown> | null;
  byMonth: Array<Record<string, unknown>>;
  byGreenhouse: Array<Record<string, unknown>>;
  byCrop: Array<Record<string, unknown>>;
};

const initialState: ReportState = {
  summary: null,
  byMonth: [],
  byGreenhouse: [],
  byCrop: []
};

export function ReportsPage(): JSX.Element {
  const { t } = useTranslation();
  const { token } = useAuth();
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");
  const [reports, setReports] = useState<ReportState>(initialState);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onLoad(event: React.FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (!token) return;
    setLoading(true);
    setError("");
    try {
      const query = new URLSearchParams({ from, to }).toString();
      const [summary, byMonth, byGreenhouse, byCrop] = await Promise.all([
        request<Record<string, unknown>>(`/reports/summary?${query}`, {}, token),
        request<unknown>(`/reports/by-month?${query}`, {}, token),
        request<unknown>(`/reports/by-greenhouse?${query}`, {}, token),
        request<unknown>(`/reports/by-crop?${query}`, {}, token)
      ]);
      setReports({
        summary,
        byMonth: extractArray(byMonth),
        byGreenhouse: extractArray(byGreenhouse),
        byCrop: extractArray(byCrop)
      });
    } catch (caught) {
      setError(toErrorMessage(caught));
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="stack">
      <p className="page-intro">{t("reports.title")}</p>
      {error ? <ErrorState message={error} /> : null}

      <div className="card">
        <div className="card-header">
          <div className="card-title">{t("actions.refresh")}</div>
        </div>
        <div className="card-body">
          <form className="form-grid" onSubmit={onLoad}>
            <div className="form-group">
              <label htmlFor="rp-from">{t("reports.from")}</label>
              <input
                id="rp-from"
                type="date"
                value={from}
                onChange={(event) => setFrom(event.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="rp-to">{t("reports.to")}</label>
              <input id="rp-to" type="date" value={to} onChange={(event) => setTo(event.target.value)} required />
            </div>
            <div className="form-actions">
              <button className="btn btn-primary" type="submit" disabled={loading}>
                {t("actions.refresh")}
              </button>
            </div>
          </form>
        </div>
      </div>

      {loading ? <LoadingState /> : null}

      {reports.summary ? (
        <div className="stats-grid">
          <article className="stat-card green">
            <div className="stat-label">{t("dashboard.revenue")}</div>
            <div className="stat-value">{formatCurrency(Number(reports.summary.revenue ?? 0))}</div>
          </article>
          <article className="stat-card amber">
            <div className="stat-label">{t("dashboard.expenses")}</div>
            <div className="stat-value">{formatCurrency(Number(reports.summary.expenses ?? 0))}</div>
          </article>
          <article className="stat-card blue">
            <div className="stat-label">{t("dashboard.profit")}</div>
            <div className="stat-value">{formatCurrency(Number(reports.summary.profit ?? 0))}</div>
          </article>
          <article className="stat-card earth">
            <div className="stat-label">{t("dashboard.margin")}</div>
            <div className="stat-value">
              {reports.summary.margin === null
                ? t("reports.marginNA")
                : marginLabel(Number(reports.summary.margin ?? 0))}
            </div>
          </article>
        </div>
      ) : null}

      {reports.summary ? (
        <>
          <div className="card">
            <div className="card-header">
              <div className="card-title">{t("reports.byMonth")}</div>
            </div>
            <div className="card-body table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>{t("forms.month")}</th>
                    <th>{t("dashboard.revenue")}</th>
                    <th>{t("dashboard.expenses")}</th>
                    <th>{t("dashboard.profit")}</th>
                  </tr>
                </thead>
                <tbody>
                  {reports.byMonth.length > 0 ? (
                    reports.byMonth.map((row) => (
                      <tr key={String(row.month ?? row.id)}>
                        <td>{String(row.month ?? "-")}</td>
                        <td className="td-num">{formatCurrency(Number(row.revenue ?? 0))}</td>
                        <td className="td-num">{formatCurrency(Number(row.expenses ?? 0))}</td>
                        <td className="td-num">{formatCurrency(Number(row.profit ?? 0))}</td>
                      </tr>
                    ))
                  ) : (
                    <tr className="empty-row">
                      <td colSpan={4}>{t("status.empty")}</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <div className="card-title">{t("reports.byGreenhouse")}</div>
            </div>
            <div className="card-body table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>{t("forms.greenhouse")}</th>
                    <th>{t("dashboard.revenue")}</th>
                    <th>{t("dashboard.expenses")}</th>
                  </tr>
                </thead>
                <tbody>
                  {reports.byGreenhouse.length > 0 ? (
                    reports.byGreenhouse.map((row) => (
                      <tr key={String(row.greenhouse_id ?? row.id)}>
                        <td>{String(row.greenhouse_name ?? row.greenhouse_id ?? "-")}</td>
                        <td className="td-num">{formatCurrency(Number(row.revenue ?? 0))}</td>
                        <td className="td-num">{formatCurrency(Number(row.expenses ?? 0))}</td>
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

          <div className="card">
            <div className="card-header">
              <div className="card-title">{t("reports.byCrop")}</div>
            </div>
            <div className="card-body table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>{t("forms.crop")}</th>
                    <th>{t("dashboard.revenue")}</th>
                    <th>{t("dashboard.expenses")}</th>
                  </tr>
                </thead>
                <tbody>
                  {reports.byCrop.length > 0 ? (
                    reports.byCrop.map((row) => (
                      <tr key={String(row.crop ?? row.id)}>
                        <td>{row.crop ? t(`crops.${String(row.crop)}`) : "-"}</td>
                        <td className="td-num">{formatCurrency(Number(row.revenue ?? 0))}</td>
                        <td className="td-num">{formatCurrency(Number(row.expenses ?? 0))}</td>
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
        </>
      ) : null}
    </section>
  );
}
