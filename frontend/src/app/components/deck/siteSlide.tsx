import { QRCodeSVG } from "qrcode.react";

import { SlideFrame } from "./slideFrame";
import type { siteSlideType } from "./slides";

export function SiteSlide({ slide }: { slide: siteSlideType }) {
    return (
        <SlideFrame title={slide.title}>
            <div className="grid h-full grid-cols-[minmax(0,3fr)_minmax(0,2fr)] items-center gap-20 pb-16">
                <div className="flex flex-col gap-10">
                    {slide.sections.map((section) => (
                        <section key={section.heading} className="flex flex-col gap-3">
                            <h3 className="text-3xl font-bold text-primary">{section.heading}</h3>
                            <ul className="flex list-disc flex-col gap-2 pl-7 text-2xl text-ink-muted marker:text-primary">
                                {section.bullets.map((bullet) => (
                                    <li key={bullet}>{bullet}</li>
                                ))}
                            </ul>
                        </section>
                    ))}
                </div>
                <div className="flex flex-col items-center gap-6">
                    <div className="rounded-2xl border border-line bg-surface p-6 text-ink">
                        <QRCodeSVG value={slide.url} size={288} fgColor="currentColor" bgColor="transparent" title={slide.url} />
                    </div>
                    <a href={slide.url} className="text-2xl font-medium text-primary underline-offset-8 hover:underline">{slide.url.replace("https://", "").replace(/\/$/, "")}</a>
                </div>
            </div>
        </SlideFrame>
    );
}
