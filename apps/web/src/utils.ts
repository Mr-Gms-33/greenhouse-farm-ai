import i18n from "./i18n";

export function formatCurrency(value: number | string | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "-";
  const locale = i18n.language === "ar" ? "ar-MA" : "en-MA";
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency: "MAD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(Number(value));
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return "-";
  const locale = i18n.language === "ar" ? "ar-MA" : "en-MA";
  return new Intl.DateTimeFormat(locale, { dateStyle: "medium" }).format(new Date(value));
}

export function marginLabel(value: number | null | undefined): string {
  if (value === null || value === undefined) return "-";
  return `${value.toFixed(2)}%`;
}

export function extractArray(payload: unknown): Array<Record<string, unknown>> {
  if (Array.isArray(payload)) {
    return payload.filter((row): row is Record<string, unknown> => typeof row === "object" && row !== null);
  }
  if (payload && typeof payload === "object") {
    const candidate = payload as Record<string, unknown>;
    if (Array.isArray(candidate.items)) {
      return candidate.items.filter(
        (row): row is Record<string, unknown> => typeof row === "object" && row !== null
      );
    }
  }
  return [];
}
