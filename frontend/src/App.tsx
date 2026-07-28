import { Route, Routes } from "react-router";
import { AppShell } from "./compontents/layout/AppShell";
import { DashboardPage } from "./pages/DashboardPage";
import { PlaceholderPage } from "./pages/PlaceholderPage";

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />} >
        <Route index element={<DashboardPage />} />
        <Route
          path="explorer"
          element={<PlaceholderPage title="Explorer" />}
        />
        <Route
          path="testing"
          element={<PlaceholderPage title="Testing" />}
        />
        <Route
          path="review"
          element={<PlaceholderPage title="Review" />}
        />
        <Route
          path="architecture"
          element={<PlaceholderPage title="Architecture" />}
        />
        <Route
          path="search"
          element={<PlaceholderPage title="AI Search" />}
        />
        <Route
          path="settings"     
          element={<PlaceholderPage title="Settings" />}
        />
      </Route>
    </Routes>
  )
}