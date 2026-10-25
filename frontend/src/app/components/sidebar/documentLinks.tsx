"use client";
import { useEffect, useLayoutEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { documentSummaryType, useDocuments } from "@/hooks/useDocuments";

const MESSAGE_ENTER_MS = 350;
const SIDEBAR_OPEN_MS = 250;
const SLIDE_MS = 600;
const SLIDE_EASING = "cubic-bezier(0.2, 0.8, 0.2, 1)";
const DRAWER_ID = "app-drawer";
const DESKTOP_QUERY = "(min-width: 1024px)";

export function DocumentLinks({ citedDocumentIds = [] }: { citedDocumentIds?: string[] }) {
    const documents = useDocuments();
    const pathname = usePathname();
    const [isOpen, setIsOpen] = useState(false);
    const [shownCitedIds, setShownCitedIds] = useState<string[]>([]);
    const itemElements = useRef(new Map<string, HTMLLIElement>());
    const previousTops = useRef(new Map<string, number>());
    const shownCitedIdsRef = useRef<string[]>([]);

    const citedKey = citedDocumentIds.join("\n");

    useEffect(() => {
        const citedIds = citedKey ? citedKey.split("\n") : [];
        const hasNewCitation = citedIds.some((id) => !shownCitedIdsRef.current.includes(id));
        if (!hasNewCitation || documents.length === 0) return;

        const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        const wait = (milliseconds: number) => (reducedMotion ? 0 : milliseconds);
        let slideTimer: ReturnType<typeof setTimeout>;

        const openTimer = setTimeout(() => {
            const drawerToggle = document.getElementById(DRAWER_ID) as HTMLInputElement | null;
            if (drawerToggle && window.matchMedia(DESKTOP_QUERY).matches) drawerToggle.checked = true;
            setIsOpen(true);

            slideTimer = setTimeout(() => {
                previousTops.current = new Map(
                    Array.from(itemElements.current, ([id, element]) => [id, element.getBoundingClientRect().top]),
                );
                shownCitedIdsRef.current = citedIds;
                setShownCitedIds(citedIds);
            }, wait(SIDEBAR_OPEN_MS));
        }, wait(MESSAGE_ENTER_MS));

        return () => {
            clearTimeout(openTimer);
            clearTimeout(slideTimer);
        };
    }, [citedKey, documents]);

    useLayoutEffect(() => {
        if (previousTops.current.size === 0) return;
        const slideElements = Array.from(itemElements.current);
        slideElements.forEach(([id, element]) => {
            const previousTop = previousTops.current.get(id);
            if (previousTop === undefined) return;
            const distance = previousTop - element.getBoundingClientRect().top;
            if (distance === 0) return;
            element.style.zIndex = "1";
            const animation = element.animate(
                [{ transform: `translateY(${distance}px)` }, { transform: "translateY(0)" }],
                { duration: SLIDE_MS, easing: SLIDE_EASING },
            );
            animation.finished.then(() => { element.style.zIndex = ""; }).catch(() => {});
        });
        previousTops.current = new Map();
    }, [shownCitedIds]);

    if (documents.length === 0) return null;

    const citedDocuments = shownCitedIds
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
            <li
                key={document.id}
                ref={(element) => {
                    if (element) itemElements.current.set(document.id, element);
                    else itemElements.current.delete(document.id);
                }}
            >
                <Link
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    title={document.title}
                    className={`text-ink transition-colors duration-500 hover:bg-primary-soft ${stateClassName}`}
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
