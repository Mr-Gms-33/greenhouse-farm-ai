import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { request, toErrorMessage } from "../api";
import { useAuth } from "../auth";
import { EmptyState, ErrorState, LoadingState } from "../components/Status";
import { extractArray } from "../utils";

type CycleForm = {
  greenhouse_id: string;
  crop: "tomato" | "pepper" | "zucchini" | "cucumber";
  planting_date: string;
  expected_end_date: string;
  status: "planned" | "active" | "completed" | "cancelled";
};

const initialForm: CycleForm = {
  greenhouse_id: "",
  crop: "tomato",
  planting_date: "",
  expected_end_date: "",
  status: "planned"
};

export function CropCyclesPage(): JSX.Element {
  const { t } = useTranslation();
  const { token, user } = useAuth();
  const [records, setRecords] = useState<Array<Record<string, unknown>>>([]);
  const [greenhouses, setGreenhouses] = useState<Array<Record<string, unknown>>>([]);
  const [form, setForm] = useState<CycleForm>(initialForm);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const canWrite = user?.role === "owner" || user?.role === "manager";

  async function load(): Promise<void> {
    if (!token) return;
    setLoading(true);
    setError("");
    try {
      const [cyclesResult, greenhousesResult] = await Promise.all([
        request<unknown>("/crop-cycles", {}, token),
        request<unknown>("/greenhouses", {}, token)
      ]);
      setRecords(extractArray(cyclesResult));
      const gh = extractArray(greenhousesResult);
      setGreenhouses(gh);
      if (!form.greenhouse_id && gh[0]?.id) {
        setForm((prev) => ({ ...prev, greenhouse_id: String(gh[0].id) }));
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
        "/crop-cycles",
        {
          method: "POST",
          body: JSON.stringify({
            greenhouse_id: form.greenhouse_id,
            crop: form.crop,
            planting_date: form.planting_date,
            expected_end_date: form.expected_end_date || null,
            status: form.status
          })
        },
        token
      );
      setForm((prev) => ({ ...initialForm, greenhouse_id: prev.greenhouse_id }));
      await load();
    } catch (caught) {
      setError(toErrorMessage(caught));
    }
  }

  return (
    <section className="stack">
      <h1>{t("entities.cropCycles")}</h1>
      {canWrite ? (
        <form className="form-grid" onSubmit={onSubmit}>
          <label>
            {t("forms.greenhouse")}
            <select
              value={form.greenhouse_id}
              onChange={(event) => setForm((prev) => ({ ...prev, greenhouse_id: event.target.value }))}
              required
            >
              {greenhouses.map((item) => (
                <option key={String(item.id)} value={String(item.id)}>
                  {String(item.name ?? item.code ?? item.id)}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("forms.crop")}
            <select
              value={form.crop}
              onChange={(event) => setForm((prev) => ({ ...prev, crop: event.target.value as CycleForm["crop"] }))}
            >
              {["tomato", "pepper", "zucchini", "cucumber"].map((crop) => (
                <option key={crop} value={crop}>
                  {t(`crops.${crop}`)}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t("forms.plantingDate")}
            <input
              type="date"
              value={form.planting_date}
              onChange={(event) => setForm((prev) => ({ ...prev, planting_date: event.target.value }))}
              required
            />
          </label>
          <label>
            {t("forms.expectedEndDate")}
            <input
              type="date"
              value={form.expected_end_date}
              onChange={(event) => setForm((prev) => ({ ...prev, expected_end_date: event.target.value }))}
            />
          </label>
          <label>
            {t("forms.cycleStatus")}
            <select
              value={form.status}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, status: event.target.value as CycleForm["status"] }))
              }
            >
              {["planned", "active", "completed", "cancelled"].map((status) => (
                <option key={status} value={status}>
                  {t(`cycleStatus.${status}`)}
                </option>
              ))}
            </select>
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
                <th>{t("forms.greenhouse")}</th>
                <th>{t("forms.crop")}</th>
                <th>{t("forms.plantingDate")}</th>
                <th>{t("forms.cycleStatus")}</th>
              </tr>
            </thead>
            <tbody>
              {records.map((item) => (
                <tr key={String(item.id)}>
                  <td>{String(item.greenhouse_name ?? item.greenhouse_id ?? "-")}</td>
                  <td>{item.crop ? t(`crops.${String(item.crop)}`) : "-"}</td>
                  <td>{String(item.planting_date ?? "-")}</td>
                  <td>{item.status ? t(`cycleStatus.${String(item.status)}`) : "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </section>
  );
}
