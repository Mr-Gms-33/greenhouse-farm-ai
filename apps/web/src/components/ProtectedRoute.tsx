import { Navigate } from "react-router-dom";
import { useAuth } from "../auth";
import type { Role } from "../types";

type ProtectedRouteProps = {
  roles?: Role[];
  children: JSX.Element;
};

export function ProtectedRoute({ roles, children }: ProtectedRouteProps): JSX.Element {
  const { isAuthenticated, hasRole } = useAuth();

  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (roles && !hasRole(roles)) return <Navigate to="/" replace />;
  return children;
}
