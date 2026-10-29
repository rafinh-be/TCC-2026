import { QRCodeSVG } from "qrcode.react";

import { SectionList } from "./sectionList";
import { SlideFrame } from "./slideFrame";
import type { siteSlideType } from "./slides";

export function SiteSlide({ slide }: { slide: siteSlideType }) {
    return (
        <SlideFrame title={slide.title}>
            <div className="grid h-full grid-cols-[minmax(0,3fr)_minmax(0,2fr)] items-center gap-20 pb-16">
                <SectionList sections={slide.sections} />
                <div className="flex flex-col items-center gap-6">
                    <p className="text-3xl font-semibold text-ink">Acesse o protótipo</p>
                    <div className="rounded-2xl border border-line bg-surface p-6 text-ink">
                        <QRCodeSVG value={slide.url} size={288} fgColor="currentColor" bgColor="transparent" title={slide.url} />
                    </div>
                    <a href={slide.url} className="text-2xl font-medium text-primary underline-offset-8 hover:underline">{slide.url.replace("https://", "").replace(/\/$/, "")}</a>
                </div>
            </div>
        </SlideFrame>
    );
}
