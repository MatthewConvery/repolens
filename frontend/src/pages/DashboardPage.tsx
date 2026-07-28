import { RepositoryBriefing } from "../compontents/layout/dashboard/RepositoryBriefing";
import { StatCard } from "../compontents/layout/dashboard/StatCard";
import { RecentFindings } from "../compontents/layout/dashboard/RecentFindings";
import { repositoryStats, repositoryBriefing, recentFindings } from "../data/mockRepository";

export function DashboardPage() {
    return (
        <section>
            <p className="page-eyebrow">Repository overview</p>
            <h1 className="page-title">Dashboard</h1>
            <p className="page-description">
                Understand the repository before making changes.
            </p>

            <div className="stat-grid">
                {repositoryStats.map((stat) => (
                    <StatCard
                        key={stat.label}
                        label={stat.label}
                        value={stat.value}
                        description={stat.description}
                    />
                ))}
            </div>

            <RepositoryBriefing
                summary={repositoryBriefing.summary}
                items={repositoryBriefing.items}
            />

            <RecentFindings 
                findings={recentFindings} 
            />
        </section>
    );
}