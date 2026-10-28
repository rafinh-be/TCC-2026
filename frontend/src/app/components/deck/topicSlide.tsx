import { SectionBlock } from "./sectionList";
import { SlideFrame } from "./slideFrame";
import type { topicSlideType } from "./slides";

const columnClassNames: Record<number, string> = { 2: "grid-cols-2", 3: "grid-cols-3" };

export function TopicSlide({ slide }: { slide: topicSlideType }) {
    return (
        <SlideFrame title={slide.title}>
            <div className={`grid h-full ${columnClassNames[slide.sections.length]} content-center gap-12 pb-16`}>
                {slide.sections.map((section) => (
                    <SectionBlock key={section.heading} section={section} size={slide.size} />
                ))}
            </div>
        </SlideFrame>
    );
}
