import { RichText } from "./richText";
import type { siteSectionType } from "./slides";

export function SectionBlock({ section }: { section: siteSectionType }) {
    return (
        <section className="flex flex-col gap-3">
            <h3 className="text-3xl font-bold text-primary">{section.heading}</h3>
            <ul className="flex list-disc flex-col gap-2 pl-7 text-2xl text-ink-muted marker:text-primary">
                {section.bullets.map((bullet) => (
                    <li key={bullet}><RichText text={bullet} /></li>
                ))}
            </ul>
        </section>
    );
}

export function SectionList({ sections }: { sections: siteSectionType[] }) {
    return (
        <div className="flex flex-col gap-10">
            {sections.map((section) => (
                <SectionBlock key={section.heading} section={section} />
            ))}
        </div>
    );
}
