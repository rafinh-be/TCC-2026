"use client";
import { COMPARE_PROVIDERS, useCompareChat } from "@/hooks/useCompareChat";
import { ProviderPane } from "./providerPane";
import { SectionList } from "./sectionList";
import { SlideFrame } from "./slideFrame";
import type { modelSlideType } from "./slides";

export function ModelSlide({ slide }: { slide: modelSlideType }) {
    const { runs, isProcessing, sendMessage } = useCompareChat();

    return (
        <SlideFrame title={slide.title}>
            <div className="grid h-full grid-cols-[minmax(0,2fr)_minmax(0,3fr)] items-center gap-12 pb-8">
                <SectionList sections={slide.sections} />
                <div className="flex h-full min-h-0 flex-col gap-4">
                    <button
                        type="button"
                        disabled={isProcessing}
                        onClick={() => sendMessage(slide.prompt)}
                        className="self-start rounded-2xl border border-line bg-primary-soft px-4 py-2.5 text-left text-primary-ink hover:border-primary disabled:opacity-50"
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
