"use client";
import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { documentSummaryType, useDocuments } from "@/hooks/useDocuments";

export function DocumentLinks({ citedDocumentIds = [] }: { citedDocumentIds?: string[] }) {
    const documents = useDocuments();
    const pathname = usePathname();
    const [isOpen, setIsOpen] = useState(false);
    const [hadCitations, setHadCitations] = useState(false);

    const hasCitations = citedDocumentIds.length > 0;
    if (hasCitations !== hadCitations) {
        setHadCitations(hasCitations);
        if (hasCitations) setIsOpen(true);
    }

    if (documents.length === 0) return null;

    const citedDocuments = citedDocumentIds
        .map((id) => documents.find((document) => document.id === id))
        .filter((document): document is documentSummaryType => document !== undefined);
    const otherDocuments = documents.filter((document) => !citedDocuments.includes(document));

    const renderLink = (document: documentSummaryType, isCited: boolean) => {
        const href = `/documentos/${encodeURIComponent(document.id)}`;
        const stateClassName = isCited
            ? "border-l-2 border-primary bg-primary-soft text-primary-ink"
            : pathname === href
                ? "bg-primary-soft text-primary-ink"
                : "";
        return (
            <li key={document.id}>
                <Link
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    title={document.title}
                    className={`text-ink hover:bg-primary-soft ${stateClassName}`}
                >
                    <span className="truncate">{document.title}</span>
                </Link>
            </li>
        );
    };

    return (
        <li className="is-drawer-close:hidden">
            <details open={isOpen} onToggle={(event) => setIsOpen(event.currentTarget.open)}>
                <summary className="text-ink hover:bg-primary-soft">Documentos</summary>
                <ul>
                    {citedDocuments.map((document) => renderLink(document, true))}
                    {otherDocuments.map((document) => renderLink(document, false))}
                </ul>
            </details>
        </li>
    );
}
