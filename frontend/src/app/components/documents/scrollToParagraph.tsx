"use client";
import { useEffect } from "react";

import { HIGHLIGHT_ANIMATION } from "@/config/highlight";
import { fadeHighlight, markerHighlight } from "@/utils/highlightAnimations";
import { paragraphElementId } from "@/utils/rehypeParagraphMarks";

const SCROLL_START_DELAY_MS = 350;
const SCROLL_END_FALLBACK_MS = 1200;

export function ScrollToParagraph({ index }: { index: number }) {
    useEffect(() => {
        const target = document.getElementById(paragraphElementId(index));
        const container = target?.closest<HTMLElement>("article");
        if (!target || !container) return;

        const paragraphElements = Array.from(document.querySelectorAll(`[data-trecho="${index}"]`));
        const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        const useMarker = HIGHLIGHT_ANIMATION === "marker" && !prefersReducedMotion;
        let fallbackTimer: ReturnType<typeof setTimeout>;
        let removeHighlight = () => {};

        const applyHighlight = (animate: boolean) => {
            removeHighlight();
            removeHighlight = useMarker
                ? markerHighlight(paragraphElements, container, index, animate)
                : fadeHighlight(paragraphElements);
        };

        const highlight = () => {
            clearTimeout(fallbackTimer);
            document.removeEventListener("scrollend", highlight, true);
            applyHighlight(true);
            if (useMarker) window.addEventListener("resize", redrawMarker);
        };

        const redrawMarker = () => applyHighlight(false);

        const startTimer = setTimeout(() => {
            document.addEventListener("scrollend", highlight, { capture: true, once: true });
            fallbackTimer = setTimeout(highlight, SCROLL_END_FALLBACK_MS);
            target.scrollIntoView({ block: "center", behavior: prefersReducedMotion ? "auto" : "smooth" });
        }, SCROLL_START_DELAY_MS);

        return () => {
            clearTimeout(startTimer);
            clearTimeout(fallbackTimer);
            document.removeEventListener("scrollend", highlight, true);
            window.removeEventListener("resize", redrawMarker);
            removeHighlight();
        };
    }, [index]);

    return null;
}
