import { Link, NavLink, Outlet } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { LanguageSwitcher } from "./LanguageSwitcher";
import { useAuth } from "../auth";

type NavItem = {
  to: string;
  key: string;
  roles: Array<"owner" | "manager" | "accountant">;
};

const navItems: NavItem[] = [
  { to: "/", key: "dashboard", roles: ["owner", "manager", "accountant"] },
  { to: "/greenhouses", key: "greenhouses", roles: ["owner", "manager", "accountant"] },
  { to: "/crop-cycles", key: "cropCycles", roles: ["owner", "manager", "accountant"] },
  { to: "/harvests", key: "harvests", roles: ["owner", "manager", "accountant"] },
  { to: "/customers", key: "customers", roles: ["owner", "accountant"] },
  { to: "/sales", key: "sales", roles: ["owner", "accountant"] },
  { to: "/expenses", key: "expenses", roles: ["owner", "accountant"] },
  { to: "/reports", key: "reports", roles: ["owner", "accountant"] },
  { to: "/analysis", key: "analyses", roles: ["owner", "accountant"] }
];

export function Layout(): JSX.Element {
  const { t } = useTranslation();
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <header className="top-bar">
        <Link to="/" className="brand">
          {t("appTitle")}
        </Link>
        <div className="top-actions">
          <LanguageSwitcher />
          <span className="role-chip">{user?.role ? t(`roles.${user.role}`) : ""}</span>
          <button type="button" onClick={() => void logout()}>
            {t("actions.logout")}
          </button>
        </div>
      </header>
      <div className="content-shell">
        <nav className="side-nav">
          {navItems
            .filter((item) => user && item.roles.includes(user.role))
            .map((item) => (
              <NavLink key={item.to} to={item.to} end={item.to === "/"}>
                {t(`nav.${item.key}`)}
              </NavLink>
            ))}
        </nav>
        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
