import { AlertTriangle, CheckCircle2, Info } from "lucide-react";
import type { BriefingItem } from "../../../data/mockRepository";

const briefingIcons = {
    success: CheckCircle2,
    warning: AlertTriangle,
    info: Info
};

type RepositoryBriefingProps = {
    summary: string;
    items: BriefingItem[];
}

export function RepositoryBriefing({
    summary,
    items,
}: RepositoryBriefingProps) {
    return (
        <section className="repository-briefing">
            <div className="repository-briefing__header">
                <div>
                    <p className="section-eyebrow">AI overview</p>
                    <h2 className="section-title">Repository Briefing</h2>
                </div>

                <span className="repository-briefing__status">
                    Mock Analysis
                </span>
            </div>

            <p className="repository-briefing__summary">
                {summary}
            </p>

            <ul className="repository-briefing__list">
                {items.map((item) => {
                    const Icon = briefingIcons[item.type];

                    return (
                        <li
                            key={item.text}
                            className={`repository-briefing__item repository-briefing__item--${item.type}`}
                        >
                            <Icon size={18} aria-hidden="true" />
                            <span>{item.text}</span>
                        </li>
                    );
                })}
            </ul>
        </section>
    )
}