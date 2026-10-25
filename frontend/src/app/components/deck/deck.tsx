"use client";
import { useEffect, useState, useSyncExternalStore } from "react";

import { actionForKey, advance, ignoresKey, slideFromHash, type deckPosition } from "@/utils/deckNavigation";
import { SlideView } from "./slideView";
import { slides, stepCounts } from "./slides";

function subscribeToHash(onChange: () => void) {
    window.addEventListener("hashchange", onChange);
    return () => window.removeEventListener("hashchange", onChange);
}

const readHash = () => window.location.hash;
const readServerHash = () => "";

export function Deck() {
    const hash = useSyncExternalStore(subscribeToHash, readHash, readServerHash);
    const slide = slideFromHash(hash, slides.length);
    const [stepState, setStepState] = useState<deckPosition>({ slide: 0, step: 0 });
    const step = stepState.slide === slide ? stepState.step : 0;

    useEffect(() => {
        const handleKeyDown = (event: KeyboardEvent) => {
            const action = actionForKey(event.key);
            if (!action || event.metaKey || event.ctrlKey || event.altKey || ignoresKey(event.key, event.target)) return;
            event.preventDefault();
            const next = advance({ slide, step }, action, stepCounts);
            setStepState(next);
            if (next.slide !== slide) {
                window.history.pushState(null, "", `#${next.slide + 1}`);
                window.dispatchEvent(new HashChangeEvent("hashchange"));
            }
        };
        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, [slide, step]);

    return (
        <div className="flex h-dvh flex-col bg-page">
            <div className="min-h-0 flex-1">
                <SlideView key={slides[slide].id} slide={slides[slide]} step={step} />
            </div>
            <div className="px-6 py-3 text-right text-sm text-ink-muted">{slide + 1} / {slides.length}</div>
        </div>
    );
}
