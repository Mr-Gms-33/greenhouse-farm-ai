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
      <h1>{t("entities.greenhouses")}</h1>
      {canWrite ? (
        <form className="form-grid" onSubmit={onSubmit}>
          <label>
            {t("forms.name")}
            <input
              value={form.name}
              onChange={(event) => setForm((prev) => ({ ...prev, name: event.target.value }))}
              required
            />
          </label>
          <label>
            {t("forms.areaM2")}
            <input
              value={form.area_m2}
              type="number"
              min={0.01}
              step={0.01}
              onChange={(event) => setForm((prev) => ({ ...prev, area_m2: event.target.value }))}
              required
            />
          </label>
          <label>
            {t("forms.status")}
            <select
              value={form.status}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, status: event.target.value as GreenhouseForm["status"] }))
              }
            >
              <option value="active">{t("greenhouseStatus.active")}</option>
              <option value="inactive">{t("greenhouseStatus.inactive")}</option>
            </select>
          </label>
          <label>
            {t("forms.notes")}
            <textarea
              value={form.notes}
              onChange={(event) => setForm((prev) => ({ ...prev, notes: event.target.value }))}
            />
          </label>
          <button type="submit">{t("actions.create")}</button>
        </form>
      ) : null}
      {error ? <ErrorState message={error} /> : null}
      {loading ? <LoadingState /> : null}
      {!loading && records.length === 0 ? <EmptyState /> : null}
      {records.length > 0 ? (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>{t("forms.name")}</th>
                <th>{t("forms.areaM2")}</th>
                <th>{t("forms.status")}</th>
              </tr>
            </thead>
            <tbody>
              {records.map((item) => (
                <tr key={String(item.id ?? item.name)}>
                  <td>{String(item.name ?? item.code ?? "-")}</td>
                  <td>{String(item.area_m2 ?? "-")}</td>
                  <td>
                    {item.status ? t(`greenhouseStatus.${String(item.status)}`) : t("status.none")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </section>
  );
}
