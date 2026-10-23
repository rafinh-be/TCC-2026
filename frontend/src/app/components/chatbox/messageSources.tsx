import { sourceType } from "./chatbox";

export function MessageSources({ sources }: { sources: sourceType[] }) {
    if (sources.length === 0) return null;

    return (
        <div className="mt-3 flex flex-wrap items-center gap-2 text-sm text-ink-muted">
            <span>Fontes:</span>
            {sources.map((source) => (
                <span key={source.title} className="rounded-full border border-line bg-primary-soft px-3 py-1 text-primary-ink">
                    {source.title}
                </span>
            ))}
        </div>
    );
}
