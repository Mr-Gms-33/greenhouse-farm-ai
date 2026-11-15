import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { I18nextProvider } from "react-i18next";
import App from "../App";
import { AuthProvider } from "../auth";
import i18n from "../i18n";
import { LanguageSwitcher } from "../components/LanguageSwitcher";

function mockFetch(routes: Record<string, unknown>): void {
  vi.spyOn(globalThis, "fetch").mockImplementation((input: RequestInfo | URL) => {
    const url = String(input);
    const match = Object.entries(routes).find(([path]) => url.includes(path));
    const body = match ? match[1] : {};
    return Promise.resolve(
      new Response(JSON.stringify(body), {
        status: 200,
        headers: { "Content-Type": "application/json" }
      })
    );
  });
}

function renderApp(initialPath = "/"): void {
  render(
    <I18nextProvider i18n={i18n}>
      <AuthProvider>
        <MemoryRouter initialEntries={[initialPath]}>
          <App />
        </MemoryRouter>
      </AuthProvider>
    </I18nextProvider>
  );
}

describe("Greenhouse web app", () => {
  beforeEach(async () => {
    vi.restoreAllMocks();
    localStorage.clear();
    await i18n.changeLanguage("en");
    document.documentElement.dir = "ltr";
    document.documentElement.lang = "en";
  });

  it("logs in and stores session token", async () => {
    const user = userEvent.setup();
    mockFetch({
      "/auth/login": {
        access_token: "jwt-test-token",
        user: { id: "u1", email: "owner@example.com", role: "owner" }
      },
      "/dashboard": { active_greenhouses: 2, active_crop_cycles: 1, revenue: 100, expenses: 20, profit: 80, margin: 80 }
    });

    renderApp("/login");
    await user.type(screen.getByLabelText("Email"), "owner@example.com");
    await user.type(screen.getByLabelText("Password"), "secret");
    await user.click(screen.getByRole("button", { name: "Sign in" }));

    await waitFor(() => {
      expect(localStorage.getItem("gh_token")).toBe("jwt-test-token");
    });
  });

  it("switches locale and updates document direction", async () => {
    const user = userEvent.setup();
    render(
      <I18nextProvider i18n={i18n}>
        <LanguageSwitcher />
      </I18nextProvider>
    );

    await user.selectOptions(screen.getByLabelText("Language"), "ar");
    await waitFor(() => {
      expect(document.documentElement.dir).toBe("rtl");
      expect(document.documentElement.lang).toBe("ar");
    });
  });

  it("hides finance navigation for manager role", async () => {
    localStorage.setItem("gh_token", "token");
    localStorage.setItem(
      "gh_user",
      JSON.stringify({ id: "u2", email: "manager@example.com", role: "manager" })
    );

    mockFetch({
      "/dashboard": { active_greenhouses: 1, active_crop_cycles: 1 }
    });

    renderApp("/");
    expect(await screen.findByRole("link", { name: "Dashboard" })).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Reports" })).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Financial analysis" })).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Sales" })).not.toBeInTheDocument();
  });

  it("shows estimate label on analysis view", async () => {
    localStorage.setItem("gh_token", "token");
    localStorage.setItem(
      "gh_user",
      JSON.stringify({ id: "u3", email: "owner@example.com", role: "owner" })
    );

    mockFetch({
      "/analyses/1": {
        id: "1",
        state: "ready",
        model_version: "trend-v1",
        generated_at: "2026-11-01T00:00:00Z",
        facts: { revenue: 1000, expenses: 300, profit: 700 },
        coverage: { month_count: 8 },
        forecast: {
          horizon_months: 3,
          monthly: [
            { month: "2026-12", revenue: 1100, expenses: 350, profit: 750 },
            { month: "2027-01", revenue: 1120, expenses: 360, profit: 760 },
            { month: "2027-02", revenue: 1140, expenses: 370, profit: 770 }
          ]
        },
        narrative_en: "Estimated values are shown clearly."
      },
      "/analyses": [{ id: "1", cutoff_month: "2026-11" }]
    });

    renderApp("/analysis");
    expect(await screen.findByText("Estimate, not recorded fact")).toBeInTheDocument();
  });
});
