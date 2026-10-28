import { SectionBlock } from "./sectionList";
import { SlideFrame } from "./slideFrame";
import type { topicSlideType } from "./slides";

export function TopicSlide({ slide }: { slide: topicSlideType }) {
    return (
        <SlideFrame title={slide.title}>
            <div className="grid h-full grid-cols-3 content-center gap-12 pb-16">
                {slide.sections.map((section) => (
                    <SectionBlock key={section.heading} section={section} />
                ))}
            </div>
        </SlideFrame>
    );
}
