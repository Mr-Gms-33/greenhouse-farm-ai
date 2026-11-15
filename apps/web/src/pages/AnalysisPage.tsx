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

function analysisStateClass(state: unknown): string {
  const value = String(state ?? "");
  if (value === "ready") return "badge badge-green";
  if (value === "insufficient_data") return "badge badge-amber";
  return "badge badge-gray";
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
      <p className="page-intro">{t("analysis.title")}</p>
      {error ? <ErrorState message={error} /> : null}

      <div className="card">
        <div className="card-header">
          <div className="card-title">{t("actions.generate")}</div>
        </div>
        <div className="card-body">
          <form className="form-grid" onSubmit={onGenerate}>
            <div className="form-group">
              <label htmlFor="an-end-month">{t("forms.endMonth")}</label>
              <input
                id="an-end-month"
                type="month"
                value={endMonth}
                onChange={(event) => setEndMonth(event.target.value)}
                required
              />
            </div>
            <div className="form-actions">
              <button className="btn btn-primary" type="submit" disabled={submitting}>
                {t("actions.generate")}
              </button>
            </div>
          </form>
        </div>
      </div>

      {loading ? <LoadingState /> : null}
      {!loading && records.length === 0 ? <EmptyState /> : null}

      {records.length > 0 ? (
        <div className="card">
          <div className="card-header">
            <div className="card-title">{t("analysis.view")}</div>
          </div>
          <div className="card-body">
            <div className="form-group">
              <label htmlFor="an-select">{t("analysis.view")}</label>
              <select id="an-select" value={selectedId} onChange={(event) => setSelectedId(event.target.value)}>
                {records.map((item) => (
                  <option key={String(item.id)} value={String(item.id)}>
                    {String(item.cutoff_month ?? item.id)}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      ) : null}

      {detail ? (
        <>
          <div className="stats-grid">
            <article className="stat-card green">
              <div className="stat-label">{t("analysis.state")}</div>
              <div className="stat-value">
                {detail.state ? (
                  <span className={analysisStateClass(detail.state)}>{String(detail.state)}</span>
                ) : (
                  "-"
                )}
              </div>
            </article>
            <article className="stat-card blue">
              <div className="stat-label">{t("analysis.modelVersion")}</div>
              <div className="stat-value">{String(detail.model_version ?? "-")}</div>
            </article>
            <article className="stat-card earth">
              <div className="stat-label">{t("analysis.generatedAt")}</div>
              <div className="stat-value">{String(detail.generated_at ?? "-")}</div>
            </article>
            <article className="stat-card amber">
              <div className="stat-label">{t("analysis.horizon")}</div>
              <div className="stat-value">
                {String((detail.forecast as Record<string, unknown> | undefined)?.horizon_months ?? "-")}
              </div>
            </article>
          </div>

          <div className="card">
            <div className="card-header">
              <div className="card-title">{t("analysis.facts")}</div>
            </div>
            <div className="card-body">
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
                {t("analysis.coverage")}:{" "}
                {String((detail.coverage as Record<string, unknown> | undefined)?.month_count ?? "-")}
              </p>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <div className="card-title">{t("analysis.estimates")}</div>
            </div>
            <div className="card-body">
              {String(detail.state) === "insufficient_data" ? <p>{t("analysis.insufficientDataBody")}</p> : null}
              <p className="estimate-label">{t("analysis.estimateLabel")}</p>
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
                    {estimates.length > 0 ? (
                      estimates.map((row) => (
                        <tr key={String(row.month)}>
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
          </div>

          <div className="card">
            <div className="card-header">
              <div className="card-title">{t("analysis.narrative")}</div>
            </div>
            <div className="card-body">
              <p>{String(narrative || "-")}</p>
            </div>
          </div>
        </>
      ) : null}
    </section>
  );
}
