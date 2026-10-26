import type { titleSlideType } from "./slides";

export function TitleSlide({ slide }: { slide: titleSlideType }) {
    return (
        <div className="mx-auto flex h-full w-full max-w-4xl flex-col justify-center gap-8 px-10">
            <p className="text-sm font-medium uppercase tracking-wide text-primary">{slide.kicker}</p>
            <h1 className="text-5xl font-semibold leading-tight tracking-tight text-ink">{slide.title}</h1>
            <div className="flex flex-col gap-2 border-t border-line pt-6">
                <p className="text-xl text-ink">{slide.authors}</p>
                <p className="text-base text-ink-muted">{slide.institution}</p>
            </div>
        </div>
    );
}
