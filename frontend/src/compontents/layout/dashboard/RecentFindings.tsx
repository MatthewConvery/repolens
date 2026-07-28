import { AlertCircle, AlertTriangle, CheckCircle2, Info } from "lucide-react";
export type FindingSeverity = | "critical" | "warning" | "success" | "info";

export type Finding = {
    id: number,
    file: string,
    message: string,
    severity: FindingSeverity;
};

type RecentFindingProps = {
    findings: Finding[];
};

const findingIcons = {
    critical: AlertCircle,
    warning: AlertTriangle,
    success: CheckCircle2,
    info: Info
};

export function RecentFindings({
    findings
}: RecentFindingProps) {
    return (
        <section className="recent-findings">
            <div className="recent-findings__header">
                <div>
                    <p className="section-eyebrow">Repository analysis</p>
                    <h2 className="section-title">Recent Findings</h2>
                </div>

                <span className="recent-findings__count">
                    {findings.length} findings
                </span>
            </div>

            <ul className="recent-findings__list">
                {findings.map((finding) => {
                    const Icon = findingIcons[finding.severity];

                    return (
                        <li
                            key={finding.id}
                            className={`finding finding--${finding.severity}`}
                        >
                            <div className="finding__icon">
                                <Icon size={18} aria-hidden="true" />
                            </div>

                            <div className="finding__content">
                                <p className="finding__file">
                                    {finding.file}
                                </p>

                                <p className="finding__message">
                                    {finding.message}
                                </p>
                            </div>

                            <span className="finding__severity">
                                {finding.severity}
                            </span>
                        </li>
                    );
                })}
            </ul>
        </section>
    );
}