import { RichText } from "./richText";
import { SlideFrame } from "./slideFrame";
import type { conceptsSlideType } from "./slides";

export function ConceptsSlide({ slide, step }: { slide: conceptsSlideType, step: number }) {
    return (
        <SlideFrame title={slide.title}>
            <ol className="flex flex-col">
                {slide.items.map((item, index) => {
                    const visible = index <= step;
                    const expanded = index === step;
                    return (
                        <li
                            key={item.heading}
                            inert={!visible}
                            className={`grid transition-[grid-template-rows,opacity] duration-500 ease-out motion-reduce:transition-none ${visible ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"}`}
                        >
                            <div className="min-h-0 overflow-hidden">
                                <div className="pb-4">
                                    <div className={`rounded-2xl border bg-surface px-8 py-5 transition-colors duration-500 motion-reduce:transition-none ${expanded ? "border-primary" : "border-line"}`}>
                                        <h3 className={`font-bold text-primary transition-[font-size] duration-500 motion-reduce:transition-none ${expanded ? "text-3xl" : "text-2xl"}`}>{item.heading}</h3>
                                        <div className={`grid transition-[grid-template-rows,opacity] duration-500 ease-out motion-reduce:transition-none ${expanded ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"}`}>
                                            <p className="min-h-0 overflow-hidden pt-3 text-2xl leading-relaxed text-ink-muted"><RichText text={item.text} /></p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </li>
                    );
                })}
            </ol>
        </SlideFrame>
    );
}
