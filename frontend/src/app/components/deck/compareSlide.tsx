import { PointCards } from "./pointCards";
import { RichText } from "./richText";
import type { compareSideType, compareSlideType } from "./slides";

function CompareSide({ side, highlighted }: { side: compareSideType, highlighted: boolean }) {
    return (
        <section className={`flex flex-col gap-4 rounded-2xl border p-6 ${highlighted ? "border-primary" : "border-line"}`}>
            <h3 className={`text-xl font-semibold ${highlighted ? "text-primary-ink" : "text-ink-muted"}`}>{side.label}</h3>
            <PointCards points={side.points} size="compact" />
        </section>
    );
}

export function CompareSlide({ slide }: { slide: compareSlideType }) {
    return (
        <div className="mx-auto flex h-full w-full max-w-6xl flex-col justify-center gap-8 px-10">
            <h2 className="text-4xl font-semibold tracking-tight text-ink">{slide.title}</h2>
            <div className="grid grid-cols-2 gap-6">
                <CompareSide side={slide.before} highlighted={false} />
                <CompareSide side={slide.after} highlighted />
            </div>
            <p className="text-base text-ink-muted"><RichText text={slide.note} /></p>
        </div>
    );
}
