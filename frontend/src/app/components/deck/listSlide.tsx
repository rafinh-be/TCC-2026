import { SlideFrame } from "./slideFrame";
import type { listSlideType } from "./slides";

export function ListSlide({ slide }: { slide: listSlideType }) {
    return (
        <SlideFrame title={slide.title}>
            <div className="flex h-full items-center pb-16">
                <ol className="flex w-full list-decimal flex-col gap-4 pl-10 text-3xl text-ink marker:font-semibold marker:text-primary">
                    {slide.items.map((item) => (
                        <li key={item} className="pl-3">{item}</li>
                    ))}
                </ol>
            </div>
        </SlideFrame>
    );
}
