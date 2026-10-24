"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { useDocuments } from "@/hooks/useDocuments";

export function DocumentLinks() {
    const documents = useDocuments();
    const pathname = usePathname();

    if (documents.length === 0) return null;

    return (
        <>
            <li className="menu-title mt-3 is-drawer-close:hidden">Documentos</li>
            {documents.map((document) => {
                const href = `/documentos/${encodeURIComponent(document.id)}`;
                return (
                    <li key={document.id} className="is-drawer-close:hidden">
                        <Link
                            href={href}
                            className={`text-ink hover:bg-primary-soft ${pathname === href ? "bg-primary-soft text-primary-ink" : ""}`}
                        >
                            <span className="line-clamp-2">{document.title}</span>
                        </Link>
                    </li>
                );
            })}
        </>
    );
}
