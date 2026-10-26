"use client";
import { useState } from "react";

import { useElapsedSeconds } from "@/hooks/useElapsedSeconds";
import type { providerRunType } from "@/hooks/useCompareChat";
import type { documentTarget } from "@/utils/documentHref";
import { Chatbox } from "../chatbox/chatbox";
import { DocumentOpenerContext } from "../chatbox/documentOpener";
import { DocumentPane } from "./documentPane";

export function ProviderPane({ label, run }: { label: string, run: providerRunType }) {
    const [openedDocument, setOpenedDocument] = useState<documentTarget | null>(null);
    const elapsedSeconds = useElapsedSeconds(run.startedAt, run.finishedAt);

    return (
        <div className="flex min-h-0 flex-col border-line">
            <div className="flex items-baseline justify-between gap-4 border-b border-line px-6 py-3">
                <h3 className="text-lg font-semibold text-ink">{label}</h3>
                <span className="text-lg font-medium tabular-nums text-primary-ink">
                    {elapsedSeconds === null ? "" : `${elapsedSeconds.toFixed(1)} s`}
                </span>
            </div>
            <DocumentOpenerContext.Provider value={setOpenedDocument}>
                {openedDocument
                    ? <DocumentPane key={`${openedDocument.id}:${openedDocument.paragraph}`} target={openedDocument} onBack={() => setOpenedDocument(null)} />
                    : <Chatbox messages={run.messages} isProcessing={run.isProcessing} liveThinking={run.liveThinking} onSendMessage={() => {}} hideInput />}
            </DocumentOpenerContext.Provider>
        </div>
    );
}
