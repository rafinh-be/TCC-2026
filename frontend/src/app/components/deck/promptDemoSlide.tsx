"use client";
import { useState } from "react";

import { useChat } from "@/hooks/useChat";
import type { documentTarget } from "@/utils/documentHref";
import { Chatbox } from "../chatbox/chatbox";
import { DocumentOpenerContext } from "../chatbox/documentOpener";
import { DocumentPane } from "./documentPane";
import { SectionBlock } from "./sectionList";
import { SlideFrame } from "./slideFrame";
import type { promptDemoSlideType } from "./slides";

export function PromptDemoSlide({ slide }: { slide: promptDemoSlideType }) {
    const { messages, isProcessing, liveThinking, sendMessage } = useChat();
    const [openedDocument, setOpenedDocument] = useState<documentTarget | null>(null);

    const sendScriptedPrompt = (prompt: string) => {
        setOpenedDocument(null);
        sendMessage(prompt);
    };

    return (
        <SlideFrame title={slide.title}>
            <div className="grid h-full grid-cols-[minmax(0,2fr)_minmax(0,3fr)] gap-10 pb-4">
                <div className="flex min-h-0 flex-col justify-center gap-5">
                    <SectionBlock section={slide.section} size="dense" />
                    <div className="flex flex-col items-start gap-2">
                        {slide.prompts.map((prompt) => (
                            <button
                                key={prompt}
                                type="button"
                                disabled={isProcessing}
                                onClick={() => sendScriptedPrompt(prompt)}
                                className="rounded-2xl border border-line bg-primary-soft px-4 py-2 text-left text-primary-ink hover:border-primary disabled:opacity-50"
                            >
                                {prompt}
                            </button>
                        ))}
                    </div>
                </div>
                <DocumentOpenerContext.Provider value={setOpenedDocument}>
                    <div className="flex min-h-0 flex-col overflow-hidden rounded-2xl border border-line">
                        {openedDocument
                            ? <DocumentPane key={`${openedDocument.id}:${openedDocument.paragraph}`} target={openedDocument} onBack={() => setOpenedDocument(null)} />
                            : <Chatbox messages={messages} isProcessing={isProcessing} liveThinking={liveThinking} onSendMessage={sendMessage} />}
                    </div>
                </DocumentOpenerContext.Provider>
            </div>
        </SlideFrame>
    );
}
