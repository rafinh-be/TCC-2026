import { SlideFrame } from "./slideFrame";
import type { listSlideType } from "./slides";

export function ListSlide({ slide }: { slide: listSlideType }) {
    return (
        <SlideFrame title={slide.title}>
            <div className="flex h-full items-center pb-16">
                <ol className="flex w-full flex-col divide-y divide-line border-y border-line">
                    {slide.items.map((item, index) => (
                        <li key={item.heading} className="flex items-baseline gap-8 py-9">
                            <span className="w-14 shrink-0 text-4xl font-light tabular-nums text-primary">{String(index + 1).padStart(2, "0")}</span>
                            <div className="flex flex-col gap-1">
                                <span className="text-4xl font-semibold text-ink">{item.heading}</span>
                                <span className="text-3xl text-ink-muted">{item.text}</span>
                            </div>
                        </li>
                    ))}
                </ol>
            </div>
        </SlideFrame>
    );
}
