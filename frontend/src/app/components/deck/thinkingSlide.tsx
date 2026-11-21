"use client";

import { useState } from "react";
import { API_URL } from "@/config/api";
import type { messageType } from "../chatbox/chatbox";
import type { providerRunType } from "@/hooks/useCompareChat";
import { readChatStream } from "@/utils/chatStream";
import { ProviderPane } from "./providerPane";
import { SectionBlock } from "./sectionList";
import { SlideFrame } from "./slideFrame";
import type { topicSlideType } from "./slides";

const prompt = "Uma gestante quer fazer a visita monitorada do HU-USP com 189 dias de gestação, outra com 210 dias. Ambas pretendem levar duas pessoas. Qual delas atende aos critérios e o que cada uma precisa mudar?";
const idle: providerRunType = { messages: [], isProcessing: false, liveThinking: [], startedAt: null, finishedAt: null };
type Mode = "with" | "without";

export function ThinkingSlide({ slide }: { slide: topicSlideType }) {
    const [runs, setRuns] = useState<Record<Mode, providerRunType>>({ with: idle, without: idle });
    const processing = runs.with.isProcessing || runs.without.isProcessing;

    const run = async (mode: Mode, history: messageType[]) => {
        const update = (change: (current: providerRunType) => providerRunType) =>
            setRuns((previous) => ({ ...previous, [mode]: change(previous[mode]) }));
        try {
            const response = await fetch(`${API_URL}/chat/stream`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ messages: history, provider: "ollama", think: mode === "with", model_variant: mode === "without" ? "base" : undefined, seed: mode === "without" ? 1 : undefined }),
            });
            if (!response.ok) throw new Error(`Falha ${response.status}`);
            await readChatStream(response, (event) => {
                if (event.type === "thinking") {
                    update((current) => ({ ...current, liveThinking: [...current.liveThinking, event.text] }));
                } else {
                    const message: messageType = event.type === "final"
                        ? { sender: "bot", content: event.answer.message.content, thinking: event.answer.message.thinking, sources: event.sources, citations: event.citations }
                        : { sender: "bot", content: event.message };
                    update((current) => ({ ...current, messages: [...history, message], liveThinking: [], isProcessing: false, finishedAt: Date.now() }));
                }
            });
        } catch {
            update((current) => ({ ...current, messages: [...history, { sender: "bot", content: "Não foi possível gerar a resposta. Tente novamente." }], isProcessing: false, finishedAt: Date.now() }));
        } finally {
            update((current) => current.isProcessing ? { ...current, isProcessing: false, finishedAt: Date.now() } : current);
        }
    };

    const compare = () => {
        const history: messageType[] = [{ sender: "user", content: prompt }];
        const started: providerRunType = { ...idle, messages: history, isProcessing: true, startedAt: Date.now() };
        setRuns({ with: started, without: started });
        void run("with", history);
        void run("without", history);
    };

    return (
        <SlideFrame title={slide.title}>
            <div className="flex h-full flex-col gap-5 pb-2">
                <div className="grid shrink-0 grid-cols-3 gap-5">
                    {slide.sections.map((section) => <SectionBlock key={section.heading} section={section} size="demonstration" />)}
                </div>
                <div className="flex min-h-0 flex-1 flex-col gap-3">
                    <button type="button" disabled={processing} onClick={compare} className="self-start rounded-2xl border border-line bg-primary-soft px-4 py-2 text-left text-xl text-primary-ink hover:border-primary disabled:opacity-50">
                        Comparar respostas: {prompt}
                    </button>
                    <div className="grid min-h-0 flex-1 grid-cols-2 divide-x divide-line overflow-hidden rounded-2xl border border-line">
                        <ProviderPane label="Qwen 3.5 9B · com thinking" run={runs.with} />
                        <ProviderPane label="Qwen 2.5 7B · sem thinking" run={runs.without} />
                    </div>
                </div>
            </div>
        </SlideFrame>
    );
}
