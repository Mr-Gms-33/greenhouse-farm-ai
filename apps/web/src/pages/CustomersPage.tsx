import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { request, toErrorMessage } from "../api";
import { useAuth } from "../auth";
import { EmptyState, ErrorState, LoadingState } from "../components/Status";
import { extractArray } from "../utils";

type CustomerForm = {
  name: string;
  contact_ref: string;
};

const initialForm: CustomerForm = { name: "", contact_ref: "" };

export function CustomersPage(): JSX.Element {
  const { t } = useTranslation();
  const { token, user } = useAuth();
  const canWrite = user?.role === "owner" || user?.role === "accountant";
  const [records, setRecords] = useState<Array<Record<string, unknown>>>([]);
  const [form, setForm] = useState<CustomerForm>(initialForm);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function load(): Promise<void> {
    if (!token) return;
    setLoading(true);
    setError("");
    try {
      const result = await request<unknown>("/customers", {}, token);
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
        "/customers",
        {
          method: "POST",
          body: JSON.stringify({ name: form.name, contact_ref: form.contact_ref || null })
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
      <h1>{t("entities.customers")}</h1>
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
            {t("forms.contactRef")}
            <input
              value={form.contact_ref}
              onChange={(event) => setForm((prev) => ({ ...prev, contact_ref: event.target.value }))}
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
                <th>{t("forms.contactRef")}</th>
              </tr>
            </thead>
            <tbody>
              {records.map((item) => (
                <tr key={String(item.id)}>
                  <td>{String(item.name ?? "-")}</td>
                  <td>{String(item.contact_ref ?? "-")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </section>
  );
}
