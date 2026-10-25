"use client";
import { useEffect } from "react";

import { HIGHLIGHT_CLASS_NAME, paragraphElementId } from "@/utils/rehypeParagraphMarks";

const SCROLL_START_DELAY_MS = 350;
const SCROLL_END_FALLBACK_MS = 1200;

export function ScrollToParagraph({ index }: { index: number }) {
    useEffect(() => {
        const target = document.getElementById(paragraphElementId(index));
        if (!target) return;

        const paragraphElements = document.querySelectorAll(`[data-trecho="${index}"]`);
        const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        let fallbackTimer: ReturnType<typeof setTimeout>;

        const highlight = () => {
            clearTimeout(fallbackTimer);
            document.removeEventListener("scrollend", highlight, true);
            paragraphElements.forEach((element) => element.classList.add(HIGHLIGHT_CLASS_NAME));
        };

        const startTimer = setTimeout(() => {
            document.addEventListener("scrollend", highlight, { capture: true, once: true });
            fallbackTimer = setTimeout(highlight, SCROLL_END_FALLBACK_MS);
            target.scrollIntoView({ block: "center", behavior: prefersReducedMotion ? "auto" : "smooth" });
        }, SCROLL_START_DELAY_MS);

        return () => {
            clearTimeout(startTimer);
            clearTimeout(fallbackTimer);
            document.removeEventListener("scrollend", highlight, true);
            paragraphElements.forEach((element) => element.classList.remove(HIGHLIGHT_CLASS_NAME));
        };
    }, [index]);

    return null;
}
