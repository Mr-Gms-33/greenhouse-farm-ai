import { useState } from "react";
import { useTranslation } from "react-i18next";
import { request, toErrorMessage } from "../api";
import { useAuth } from "../auth";
import { ErrorState } from "../components/Status";
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
      <h1>{t("reports.title")}</h1>
      <form className="form-grid" onSubmit={onLoad}>
        <label>
          {t("reports.from")}
          <input type="date" value={from} onChange={(event) => setFrom(event.target.value)} required />
        </label>
        <label>
          {t("reports.to")}
          <input type="date" value={to} onChange={(event) => setTo(event.target.value)} required />
        </label>
        <button type="submit" disabled={loading}>
          {t("actions.refresh")}
        </button>
      </form>
      {error ? <ErrorState message={error} /> : null}
      {reports.summary ? (
        <div className="cards">
          <article className="card">
            <h2>{t("dashboard.revenue")}</h2>
            <p>{formatCurrency(Number(reports.summary.revenue ?? 0))}</p>
          </article>
          <article className="card">
            <h2>{t("dashboard.expenses")}</h2>
            <p>{formatCurrency(Number(reports.summary.expenses ?? 0))}</p>
          </article>
          <article className="card">
            <h2>{t("dashboard.profit")}</h2>
            <p>{formatCurrency(Number(reports.summary.profit ?? 0))}</p>
          </article>
          <article className="card">
            <h2>{t("dashboard.margin")}</h2>
            <p>
              {reports.summary.margin === null
                ? t("reports.marginNA")
                : marginLabel(Number(reports.summary.margin ?? 0))}
            </p>
          </article>
        </div>
      ) : null}
      <div className="table-wrap">
        <h2>{t("reports.byMonth")}</h2>
        <table>
          <tbody>
            {reports.byMonth.map((row) => (
              <tr key={String(row.month ?? row.id)}>
                <td>{String(row.month ?? "-")}</td>
                <td>{formatCurrency(Number(row.revenue ?? 0))}</td>
                <td>{formatCurrency(Number(row.expenses ?? 0))}</td>
                <td>{formatCurrency(Number(row.profit ?? 0))}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="table-wrap">
        <h2>{t("reports.byGreenhouse")}</h2>
        <table>
          <tbody>
            {reports.byGreenhouse.map((row) => (
              <tr key={String(row.greenhouse_id ?? row.id)}>
                <td>{String(row.greenhouse_name ?? row.greenhouse_id ?? "-")}</td>
                <td>{formatCurrency(Number(row.revenue ?? 0))}</td>
                <td>{formatCurrency(Number(row.expenses ?? 0))}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="table-wrap">
        <h2>{t("reports.byCrop")}</h2>
        <table>
          <tbody>
            {reports.byCrop.map((row) => (
              <tr key={String(row.crop ?? row.id)}>
                <td>{row.crop ? t(`crops.${String(row.crop)}`) : "-"}</td>
                <td>{formatCurrency(Number(row.revenue ?? 0))}</td>
                <td>{formatCurrency(Number(row.expenses ?? 0))}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
