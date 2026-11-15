import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { request, toErrorMessage } from "../api";
import { useAuth } from "../auth";
import { EmptyState, ErrorState, LoadingState } from "../components/Status";
import { extractArray, formatCurrency } from "../utils";

type SaleForm = {
  sale_date: string;
  customer_id: string;
  crop_cycle_id: string;
  quantity_kg: string;
  unit_price_mad: string;
  channel: "wholesaler" | "market" | "distributor" | "other";
  external_ref: string;
  notes: string;
};

const initialForm: SaleForm = {
  sale_date: "",
  customer_id: "",
  crop_cycle_id: "",
  quantity_kg: "",
  unit_price_mad: "",
  channel: "wholesaler",
  external_ref: "",
  notes: ""
};

export function SalesPage(): JSX.Element {
  const { t } = useTranslation();
  const { token, user } = useAuth();
  const canWrite = user?.role === "owner" || user?.role === "accountant";
  const [records, setRecords] = useState<Array<Record<string, unknown>>>([]);
  const [customers, setCustomers] = useState<Array<Record<string, unknown>>>([]);
  const [cycles, setCycles] = useState<Array<Record<string, unknown>>>([]);
  const [form, setForm] = useState<SaleForm>(initialForm);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const computedTotal = useMemo(() => {
    const quantity = Number(form.quantity_kg);
    const unitPrice = Number(form.unit_price_mad);
    if (!quantity || !unitPrice) return 0;
    return quantity * unitPrice;
  }, [form.quantity_kg, form.unit_price_mad]);

  async function load(): Promise<void> {
    if (!token) return;
    setLoading(true);
    setError("");
    try {
      const [salesResult, customerResult, cycleResult] = await Promise.all([
        request<unknown>("/sales", {}, token),
        request<unknown>("/customers", {}, token),
        request<unknown>("/crop-cycles", {}, token)
      ]);
      setRecords(extractArray(salesResult));
      const customerRows = extractArray(customerResult);
      const cycleRows = extractArray(cycleResult);
      setCustomers(customerRows);
      setCycles(cycleRows);
      setForm((prev) => ({
        ...prev,
        customer_id: prev.customer_id || String(customerRows[0]?.id ?? ""),
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
        "/sales",
        {
          method: "POST",
          headers: { "Idempotency-Key": crypto.randomUUID() },
          body: JSON.stringify({
            sale_date: form.sale_date,
            customer_id: form.customer_id,
            crop_cycle_id: form.crop_cycle_id,
            quantity_kg: Number(form.quantity_kg),
            unit_price_mad: Number(form.unit_price_mad),
            channel: form.channel,
            external_ref: form.external_ref || null,
            notes: form.notes || null
          })
        },
        token
      );
      setForm((prev) => ({
        ...initialForm,
        customer_id: prev.customer_id,
        crop_cycle_id: prev.crop_cycle_id
      }));
      await load();
    } catch (caught) {
      setError(toErrorMessage(caught));
    }
  }

  return (
    <section className="stack">
      <p className="page-intro">{t("entities.sales")}</p>
      {error ? <ErrorState message={error} /> : null}

      {canWrite ? (
        <div className="card">
          <div className="card-header">
            <div className="card-title">{t("actions.create")}</div>
          </div>
          <div className="card-body">
            <form className="form-grid" onSubmit={onSubmit}>
              <div className="form-group">
                <label htmlFor="sl-date">{t("forms.saleDate")}</label>
                <input
                  id="sl-date"
                  type="date"
                  value={form.sale_date}
                  onChange={(event) => setForm((prev) => ({ ...prev, sale_date: event.target.value }))}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="sl-customer">{t("forms.customer")}</label>
                <select
                  id="sl-customer"
                  value={form.customer_id}
                  onChange={(event) => setForm((prev) => ({ ...prev, customer_id: event.target.value }))}
                  required
                >
                  {customers.map((item) => (
                    <option key={String(item.id)} value={String(item.id)}>
                      {String(item.name ?? item.id)}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="sl-cycle">{t("forms.crop")}</label>
                <select
                  id="sl-cycle"
                  value={form.crop_cycle_id}
                  onChange={(event) => setForm((prev) => ({ ...prev, crop_cycle_id: event.target.value }))}
                  required
                >
                  {cycles.map((item) => (
                    <option key={String(item.id)} value={String(item.id)}>
                      {String(item.id)} - {item.crop ? t(`crops.${String(item.crop)}`) : ""}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label htmlFor="sl-qty">{t("forms.quantityKg")}</label>
                <input
                  id="sl-qty"
                  type="number"
                  min={0.01}
                  step={0.01}
                  value={form.quantity_kg}
                  onChange={(event) => setForm((prev) => ({ ...prev, quantity_kg: event.target.value }))}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="sl-price">{t("forms.unitPriceMad")}</label>
                <input
                  id="sl-price"
                  type="number"
                  min={0}
                  step={0.01}
                  value={form.unit_price_mad}
                  onChange={(event) => setForm((prev) => ({ ...prev, unit_price_mad: event.target.value }))}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="sl-channel">{t("forms.channel")}</label>
                <select
                  id="sl-channel"
                  value={form.channel}
                  onChange={(event) =>
                    setForm((prev) => ({ ...prev, channel: event.target.value as SaleForm["channel"] }))
                  }
                >
                  {["wholesaler", "market", "distributor", "other"].map((channel) => (
                    <option key={channel} value={channel}>
                      {t(`channels.${channel}`)}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group form-full">
                <span>
                  {t("forms.totalMad")}: <strong>{formatCurrency(computedTotal)}</strong>
                </span>
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
            <div className="card-title">{t("entities.sales")}</div>
          </div>
          <div className="card-body table-wrap">
            <table>
              <thead>
                <tr>
                  <th>{t("forms.saleDate")}</th>
                  <th>{t("forms.customer")}</th>
                  <th>{t("forms.totalMad")}</th>
                </tr>
              </thead>
              <tbody>
                {records.map((item) => (
                  <tr key={String(item.id)}>
                    <td>{String(item.sale_date ?? "-")}</td>
                    <td>{String(item.customer_name ?? item.customer_id ?? "-")}</td>
                    <td className="td-num">{formatCurrency(Number(item.total ?? item.total_mad ?? 0))}</td>
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
