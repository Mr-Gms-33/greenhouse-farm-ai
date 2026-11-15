import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { request, toErrorMessage } from "../api";
import { useAuth } from "../auth";
import { EmptyState, ErrorState, LoadingState } from "../components/Status";
import { extractArray } from "../utils";

type GreenhouseForm = {
  name: string;
  area_m2: string;
  status: "active" | "inactive";
  notes: string;
};

const initialForm: GreenhouseForm = { name: "", area_m2: "", status: "active", notes: "" };

export function GreenhousesPage(): JSX.Element {
  const { t } = useTranslation();
  const { token, user } = useAuth();
  const [records, setRecords] = useState<Array<Record<string, unknown>>>([]);
  const [form, setForm] = useState<GreenhouseForm>(initialForm);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const canWrite = user?.role === "owner" || user?.role === "manager";

  async function load(): Promise<void> {
    if (!token) return;
    setLoading(true);
    setError("");
    try {
      const result = await request<unknown>("/greenhouses", {}, token);
      setRecords(extractArray(result));
    } catch (caught) {
      setError(toErrorMessage(caught));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, [token]);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (!token || !canWrite) return;
    setError("");
    try {
      await request(
        "/greenhouses",
        {
          method: "POST",
          body: JSON.stringify({
            name: form.name,
            area_m2: Number(form.area_m2),
            status: form.status,
            notes: form.notes || null
          })
        },
        token
      );
      setForm(initialForm);
      await load();
    } catch (caught) {
      setError(toErrorMessage(caught));
    }
  }

  return (
    <section className="stack">
      <p className="page-intro">{t("entities.greenhouses")}</p>
      {error ? <ErrorState message={error} /> : null}

      {canWrite ? (
        <div className="card">
          <div className="card-header">
            <div className="card-title">{t("actions.create")}</div>
          </div>
          <div className="card-body">
            <form className="form-grid" onSubmit={onSubmit}>
              <div className="form-group">
                <label htmlFor="gh-name">{t("forms.name")}</label>
                <input
                  id="gh-name"
                  value={form.name}
                  onChange={(event) => setForm((prev) => ({ ...prev, name: event.target.value }))}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="gh-area">{t("forms.areaM2")}</label>
                <input
                  id="gh-area"
                  value={form.area_m2}
                  type="number"
                  min={0.01}
                  step={0.01}
                  onChange={(event) => setForm((prev) => ({ ...prev, area_m2: event.target.value }))}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="gh-status">{t("forms.status")}</label>
                <select
                  id="gh-status"
                  value={form.status}
                  onChange={(event) =>
                    setForm((prev) => ({ ...prev, status: event.target.value as GreenhouseForm["status"] }))
                  }
                >
                  <option value="active">{t("greenhouseStatus.active")}</option>
                  <option value="inactive">{t("greenhouseStatus.inactive")}</option>
                </select>
              </div>
              <div className="form-group form-full">
                <label htmlFor="gh-notes">{t("forms.notes")}</label>
                <textarea
                  id="gh-notes"
                  value={form.notes}
                  onChange={(event) => setForm((prev) => ({ ...prev, notes: event.target.value }))}
                />
              </div>
              <div className="form-actions">
                <button className="btn btn-primary" type="submit">
                  {t("actions.create")}
                </button>
              </div>
            </form>
          </div>
        </div>
      ) : null}

      {loading ? <LoadingState /> : null}
      {!loading && records.length === 0 ? <EmptyState /> : null}

      {records.length > 0 ? (
        <div className="plots-grid">
          {records.map((item) => (
            <article key={String(item.id ?? item.name)} className="plot-card">
              <div className="plot-card-banner">⌂</div>
              <div className="plot-card-body">
                <div className="plot-card-name">{String(item.name ?? item.code ?? "-")}</div>
                <div className="plot-card-meta">
                  <span className={`badge ${item.status === "active" ? "badge-green" : "badge-gray"}`}>
                    {item.status ? t(`greenhouseStatus.${String(item.status)}`) : t("status.none")}
                  </span>
                </div>
                <div className="plot-card-stats">
                  <div className="plot-stat">
                    <div className="l">{t("forms.areaM2")}</div>
                    <div className="v">{String(item.area_m2 ?? "-")}</div>
                  </div>
                  <div className="plot-stat">
                    <div className="l">{t("forms.status")}</div>
                    <div className="v">{item.status ? t(`greenhouseStatus.${String(item.status)}`) : "-"}</div>
                  </div>
                </div>
              </div>
            </article>
          ))}
        </div>
      ) : null}
    </section>
  );
}
