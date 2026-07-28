type PlaceholderPageProps = {
    title: string;
};

export function PlaceholderPage({title}: PlaceholderPageProps) {
    return (
        <section>
            <p className="page-eyebrow">RepoLens workspace</p>
            <h1 className="page-title">{title}</h1>
            <p className="page-description">This page will be built in a later ticket.</p>
        </section>
    );
}