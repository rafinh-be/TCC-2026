import { referenceNumbering } from "./referenceNumbering";
import { references } from "./references";
import { SlideFrame } from "./slideFrame";
import type { sourcesSlideType } from "./slides";

export function SourcesSlide({ slide }: { slide: sourcesSlideType }) {
    const entries = [...referenceNumbering.entries()].sort((first, second) => first[1] - second[1]);

    return (
        <SlideFrame title={slide.title}>
            <div className="flex h-full items-center pb-8">
                <ol className="columns-2 gap-12">
                    {entries.map(([id, number]) => (
                        <li key={id} className="mb-5 flex break-inside-avoid gap-3 text-xl text-ink-muted">
                            <span className="font-medium text-primary">[{number}]</span>
                            <span className="flex flex-col gap-1">
                                <span>{references[id].citation}</span>
                                <a href={references[id].url} target="_blank" rel="noreferrer" className="break-all text-base text-primary hover:underline">
                                    {references[id].url}
                                </a>
                            </span>
                        </li>
                    ))}
                </ol>
            </div>
        </SlideFrame>
    );
}
