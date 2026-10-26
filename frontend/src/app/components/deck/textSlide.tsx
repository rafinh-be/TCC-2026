import { PointCards } from "./pointCards";
import type { textSlideType } from "./slides";

export function TextSlide({ slide }: { slide: textSlideType }) {
    return (
        <div className="mx-auto flex h-full w-full max-w-4xl flex-col justify-center gap-10 px-10">
            <h2 className="text-4xl font-semibold tracking-tight text-ink">{slide.title}</h2>
            <PointCards points={slide.bullets} size="large" />
        </div>
    );
}
