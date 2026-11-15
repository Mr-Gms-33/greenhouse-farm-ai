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

function cycleStatusClass(status: unknown): string {
  const value = String(status ?? "");
  if (value === "active") return "badge badge-green";
  if (value === "planned") return "badge badge-amber";
  return "badge badge-gray";
}

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
      <p className="page-intro">{t("entities.cropCycles")}</p>
      {error ? <ErrorState message={error} /> : null}

      {canWrite ? (
        <div className="card">
          <div className="card-header">
            <div className="card-title">{t("actions.create")}</div>
          </div>
          <div className="card-body">
            <form className="form-grid" onSubmit={onSubmit}>
              <div className="form-group">
                <label htmlFor="cc-greenhouse">{t("forms.greenhouse")}</label>
                <select
                  id="cc-greenhouse"
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
              </div>
              <div className="form-group">
                <label htmlFor="cc-crop">{t("forms.crop")}</label>
                <select
                  id="cc-crop"
                  value={form.crop}
                  onChange={(event) => setForm((prev) => ({ ...prev, crop: event.target.value as CycleForm["crop"] }))}
                >
                  {["tomato", "pepper", "zucchini", "cucumber"].map((crop) => (
                    <option key={crop} value={crop}>
                      {t(`crops.${crop}`)}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="cc-planting">{t("forms.plantingDate")}</label>
                <input
                  id="cc-planting"
                  type="date"
                  value={form.planting_date}
                  onChange={(event) => setForm((prev) => ({ ...prev, planting_date: event.target.value }))}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="cc-expected-end">{t("forms.expectedEndDate")}</label>
                <input
                  id="cc-expected-end"
                  type="date"
                  value={form.expected_end_date}
                  onChange={(event) => setForm((prev) => ({ ...prev, expected_end_date: event.target.value }))}
                />
              </div>
              <div className="form-group">
                <label htmlFor="cc-status">{t("forms.cycleStatus")}</label>
                <select
                  id="cc-status"
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
            <div className="card-title">{t("entities.cropCycles")}</div>
          </div>
          <div className="card-body table-wrap">
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
                    <td>
                      {item.status ? (
                        <span className={cycleStatusClass(item.status)}>
                          {t(`cycleStatus.${String(item.status)}`)}
                        </span>
                      ) : (
                        "-"
                      )}
                    </td>
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
