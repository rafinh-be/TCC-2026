"use client";
import { useState } from "react";

import { useChat } from "@/hooks/useChat";
import type { documentTarget } from "@/utils/documentHref";
import { Chatbox } from "../chatbox/chatbox";
import { DocumentOpenerContext } from "../chatbox/documentOpener";
import { DocumentPane } from "./documentPane";
import { PointCards } from "./pointCards";
import type { demoSlideType } from "./slides";

export function DemoSlide({ slide }: { slide: demoSlideType }) {
    const { messages, isProcessing, liveThinking, sendMessage } = useChat();
    const [openedDocument, setOpenedDocument] = useState<documentTarget | null>(null);

    const sendScriptedPrompt = () => {
        setOpenedDocument(null);
        sendMessage(slide.prompt);
    };

    return (
        <div className="grid h-full min-h-0 grid-cols-[minmax(0,2fr)_minmax(0,3fr)]">
            <div className="flex min-h-0 flex-col gap-6 overflow-y-auto px-10 py-12">
                <p className="text-sm font-medium uppercase tracking-wide text-primary">{slide.claim}</p>
                <h2 className="text-3xl font-semibold tracking-tight text-ink">{slide.title}</h2>
                <PointCards points={slide.points} size="compact" />
                <button
                    type="button"
                    disabled={isProcessing}
                    onClick={sendScriptedPrompt}
                    className="mt-auto self-start rounded-2xl border border-line bg-primary-soft px-4 py-2.5 text-left text-primary-ink hover:border-primary disabled:opacity-50"
                >
                    {slide.prompt}
                </button>
            </div>
            <DocumentOpenerContext.Provider value={setOpenedDocument}>
                <div className="flex min-h-0 flex-col border-l border-line">
                    {openedDocument
                        ? <DocumentPane key={`${openedDocument.id}:${openedDocument.paragraph}`} target={openedDocument} onBack={() => setOpenedDocument(null)} />
                        : <Chatbox messages={messages} isProcessing={isProcessing} liveThinking={liveThinking} onSendMessage={sendMessage} />}
                </div>
            </DocumentOpenerContext.Provider>
        </div>
    );
}
