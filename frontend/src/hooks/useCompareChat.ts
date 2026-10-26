"use client";
import { useState } from "react";

import type { messageType } from "@/app/components/chatbox/chatbox";
import { API_URL } from "@/config/api";
import { readChatStream } from "@/utils/chatStream";

export const COMPARE_PROVIDERS = ["gemini", "ollama"] as const;
export type compareProviderType = (typeof COMPARE_PROVIDERS)[number];

export type providerRunType = {
    messages: messageType[],
    isProcessing: boolean,
    liveThinking: string[],
    startedAt: number | null,
    finishedAt: number | null,
};

const GENERIC_ERROR = "Não foi possível gerar a resposta. Tente novamente.";

const idleRun: providerRunType = { messages: [], isProcessing: false, liveThinking: [], startedAt: null, finishedAt: null };

const isCompareProvider = (provider: string | undefined): provider is compareProviderType =>
    COMPARE_PROVIDERS.some((candidate) => candidate === provider);

export function useCompareChat() {
    const [runs, setRuns] = useState<Record<compareProviderType, providerRunType>>({ gemini: idleRun, ollama: idleRun });
    const isProcessing = COMPARE_PROVIDERS.some((provider) => runs[provider].isProcessing);

    const updateRun = (provider: compareProviderType, change: (run: providerRunType) => providerRunType) => {
        setRuns((previous) => ({ ...previous, [provider]: change(previous[provider]) }));
    };

    const sendMessage = async (inputMessage: string) => {
        const history: messageType[] = [{ sender: "user", content: inputMessage }];
        const startedAt = Date.now();
        const startedRun: providerRunType = { messages: history, isProcessing: true, liveThinking: [], startedAt, finishedAt: null };
        setRuns({ gemini: startedRun, ollama: startedRun });

        const finish = (provider: compareProviderType, message: messageType) => {
            updateRun(provider, (run) => ({ ...run, messages: [...history, message], isProcessing: false, liveThinking: [], finishedAt: Date.now() }));
        };

        try {
            const response = await fetch(`${API_URL}/chat/compare`, {
                method: "POST",
                body: JSON.stringify({ messages: history }),
                headers: { "Content-Type": "application/json" }
            });
            if (!response.ok) throw new Error(`Falha ${response.status}`);
            await readChatStream(response, (event) => {
                if (!isCompareProvider(event.provider)) {
                    if (event.type === "error") COMPARE_PROVIDERS.forEach((provider) => finish(provider, { sender: "bot", content: event.message }));
                    return;
                }
                const provider = event.provider;
                if (event.type === "thinking") {
                    updateRun(provider, (run) => ({ ...run, liveThinking: [...run.liveThinking, event.text] }));
                } else if (event.type === "final") {
                    finish(provider, { sender: "bot", content: event.answer.message.content, thinking: event.answer.message.thinking, sources: event.sources, citations: event.citations });
                } else {
                    finish(provider, { sender: "bot", content: event.message });
                }
            });
        } catch (e) {
            console.log(e);
            COMPARE_PROVIDERS.forEach((provider) => finish(provider, { sender: "bot", content: GENERIC_ERROR }));
        } finally {
            COMPARE_PROVIDERS.forEach((provider) => {
                updateRun(provider, (run) => (run.isProcessing ? { ...run, isProcessing: false, liveThinking: [], finishedAt: Date.now() } : run));
            });
        }
    };

    return { runs, isProcessing, sendMessage };
}
