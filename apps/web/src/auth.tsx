import { createContext, useContext, useMemo, useState } from "react";
import { request } from "./api";
import type { Role, User } from "./types";

type AuthContextValue = {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  hasRole: (roles: Role[]) => boolean;
};

const TOKEN_KEY = "gh_token";
const USER_KEY = "gh_user";

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }): JSX.Element {
  const [token, setToken] = useState<string | null>(localStorage.getItem(TOKEN_KEY));
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem(USER_KEY);
    return saved ? (JSON.parse(saved) as User) : null;
  });

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      user,
      isAuthenticated: Boolean(token && user),
      async login(email, password) {
        const result = await request<{ access_token: string; user: User }>("/auth/login", {
          method: "POST",
          body: JSON.stringify({ email, password })
        });
        setToken(result.access_token);
        setUser(result.user);
        localStorage.setItem(TOKEN_KEY, result.access_token);
        localStorage.setItem(USER_KEY, JSON.stringify(result.user));
      },
      async logout() {
        if (token) {
          try {
            await request("/auth/logout", { method: "POST" }, token);
          } catch {
            // Best-effort logout; local session is always cleared.
          }
        }
        setToken(null);
        setUser(null);
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
      },
      hasRole(roles) {
        return user ? roles.includes(user.role) : false;
      }
    }),
    [token, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
