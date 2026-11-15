export type Role = "owner" | "manager" | "accountant";

export type User = {
  id: string;
  email: string;
  role: Role;
  locale?: "en" | "ar";
  active?: boolean;
};

export type ApiErrorPayload = {
  detail?: string | Record<string, unknown>;
  code?: string;
};
