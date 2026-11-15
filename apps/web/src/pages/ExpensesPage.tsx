import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { request, toErrorMessage } from "../api";
import { useAuth } from "../auth";
import { EmptyState, ErrorState, LoadingState } from "../components/Status";
import { extractArray, formatCurrency } from "../utils";

type ExpenseScope = "farm" | "greenhouse" | "crop_cycle";
type ExpenseForm = {
  expense_date: string;
  category: string;
  amount_mad: string;
  scope: ExpenseScope;
  greenhouse_id: string;
  crop_cycle_id: string;
  notes: string;
};

const initialForm: ExpenseForm = {
  expense_date: "",
  category: "water",
  amount_mad: "",
  scope: "farm",
  greenhouse_id: "",
  crop_cycle_id: "",
  notes: ""
};

export function ExpensesPage(): JSX.Element {
  const { t } = useTranslation();
  const { token, user } = useAuth();
  const canWrite = user?.role === "owner" || user?.role === "accountant";
  const [records, setRecords] = useState<Array<Record<string, unknown>>>([]);
  const [greenhouses, setGreenhouses] = useState<Array<Record<string, unknown>>>([]);
  const [cycles, setCycles] = useState<Array<Record<string, unknown>>>([]);
  const [form, setForm] = useState<ExpenseForm>(initialForm);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function load(): Promise<void> {
    if (!token) return;
    setLoading(true);
    setError("");
    try {
      const [expenseResult, greenhouseResult, cycleResult] = await Promise.all([
        request<unknown>("/expenses", {}, token),
        request<unknown>("/greenhouses", {}, token),
        request<unknown>("/crop-cycles", {}, token)
      ]);
      setRecords(extractArray(expenseResult));
      const greenhouseRows = extractArray(greenhouseResult);
      const cycleRows = extractArray(cycleResult);
      setGreenhouses(greenhouseRows);
      setCycles(cycleRows);
      setForm((prev) => ({
        ...prev,
        greenhouse_id: prev.greenhouse_id || String(greenhouseRows[0]?.id ?? ""),
        crop_cycle_id: prev.crop_cycle_id || String(cycleRows[0]?.id ?? "")
      }));
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
        "/expenses",
        {
          method: "POST",
          headers: { "Idempotency-Key": crypto.randomUUID() },
          body: JSON.stringify({
            expense_date: form.expense_date,
            category: form.category,
            amount_mad: Number(form.amount_mad),
            scope: form.scope,
            greenhouse_id: form.scope === "greenhouse" ? form.greenhouse_id : null,
            crop_cycle_id: form.scope === "crop_cycle" ? form.crop_cycle_id : null,
            notes: form.notes || null
          })
        },
        token
      );
      setForm((prev) => ({
        ...initialForm,
        greenhouse_id: prev.greenhouse_id,
        crop_cycle_id: prev.crop_cycle_id
      }));
      await load();
    } catch (caught) {
      setError(toErrorMessage(caught));
    }
  }

  return (
    <section className="stack">
      <p className="page-intro">{t("entities.expenses")}</p>
      {error ? <ErrorState message={error} /> : null}

      {canWrite ? (
        <div className="card">
          <div className="card-header">
            <div className="card-title">{t("actions.create")}</div>
          </div>
          <div className="card-body">
            <form className="form-grid" onSubmit={onSubmit}>
              <div className="form-group">
                <label htmlFor="ex-date">{t("forms.expenseDate")}</label>
                <input
                  id="ex-date"
                  type="date"
                  value={form.expense_date}
                  onChange={(event) => setForm((prev) => ({ ...prev, expense_date: event.target.value }))}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="ex-category">{t("forms.category")}</label>
                <select
                  id="ex-category"
                  value={form.category}
                  onChange={(event) => setForm((prev) => ({ ...prev, category: event.target.value }))}
                >
                  {[
                    "seeds_plants",
                    "fertilizer",
                    "water",
                    "energy",
                    "labor",
                    "equipment",
                    "maintenance",
                    "transport",
                    "packaging",
                    "other"
                  ].map((category) => (
                    <option key={category} value={category}>
                      {t(`expenseCategories.${category}`)}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="ex-amount">{t("forms.amountMad")}</label>
                <input
                  id="ex-amount"
                  type="number"
                  min={0.01}
                  step={0.01}
                  value={form.amount_mad}
                  onChange={(event) => setForm((prev) => ({ ...prev, amount_mad: event.target.value }))}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="ex-scope">{t("forms.scope")}</label>
                <select
                  id="ex-scope"
                  value={form.scope}
                  onChange={(event) => setForm((prev) => ({ ...prev, scope: event.target.value as ExpenseScope }))}
                >
                  {["farm", "greenhouse", "crop_cycle"].map((scope) => (
                    <option key={scope} value={scope}>
                      {t(`scopes.${scope}`)}
                    </option>
                  ))}
                </select>
              </div>
              {form.scope === "greenhouse" ? (
                <div className="form-group">
                  <label htmlFor="ex-greenhouse">{t("forms.greenhouse")}</label>
                  <select
                    id="ex-greenhouse"
                    value={form.greenhouse_id}
                    onChange={(event) => setForm((prev) => ({ ...prev, greenhouse_id: event.target.value }))}
                  >
                    {greenhouses.map((item) => (
                      <option key={String(item.id)} value={String(item.id)}>
                        {String(item.name ?? item.id)}
                      </option>
                    ))}
                  </select>
                </div>
              ) : null}
              {form.scope === "crop_cycle" ? (
                <div className="form-group">
                  <label htmlFor="ex-cycle">{t("forms.crop")}</label>
                  <select
                    id="ex-cycle"
                    value={form.crop_cycle_id}
                    onChange={(event) => setForm((prev) => ({ ...prev, crop_cycle_id: event.target.value }))}
                  >
                    {cycles.map((item) => (
                      <option key={String(item.id)} value={String(item.id)}>
                        {String(item.id)}
                      </option>
                    ))}
                  </select>
                </div>
              ) : null}
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
            <div className="card-title">{t("entities.expenses")}</div>
          </div>
          <div className="card-body table-wrap">
            <table>
              <thead>
                <tr>
                  <th>{t("forms.expenseDate")}</th>
                  <th>{t("forms.category")}</th>
                  <th>{t("forms.scope")}</th>
                  <th>{t("forms.amountMad")}</th>
                </tr>
              </thead>
              <tbody>
                {records.map((item) => (
                  <tr key={String(item.id)}>
                    <td>{String(item.expense_date ?? "-")}</td>
                    <td>{item.category ? t(`expenseCategories.${String(item.category)}`) : "-"}</td>
                    <td>{item.scope ? t(`scopes.${String(item.scope)}`) : "-"}</td>
                    <td className="td-num">{formatCurrency(Number(item.amount_mad ?? item.amount ?? 0))}</td>
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
