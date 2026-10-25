"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { useDocuments } from "@/hooks/useDocuments";

export function DocumentLinks() {
    const documents = useDocuments();
    const pathname = usePathname();

    if (documents.length === 0) return null;

    return (
        <li className="is-drawer-close:hidden">
            <details>
                <summary className="text-ink hover:bg-primary-soft">Documentos</summary>
                <ul>
                    {documents.map((document) => {
                        const href = `/documentos/${encodeURIComponent(document.id)}`;
                        return (
                            <li key={document.id}>
                                <Link
                                    href={href}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    title={document.title}
                                    className={`text-ink hover:bg-primary-soft ${pathname === href ? "bg-primary-soft text-primary-ink" : ""}`}
                                >
                                    <span className="truncate">{document.title}</span>
                                </Link>
                            </li>
                        );
                    })}
                </ul>
            </details>
        </li>
    );
}
