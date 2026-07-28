import {
    Bot,
    Boxes,
    FlaskConical,
    LayoutDashboard,
    Search,
    Settings,
    ShieldCheck,
    Telescope
} from "lucide-react";
import {NavLink, type NavLinkRenderProps} from "react-router";

const navigationItems = [
    {
        label: "Dashboard",
        path: "/",
        icon: LayoutDashboard
    },
    {
        label: "Explorer",
        path: "/explorer",
        icon: Telescope
    },
    {
        label: "Testing",
        path: "/testing",
        icon: FlaskConical
    },
    {
        label: "Review",
        path: "/review",
        icon: ShieldCheck
    },
    {
        label: "Architecture",
        path: "/architecture",
        icon: Boxes
    },
    {
        label: "AI Search",
        path: "/search",
        icon: Search
    }
];

export function Sidebar() {
    return (
        <aside className="sidebar">
            <div className="sidebar__brand">
                <Bot size={24} />
                <span>RepoLens</span>
            </div>

            <nav className="sidebar__navigation" aria-label="Main navigation">
                {navigationItems.map(({label, path, icon: Icon}) => (
                    <NavLink
                        key={path}
                        to={path}
                        end={path === "/"}
                        className={({isActive}: NavLinkRenderProps) => `sidebar__link ${isActive ? "sidebar__link--active" : ""}`
                        }
                >
                    <Icon size={19} />
                    <span>{label}</span>
                </NavLink>))}
            </nav>

            <NavLink
                to="/settings"
                className={({isActive}: NavLinkRenderProps) => `sidebar__link sidebar__settings ${isActive ? "sidebar__link--active" : ""}`
                }
            >
                <Settings size={19} />
                <span>Settings</span>
            </NavLink>
        </aside>
    );
}