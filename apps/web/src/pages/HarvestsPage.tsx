import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { request, toErrorMessage } from "../api";
import { useAuth } from "../auth";
import { EmptyState, ErrorState, LoadingState } from "../components/Status";
import { extractArray } from "../utils";

type HarvestForm = {
  crop_cycle_id: string;
  harvest_date: string;
  quantity_kg: string;
  quality_grade: string;
  notes: string;
};

const initialForm: HarvestForm = {
  crop_cycle_id: "",
  harvest_date: "",
  quantity_kg: "",
  quality_grade: "",
  notes: ""
};

export function HarvestsPage(): JSX.Element {
  const { t } = useTranslation();
  const { token, user } = useAuth();
  const [records, setRecords] = useState<Array<Record<string, unknown>>>([]);
  const [cycles, setCycles] = useState<Array<Record<string, unknown>>>([]);
  const [form, setForm] = useState<HarvestForm>(initialForm);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const canWrite = user?.role === "owner" || user?.role === "manager";

  async function load(): Promise<void> {
    if (!token) return;
    setLoading(true);
    setError("");
    try {
      const [harvestResult, cycleResult] = await Promise.all([
        request<unknown>("/harvests", {}, token),
        request<unknown>("/crop-cycles", {}, token)
      ]);
      setRecords(extractArray(harvestResult));
      const cycleRows = extractArray(cycleResult);
      setCycles(cycleRows);
      if (!form.crop_cycle_id && cycleRows[0]?.id) {
        setForm((prev) => ({ ...prev, crop_cycle_id: String(cycleRows[0].id) }));
      }
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
        "/harvests",
        {
          method: "POST",
          body: JSON.stringify({
            crop_cycle_id: form.crop_cycle_id,
            harvest_date: form.harvest_date,
            quantity_kg: Number(form.quantity_kg),
            quality_grade: form.quality_grade || null,
            notes: form.notes || null
          })
        },
        token
      );
      setForm((prev) => ({ ...initialForm, crop_cycle_id: prev.crop_cycle_id }));
      await load();
    } catch (caught) {
      setError(toErrorMessage(caught));
    }
  }

  return (
    <section className="stack">
      <p className="page-intro">{t("entities.harvests")}</p>
      {error ? <ErrorState message={error} /> : null}

      {canWrite ? (
        <div className="card">
          <div className="card-header">
            <div className="card-title">{t("actions.create")}</div>
          </div>
          <div className="card-body">
            <form className="form-grid" onSubmit={onSubmit}>
              <div className="form-group">
                <label htmlFor="hv-cycle">{t("forms.cycleStatus")}</label>
                <select
                  id="hv-cycle"
                  value={form.crop_cycle_id}
                  onChange={(event) => setForm((prev) => ({ ...prev, crop_cycle_id: event.target.value }))}
                  required
                >
                  {cycles.map((item) => (
                    <option key={String(item.id)} value={String(item.id)}>
                      {String(item.id)} - {item.crop ? t(`crops.${String(item.crop)}`) : "-"}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="hv-date">{t("forms.harvestDate")}</label>
                <input
                  id="hv-date"
                  type="date"
                  value={form.harvest_date}
                  onChange={(event) => setForm((prev) => ({ ...prev, harvest_date: event.target.value }))}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="hv-qty">{t("forms.quantityKg")}</label>
                <input
                  id="hv-qty"
                  type="number"
                  min={0.01}
                  step={0.01}
                  value={form.quantity_kg}
                  onChange={(event) => setForm((prev) => ({ ...prev, quantity_kg: event.target.value }))}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="hv-grade">{t("forms.qualityGrade")}</label>
                <input
                  id="hv-grade"
                  value={form.quality_grade}
                  onChange={(event) => setForm((prev) => ({ ...prev, quality_grade: event.target.value }))}
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

      {!loading && records.length > 0 ? (
        <div className="card">
          <div className="card-header">
            <div className="card-title">{t("entities.harvests")}</div>
          </div>
          <div className="card-body table-wrap">
            <table>
              <thead>
                <tr>
                  <th>{t("forms.harvestDate")}</th>
                  <th>{t("forms.quantityKg")}</th>
                  <th>{t("forms.cycleStatus")}</th>
                </tr>
              </thead>
              <tbody>
                {records.map((item) => (
                  <tr key={String(item.id)}>
                    <td>{String(item.harvest_date ?? "-")}</td>
                    <td className="td-num">{String(item.quantity_kg ?? "-")}</td>
                    <td>{String(item.crop_cycle_id ?? "-")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}
    </section>
  );
}
