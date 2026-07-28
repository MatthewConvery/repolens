import {Outlet} from "react-router";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

export function AppShell() {
    return (
        <div className="app-shell">
            <Sidebar />

            <div className="app-shell__main">
                <Topbar />

                <main className="page-content">
                    <Outlet />
                </main>
            </div>
        </div>
    );
}