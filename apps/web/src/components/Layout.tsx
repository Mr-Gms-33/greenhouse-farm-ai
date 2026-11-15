import { useMemo, useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { LanguageSwitcher } from "./LanguageSwitcher";
import { useAuth } from "../auth";

type NavItem = {
  to: string;
  key: string;
  section: "ops" | "finance";
  roles: Array<"owner" | "manager" | "accountant">;
};

const navItems: NavItem[] = [
  { to: "/", key: "dashboard", section: "ops", roles: ["owner", "manager", "accountant"] },
  { to: "/greenhouses", key: "greenhouses", section: "ops", roles: ["owner", "manager", "accountant"] },
  { to: "/crop-cycles", key: "cropCycles", section: "ops", roles: ["owner", "manager", "accountant"] },
  { to: "/harvests", key: "harvests", section: "ops", roles: ["owner", "manager", "accountant"] },
  { to: "/customers", key: "customers", section: "finance", roles: ["owner", "accountant"] },
  { to: "/sales", key: "sales", section: "finance", roles: ["owner", "accountant"] },
  { to: "/expenses", key: "expenses", section: "finance", roles: ["owner", "accountant"] },
  { to: "/reports", key: "reports", section: "finance", roles: ["owner", "accountant"] },
  { to: "/analysis", key: "analyses", section: "finance", roles: ["owner", "accountant"] }
];

const titleByPath: Record<string, string> = {
  "/": "dashboard",
  "/greenhouses": "greenhouses",
  "/crop-cycles": "cropCycles",
  "/harvests": "harvests",
  "/customers": "customers",
  "/sales": "sales",
  "/expenses": "expenses",
  "/reports": "reports",
  "/analysis": "analyses"
};

export function Layout(): JSX.Element {
  const { t } = useTranslation();
  const { user, logout } = useAuth();
  const location = useLocation();
  const [navOpen, setNavOpen] = useState(false);

  const visible = useMemo(
    () => navItems.filter((item) => user && item.roles.includes(user.role)),
    [user]
  );
  const ops = visible.filter((i) => i.section === "ops");
  const finance = visible.filter((i) => i.section === "finance");
  const pageKey = titleByPath[location.pathname] ?? "dashboard";
  const initials = (user?.email?.[0] ?? "U").toUpperCase();

  return (
    <div className={`app${navOpen ? " nav-open" : ""}`}>
      {navOpen ? <button type="button" className="sidebar-open-backdrop" aria-label="Close menu" onClick={() => setNavOpen(false)} /> : null}

      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-mark">ف</div>
          <div>
            <div className="brand">
              {t("brand.short")} <span>Pro</span>
            </div>
            <div className="sub">{t("brand.tagline")}</div>
          </div>
        </div>

        <div className="nav-section">{t("navSections.operations")}</div>
        {ops.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}
            onClick={() => setNavOpen(false)}
          >
            {t(`nav.${item.key}`)}
          </NavLink>
        ))}

        {finance.length > 0 ? (
          <>
            <div className="nav-section">{t("navSections.finance")}</div>
            {finance.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}
                onClick={() => setNavOpen(false)}
              >
                {t(`nav.${item.key}`)}
              </NavLink>
            ))}
          </>
        ) : null}

        <div className="sidebar-foot">
          <button type="button" className="btn btn-ghost" style={{ width: "100%", color: "rgba(255,255,255,.7)" }} onClick={() => void logout()}>
            {t("actions.logout")}
          </button>
        </div>
      </aside>

      <div className="main">
        <header className="topbar">
          <div className="topbar-left">
            <button type="button" className="hamburger" aria-label="Menu" onClick={() => setNavOpen((v) => !v)}>
              ☰
            </button>
            <h1>{t(`nav.${pageKey}`)}</h1>
          </div>
          <div className="topbar-right">
            <LanguageSwitcher />
            <div className="user-pill">
              <div>
                <div className="user-name">{user?.email}</div>
                <div className="user-role">{user?.role ? t(`roles.${user.role}`) : ""}</div>
              </div>
              <div className="user-avatar">{initials}</div>
            </div>
          </div>
        </header>
        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
