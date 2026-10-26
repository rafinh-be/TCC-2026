"use client";
import { COMPARE_PROVIDERS, useCompareChat } from "@/hooks/useCompareChat";
import { ProviderPane } from "./providerPane";
import type { providerCompareSlideType } from "./slides";

export function ProviderCompareSlide({ slide }: { slide: providerCompareSlideType }) {
    const { runs, isProcessing, sendMessage } = useCompareChat();

    return (
        <div className="flex h-full min-h-0 flex-col">
            <div className="flex flex-col gap-3 px-10 py-6">
                <p className="text-sm font-medium uppercase tracking-wide text-primary">{slide.claim}</p>
                <div className="flex flex-wrap items-center justify-between gap-4">
                    <h2 className="text-3xl font-semibold tracking-tight text-ink">{slide.title}</h2>
                    <button
                        type="button"
                        disabled={isProcessing}
                        onClick={() => sendMessage(slide.prompt)}
                        className="rounded-2xl border border-line bg-primary-soft px-4 py-2.5 text-left text-primary-ink hover:border-primary disabled:opacity-50"
                    >
                        {slide.prompt}
                    </button>
                </div>
                <p className="text-sm text-ink-muted">{slide.caption}</p>
            </div>
            <div className="grid min-h-0 flex-1 grid-cols-2 divide-x divide-line border-t border-line">
                {COMPARE_PROVIDERS.map((provider) => (
                    <ProviderPane key={provider} label={slide.panes[provider]} run={runs[provider]} />
                ))}
            </div>
        </div>
    );
}
