type StatCardProps = {
    label: string,
    value: string,
    description?: string;
};

export function StatCard({
    label,
    value,
    description,
}: StatCardProps) {
    return (
        <article className="stat-card">
            <p className="stat-card__label">{label}</p>
            <strong className="stat-card__value">{value}</strong>

            {description && (<p className="stat-card__description">{description}</p>)}
        </article>
    );
}