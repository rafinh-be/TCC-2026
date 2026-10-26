import { RichText } from "./richText";
import type { pipelineSlideType } from "./slides";

export function PipelineSlide({ slide, step }: { slide: pipelineSlideType, step: number }) {
    return (
        <div className="mx-auto flex h-full w-full max-w-6xl flex-col justify-center gap-12 px-10">
            <h2 className="text-4xl font-semibold tracking-tight text-ink">{slide.title}</h2>
            <ol className="grid grid-cols-4 gap-4">
                {slide.stages.map((stage, index) => (
                    <li
                        key={stage.label}
                        className={`flex flex-col gap-2 rounded-2xl border px-5 py-6 transition ${index === step ? "border-primary bg-primary-soft text-primary-ink" : "border-line bg-surface text-ink-muted"}`}
                    >
                        <span className="text-sm font-medium">{index + 1}</span>
                        <span className="text-xl font-semibold">{stage.label}</span>
                        <span className="text-base"><RichText text={stage.detail} /></span>
                    </li>
                ))}
            </ol>
            {slide.note && <p className="text-lg text-ink-muted"><RichText text={slide.note} /></p>}
        </div>
    );
}
