import { RichText } from "./richText";
import type { siteSectionType } from "./slides";

const blockClassNames = {
    regular: {
        card: "gap-[calc(1rem*min(1,100vh/900px))] p-[calc(2rem*min(1,100vh/900px))]",
        heading: "text-[calc(1.875rem*min(1,100vh/900px))]",
        bullets: "gap-[calc(0.5rem*min(1,100vh/900px))] text-[calc(1.5rem*min(1,100vh/900px))]",
    },
    dense: {
        card: "gap-[calc(1rem*min(1,100vh/1080px))] p-[calc(2rem*min(1,100vh/1080px))]",
        heading: "text-[calc(1.875rem*min(1,100vh/1080px))]",
        bullets: "gap-[calc(0.5rem*min(1,100vh/1080px))] text-[calc(1.5rem*min(1,100vh/1080px))]",
    },
    compact: {
        card: "gap-[calc(0.5rem*min(1,100vh/900px))] p-[calc(1.25rem*min(1,100vh/900px))]",
        heading: "text-[calc(1.5rem*min(1,100vh/900px))]",
        bullets: "gap-[calc(0.25rem*min(1,100vh/900px))] text-[calc(1.125rem*min(1,100vh/900px))]",
    },
};

export function SectionBlock({ section, size = "regular" }: { section: siteSectionType, size?: keyof typeof blockClassNames }) {
    const classNames = blockClassNames[size];

    return (
        <section className={`flex flex-col rounded-2xl border border-line bg-surface ${classNames.card}`}>
            <h3 className={`font-bold leading-tight text-primary ${classNames.heading}`}>{section.heading}</h3>
            <ul className={`flex list-disc flex-col pl-7 leading-snug text-ink-muted marker:text-primary ${classNames.bullets}`}>
                {section.bullets.map((bullet) => (
                    <li key={bullet}><RichText text={bullet} /></li>
                ))}
            </ul>
        </section>
    );
}

export function SectionList({ sections }: { sections: siteSectionType[] }) {
    return (
        <div className="flex flex-col gap-[calc(1.25rem*min(1,100vh/900px))]">
            {sections.map((section) => (
                <SectionBlock key={section.heading} section={section} />
            ))}
        </div>
    );
}
