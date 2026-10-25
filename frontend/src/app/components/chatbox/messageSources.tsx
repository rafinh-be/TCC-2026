"use client";
import Link from "next/link";

import { useDocuments } from "@/hooks/useDocuments";
import { sourceType } from "./chatbox";
import { useDocumentOpener } from "./documentOpener";

const chipClassName = "rounded-full border border-line bg-primary-soft px-3 py-1 text-primary-ink";

export function MessageSources({ sources }: { sources: sourceType[] }) {
    const documents = useDocuments();
    const openDocument = useDocumentOpener();

    if (sources.length === 0) return null;

    return (
        <div className="mt-3 flex flex-wrap items-center gap-2 text-sm text-ink-muted">
            <span>Fontes:</span>
            {sources.map((source) => {
                const document = documents.find((candidate) => candidate.title === source.title);
                if (!document) {
                    return <span key={source.title} className={chipClassName}>{source.title}</span>;
                }
                return (
                    <Link
                        key={source.title}
                        href={`/documentos/${encodeURIComponent(document.id)}`}
                        onClick={(event) => {
                            if (!openDocument) return;
                            event.preventDefault();
                            openDocument({ id: document.id, paragraph: null });
                        }}
                        className={`${chipClassName} hover:border-primary`}
                    >
                        {source.title}
                    </Link>
                );
            })}
        </div>
    );
}
