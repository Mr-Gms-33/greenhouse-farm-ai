import { Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { LoginPage } from "./pages/LoginPage";
import { DashboardPage } from "./pages/DashboardPage";
import { GreenhousesPage } from "./pages/GreenhousesPage";
import { CropCyclesPage } from "./pages/CropCyclesPage";
import { HarvestsPage } from "./pages/HarvestsPage";
import { CustomersPage } from "./pages/CustomersPage";
import { SalesPage } from "./pages/SalesPage";
import { ExpensesPage } from "./pages/ExpensesPage";
import { ReportsPage } from "./pages/ReportsPage";
import { AnalysisPage } from "./pages/AnalysisPage";

export default function App(): JSX.Element {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="greenhouses" element={<GreenhousesPage />} />
        <Route path="crop-cycles" element={<CropCyclesPage />} />
        <Route path="harvests" element={<HarvestsPage />} />
        <Route
          path="customers"
          element={
            <ProtectedRoute roles={["owner", "accountant"]}>
              <CustomersPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="sales"
          element={
            <ProtectedRoute roles={["owner", "accountant"]}>
              <SalesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="expenses"
          element={
            <ProtectedRoute roles={["owner", "accountant"]}>
              <ExpensesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="reports"
          element={
            <ProtectedRoute roles={["owner", "accountant"]}>
              <ReportsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="analysis"
          element={
            <ProtectedRoute roles={["owner", "accountant"]}>
              <AnalysisPage />
            </ProtectedRoute>
          }
        />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
