import type { closingSlideType } from "./slides";

export function ClosingSlide({ slide }: { slide: closingSlideType }) {
    return (
        <div className="mx-auto flex h-full w-full max-w-4xl flex-col justify-center gap-8 px-10">
            <h1 className="text-6xl font-semibold tracking-tight text-ink">{slide.title}</h1>
            <p className="border-t border-line pt-6 text-xl text-ink">{slide.authors}</p>
        </div>
    );
}
