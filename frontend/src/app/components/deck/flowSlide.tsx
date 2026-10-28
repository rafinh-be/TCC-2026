import { RichText } from "./richText";
import { SlideFrame } from "./slideFrame";
import type { flowSlideType } from "./slides";

const COLUMNS = 4;

function Arrow({ direction, active }: { direction: "right" | "left" | "down", active: boolean }) {
    const placement = {
        right: "right-[-2.75rem] top-1/2 -translate-y-1/2",
        left: "left-[-2.75rem] top-1/2 -translate-y-1/2 rotate-180",
        down: "bottom-[-2rem] left-1/2 -translate-x-1/2 rotate-90",
    }[direction];

    return (
        <svg viewBox="0 0 40 16" className={`absolute h-4 w-10 transition-colors ${placement} ${active ? "text-primary" : "text-line"}`} aria-hidden>
            <path d="M0 8H36M30 2l6 6-6 6" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    );
}

function position(index: number) {
    const row = Math.floor(index / COLUMNS);
    const offset = index % COLUMNS;
    return { row, column: row % 2 === 0 ? offset : COLUMNS - 1 - offset };
}

function arrowDirection(index: number, total: number) {
    if (index === total - 1) return null;
    if ((index + 1) % COLUMNS === 0) return "down";
    return Math.floor(index / COLUMNS) % 2 === 0 ? "right" : "left";
}

export function FlowSlide({ slide, step }: { slide: flowSlideType, step: number }) {
    return (
        <SlideFrame title={slide.title}>
            <div className="grid h-full content-center gap-x-12 gap-y-12 pb-8" style={{ gridTemplateColumns: `repeat(${COLUMNS}, minmax(0, 1fr))` }}>
                {slide.steps.map((flowStep, index) => {
                    const { row, column } = position(index);
                    const direction = arrowDirection(index, slide.steps.length);
                    const current = index === step;
                    const reached = index <= step;
                    return (
                        <div
                            key={flowStep.label}
                            style={{ gridRow: row + 1, gridColumn: column + 1 }}
                            className={`relative flex flex-col gap-[calc(0.5rem*min(1,100vh/900px))] rounded-2xl border p-[calc(1.5rem*min(1,100vh/900px))] transition ${current ? "border-primary bg-primary-soft" : "border-line bg-surface"} ${reached ? "opacity-100" : "opacity-40"}`}
                        >
                            <div className="flex items-center justify-between gap-3">
                                <span className="text-[calc(1rem*min(1,100vh/900px))] font-medium tabular-nums text-primary">{String(index + 1).padStart(2, "0")}</span>
                                <span className="rounded-full border border-line bg-page px-3 py-0.5 text-[calc(0.875rem*min(1,100vh/900px))] text-ink-muted">{flowStep.lane}</span>
                            </div>
                            <h3 className="text-[calc(1.5rem*min(1,100vh/900px))] font-bold leading-tight text-ink">{flowStep.label}</h3>
                            <p className="text-[calc(1.125rem*min(1,100vh/900px))] leading-snug text-ink-muted"><RichText text={flowStep.detail} /></p>
                            {direction && <Arrow direction={direction} active={index < step} />}
                        </div>
                    );
                })}
            </div>
        </SlideFrame>
    );
}
