import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { request, toErrorMessage } from "../api";
import { useAuth } from "../auth";
import { EmptyState, ErrorState, LoadingState } from "../components/Status";
import { extractArray, formatCurrency } from "../utils";

type AnalysisRecord = Record<string, unknown>;

function estimateRows(analysis: AnalysisRecord | null): Array<Record<string, unknown>> {
  if (!analysis) return [];
  const forecast = analysis.forecast as Record<string, unknown> | undefined;
  if (!forecast) return [];
  const monthly = forecast.monthly as unknown;
  return extractArray(monthly);
}

export function AnalysisPage(): JSX.Element {
  const { t, i18n } = useTranslation();
  const { token } = useAuth();
  const [endMonth, setEndMonth] = useState("");
  const [records, setRecords] = useState<AnalysisRecord[]>([]);
  const [selectedId, setSelectedId] = useState<string>("");
  const [detail, setDetail] = useState<AnalysisRecord | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  async function loadList(): Promise<void> {
    if (!token) return;
    setLoading(true);
    setError("");
    try {
      const listResult = await request<unknown>("/analyses", {}, token);
      const rows = extractArray(listResult);
      setRecords(rows);
      const firstId = String(rows[0]?.id ?? "");
      if (!selectedId && firstId) {
        setSelectedId(firstId);
      }
    } catch (caught) {
      setError(toErrorMessage(caught));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadList();
  }, [token]);

  useEffect(() => {
    async function loadDetail(): Promise<void> {
      if (!token || !selectedId) return;
      try {
        const item = await request<AnalysisRecord>(`/analyses/${selectedId}`, {}, token);
        setDetail(item);
      } catch (caught) {
        setError(toErrorMessage(caught));
      }
    }
    void loadDetail();
  }, [token, selectedId]);

  async function onGenerate(event: React.FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (!token) return;
    setSubmitting(true);
    setError("");
    try {
      const created = await request<AnalysisRecord>(
        "/analyses",
        {
          method: "POST",
          body: JSON.stringify({ end_month: endMonth })
        },
        token
      );
      await loadList();
      if (created.id) {
        setSelectedId(String(created.id));
      }
    } catch (caught) {
      setError(toErrorMessage(caught));
    } finally {
      setSubmitting(false);
    }
  }

  const estimates = useMemo(() => estimateRows(detail), [detail]);
  const facts = (detail?.facts as Record<string, unknown> | undefined) ?? {};
  const narrative = detail?.[`narrative_${i18n.language}`] ?? detail?.narrative ?? "";

  return (
    <section className="stack">
      <h1>{t("analysis.title")}</h1>
      <form className="form-grid" onSubmit={onGenerate}>
        <label>
          {t("forms.endMonth")}
          <input type="month" value={endMonth} onChange={(event) => setEndMonth(event.target.value)} required />
        </label>
        <button type="submit" disabled={submitting}>
          {t("actions.generate")}
        </button>
      </form>
      {error ? <ErrorState message={error} /> : null}
      {loading ? <LoadingState /> : null}
      {!loading && records.length === 0 ? <EmptyState /> : null}
      {records.length > 0 ? (
        <label>
          {t("analysis.view")}
          <select value={selectedId} onChange={(event) => setSelectedId(event.target.value)}>
            {records.map((item) => (
              <option key={String(item.id)} value={String(item.id)}>
                {String(item.cutoff_month ?? item.id)}
              </option>
            ))}
          </select>
        </label>
      ) : null}
      {detail ? (
        <>
          <div className="cards">
            <article className="card">
              <h2>{t("analysis.state")}</h2>
              <p>{String(detail.state ?? "-")}</p>
            </article>
            <article className="card">
              <h2>{t("analysis.modelVersion")}</h2>
              <p>{String(detail.model_version ?? "-")}</p>
            </article>
            <article className="card">
              <h2>{t("analysis.generatedAt")}</h2>
              <p>{String(detail.generated_at ?? "-")}</p>
            </article>
            <article className="card">
              <h2>{t("analysis.horizon")}</h2>
              <p>{String((detail.forecast as Record<string, unknown> | undefined)?.horizon_months ?? "-")}</p>
            </article>
          </div>

          <div className="card">
            <h2>{t("analysis.facts")}</h2>
            <p>
              {t("dashboard.revenue")}: {formatCurrency(Number(facts.revenue ?? 0))}
            </p>
            <p>
              {t("dashboard.expenses")}: {formatCurrency(Number(facts.expenses ?? 0))}
            </p>
            <p>
              {t("dashboard.profit")}: {formatCurrency(Number(facts.profit ?? 0))}
            </p>
            <p>
              {t("analysis.coverage")}: {String((detail.coverage as Record<string, unknown> | undefined)?.month_count ?? "-")}
            </p>
          </div>

          <div className="card">
            <h2>{t("analysis.estimates")}</h2>
            {String(detail.state) === "insufficient_data" ? <p>{t("analysis.insufficientDataBody")}</p> : null}
            <p className="estimate-label">{t("analysis.estimateLabel")}</p>
            {estimates.length ? (
              <div className="table-wrap">
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
                    {estimates.map((row) => (
                      <tr key={String(row.month)}>
                        <td>{String(row.month ?? "-")}</td>
                        <td>{formatCurrency(Number(row.revenue ?? 0))}</td>
                        <td>{formatCurrency(Number(row.expenses ?? 0))}</td>
                        <td>{formatCurrency(Number(row.profit ?? 0))}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : null}
          </div>

          <div className="card">
            <h2>{t("analysis.narrative")}</h2>
            <p>{String(narrative || "-")}</p>
          </div>
        </>
      ) : null}
    </section>
  );
}
