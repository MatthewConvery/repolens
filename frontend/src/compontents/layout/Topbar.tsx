import {Bell, ChevronDown, GitBranch, Search} from "lucide-react";

export function Topbar() {
    return (
        <header className="topbar">
            <button className="repository-selector" type="button">
                <span className="repository-selector__label">Repository</span>
                <strong>repolens</strong>
                <ChevronDown size={16} />
            </button>

            <div className="topbar__branch">
                <GitBranch size={16} />
                <span>main</span>
            </div>

            <label className="topbar__search">
                <Search size={18} aria-hidden="true" />
                <input
                    type="search"
                    placeholder="Search repository..."
                    aria-label="Search repository"
                />
            </label>

            <div className="topbar__actions">
                <button
                    className="icon-button"
                    type="button"
                    aria-label="Notifications"
                >
                    <Bell size={19} />
                </button>

                <button className="user-avatar" type ="button" aria-label="Open profile">
                    RL
                </button>
            </div>
        </header>
    )
}