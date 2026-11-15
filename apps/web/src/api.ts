import type { ApiErrorPayload } from "./types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  status: number;

  detail: unknown;

  constructor(status: number, detail: unknown) {
    super(typeof detail === "string" ? detail : "API request failed");
    this.status = status;
    this.detail = detail;
  }
}

async function parseResponse(response: Response): Promise<unknown> {
  const text = await response.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export function toErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (typeof error.detail === "string") return error.detail;
    if (error.detail && typeof error.detail === "object") {
      return JSON.stringify(error.detail);
    }
    return error.message;
  }
  if (error instanceof Error) return error.message;
  return "Request failed";
}

export async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string
): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Accept", "application/json");
  if (!(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers
  });
  const payload = (await parseResponse(response)) as ApiErrorPayload | null;

  if (!response.ok) {
    throw new ApiError(response.status, payload?.detail ?? payload ?? response.statusText);
  }
  return payload as T;
}

export { API_URL };
