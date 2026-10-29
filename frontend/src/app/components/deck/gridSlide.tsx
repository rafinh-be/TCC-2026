import { RichText } from "./richText";
import { SlideFrame } from "./slideFrame";
import type { gridSlideType } from "./slides";

export function GridSlide({ slide }: { slide: gridSlideType }) {
    return (
        <SlideFrame title={slide.title}>
            <div className="flex h-full items-center pb-16">
                <ul className="grid w-full grid-cols-2 gap-5">
                    {slide.items.map((item) => (
                        <li key={item.heading} className="flex min-h-60 flex-col gap-3 rounded-2xl border border-line bg-surface p-8">
                            <h3 className="text-4xl font-bold text-primary">{item.heading}</h3>
                            <p className="text-3xl text-ink-muted"><RichText text={item.text} /></p>
                        </li>
                    ))}
                </ul>
            </div>
        </SlideFrame>
    );
}
