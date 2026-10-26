import { referenceNumbering } from "./referenceNumbering";
import { references } from "./references";
import type { sourcesSlideType } from "./slides";

export function SourcesSlide({ slide }: { slide: sourcesSlideType }) {
    const entries = [...referenceNumbering.entries()].sort((first, second) => first[1] - second[1]);

    return (
        <div className="mx-auto flex h-full w-full max-w-6xl flex-col justify-center gap-8 px-10">
            <h2 className="text-4xl font-semibold tracking-tight text-ink">{slide.title}</h2>
            <ol className="columns-2 gap-10">
                {entries.map(([id, number]) => (
                    <li key={id} className="mb-5 flex break-inside-avoid gap-3 text-base text-ink-muted">
                        <span className="font-medium text-primary">[{number}]</span>
                        <span className="flex flex-col gap-1">
                            <span>{references[id].citation}</span>
                            <a href={references[id].url} target="_blank" rel="noreferrer" className="break-all text-sm text-primary hover:underline">
                                {references[id].url}
                            </a>
                        </span>
                    </li>
                ))}
            </ol>
        </div>
    );
}
