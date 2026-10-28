import { QRCodeSVG } from "qrcode.react";

import { SlideFrame } from "./slideFrame";
import type { siteSlideType } from "./slides";

export function SiteSlide({ slide }: { slide: siteSlideType }) {
    return (
        <SlideFrame title={slide.title}>
            <div className="flex h-full items-center justify-center gap-16 pb-16">
                <div className="rounded-2xl border border-line bg-surface p-6 text-ink">
                    <QRCodeSVG value={slide.url} size={288} fgColor="currentColor" bgColor="transparent" title={slide.url} />
                </div>
                <a href={slide.url} className="text-4xl font-medium text-primary underline-offset-8 hover:underline">{slide.url.replace("https://", "").replace(/\/$/, "")}</a>
            </div>
        </SlideFrame>
    );
}
