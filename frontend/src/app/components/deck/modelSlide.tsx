"use client";
import { COMPARE_PROVIDERS, useCompareChat } from "@/hooks/useCompareChat";
import { ProviderPane } from "./providerPane";
import { SectionBlock } from "./sectionList";
import { SlideFrame } from "./slideFrame";
import type { modelSlideType } from "./slides";

export function ModelSlide({ slide }: { slide: modelSlideType }) {
    const { runs, isProcessing, sendMessage } = useCompareChat();

    return (
        <SlideFrame title={slide.title}>
            <div className="flex h-full flex-col gap-5 pb-2">
                <div className="grid shrink-0 grid-cols-3 gap-5">
                    {slide.sections.map((section) => (
                        <SectionBlock key={section.heading} section={section} size="compact" />
                    ))}
                </div>
                <div className="flex min-h-0 flex-1 flex-col gap-3">
                    <button
                        type="button"
                        disabled={isProcessing}
                        onClick={() => sendMessage(slide.prompt)}
                        className="self-start rounded-2xl border border-line bg-primary-soft px-4 py-2 text-left text-primary-ink hover:border-primary disabled:opacity-50"
                    >
                        {slide.prompt}
                    </button>
                    <div className="grid min-h-0 flex-1 grid-cols-2 divide-x divide-line overflow-hidden rounded-2xl border border-line">
                        {COMPARE_PROVIDERS.map((provider) => (
                            <ProviderPane key={provider} label={slide.panes[provider]} run={runs[provider]} />
                        ))}
                    </div>
                </div>
            </div>
        </SlideFrame>
    );
}
