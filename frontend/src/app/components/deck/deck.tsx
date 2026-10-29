"use client";
import { useEffect, useState, useSyncExternalStore } from "react";

import { actionForKey, advance, ignoresKey, slideFromHash, type deckPosition } from "@/utils/deckNavigation";
import { ReferencesFooter } from "./referencesFooter";
import { SlideView } from "./slideView";
import { slides, stepCounts } from "./slides";

function subscribeToHash(onChange: () => void) {
    window.addEventListener("hashchange", onChange);
    return () => window.removeEventListener("hashchange", onChange);
}

const readHash = () => window.location.hash;
const readServerHash = () => "";
const subscribeToResize = (onChange: () => void) => {
    window.addEventListener("resize", onChange);
    return () => window.removeEventListener("resize", onChange);
};
const readScale = () => Math.min(window.innerWidth / 1920, window.innerHeight / 1080);
const readServerScale = () => 1;
const subscribeToFullscreen = (onChange: () => void) => {
    document.addEventListener("fullscreenchange", onChange);
    return () => document.removeEventListener("fullscreenchange", onChange);
};
const readFullscreen = () => Boolean(document.fullscreenElement);
const readServerFullscreen = () => false;

export function Deck() {
    const hash = useSyncExternalStore(subscribeToHash, readHash, readServerHash);
    const scale = useSyncExternalStore(subscribeToResize, readScale, readServerScale);
    const fullscreen = useSyncExternalStore(subscribeToFullscreen, readFullscreen, readServerFullscreen);
    const [fullscreenError, setFullscreenError] = useState(false);
    const slide = slideFromHash(hash, slides.length);
    const [stepState, setStepState] = useState<deckPosition>({ slide: 0, step: 0 });
    const step = stepState.slide === slide ? stepState.step : 0;
    const currentRefs = slides[slide].refs;

    async function toggleFullscreen() {
        try {
            if (document.fullscreenElement) await document.exitFullscreen();
            else await document.documentElement.requestFullscreen();
            setFullscreenError(false);
        } catch {
            setFullscreenError(true);
        }
    }

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
        <div className="flex h-dvh w-full items-center justify-center overflow-hidden bg-page">
            <div style={{ width: 1920 * scale, height: 1080 * scale }}>
                <div className="flex flex-col bg-page" style={{ width: 1920, height: 1080, transform: `scale(${scale})`, transformOrigin: "top left" }}>
                    <div className="min-h-0 flex-1">
                        <SlideView key={slides[slide].id} slide={slides[slide]} step={step} />
                    </div>
                    <div className="flex items-end justify-between gap-6 px-6 py-3">
                        <div className="min-w-0">{currentRefs && <ReferencesFooter ids={currentRefs} />}</div>
                        <div className="flex shrink-0 items-center gap-4 text-sm text-ink-muted">
                            {fullscreenError && <span role="status">Tela cheia indisponível neste navegador.</span>}
                            <button type="button" onClick={toggleFullscreen} className="rounded border border-line px-3 py-1 hover:bg-primary-soft">
                                {fullscreen ? "Sair da tela cheia" : "Tela cheia"}
                            </button>
                            <span>{slide + 1} / {slides.length}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
