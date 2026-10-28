import { SlideFrame } from "./slideFrame";
import type { listSlideType } from "./slides";

export function ListSlide({ slide }: { slide: listSlideType }) {
    return (
        <SlideFrame title={slide.title}>
            <div className="flex h-full items-center pb-16">
                <ul className="flex w-full flex-col gap-3">
                    {slide.items.map((item) => (
                        <li key={item} className="rounded-2xl border border-line bg-surface px-8 py-4 text-2xl text-ink">{item}</li>
                    ))}
                </ul>
            </div>
        </SlideFrame>
    );
}
