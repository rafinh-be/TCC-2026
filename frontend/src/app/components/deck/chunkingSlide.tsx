"use client";
import { useState } from "react";

import { chunkSegments } from "@/utils/chunkSegments";
import { chunksData } from "./deckData";
import type { chunkingSlideType } from "./slides";

type strategyType = "paragraph" | "window";

const strategyLabels: Record<strategyType, string> = { paragraph: "Parágrafo", window: "Janela" };

function segmentClassName(chunkIndexes: number[]) {
    if (chunkIndexes.length === 0) return "text-ink-muted";
    if (chunkIndexes.length > 1) return "border-b-2 border-primary bg-alert-soft text-alert-ink";
    return chunkIndexes[0] % 2 === 0 ? "bg-primary-soft text-primary-ink" : "bg-line text-ink";
}

function segmentTitle(chunkIndexes: number[]) {
    if (chunkIndexes.length === 0) return undefined;
    if (chunkIndexes.length > 1) return `Sobreposição entre os trechos ${chunkIndexes.map((index) => index + 1).join(" e ")}`;
    return `Trecho ${chunkIndexes[0] + 1}`;
}

export function ChunkingSlide({ slide }: { slide: chunkingSlideType }) {
    const [strategy, setStrategy] = useState<strategyType>("paragraph");
    const [documentId, setDocumentId] = useState(chunksData.documents[0].id);
    const document = chunksData.documents.find((candidate) => candidate.id === documentId) ?? chunksData.documents[0];
    const spans = document.spans[strategy];
    const segments = chunkSegments(document.content, spans);
    const averageLength = Math.round(spans.reduce((total, [start, end]) => total + (end - start), 0) / spans.length);

    return (
        <div className="mx-auto flex h-full w-full max-w-7xl flex-col gap-5 px-10 py-8">
            <h2 className="text-3xl font-semibold tracking-tight text-ink">{slide.title}</h2>
            <div className="grid min-h-0 flex-1 grid-cols-[minmax(0,1fr)_minmax(0,3fr)] gap-6">
                <div className="flex min-h-0 flex-col gap-4">
                    <div className="flex gap-2">
                        {(Object.keys(strategyLabels) as strategyType[]).map((option) => (
                            <button
                                key={option}
                                type="button"
                                aria-pressed={strategy === option}
                                onClick={() => setStrategy(option)}
                                className={`rounded-full border px-4 py-1.5 text-sm font-medium transition ${strategy === option ? "border-primary bg-primary-soft text-primary-ink" : "border-line bg-surface text-ink-muted hover:text-ink"}`}
                            >
                                {strategyLabels[option]}
                            </button>
                        ))}
                    </div>
                    <ul className="flex min-h-0 flex-1 flex-col gap-1 overflow-y-auto pr-1">
                        {chunksData.documents.map((candidate) => (
                            <li key={candidate.id}>
                                <button
                                    type="button"
                                    aria-pressed={candidate.id === document.id}
                                    onClick={() => setDocumentId(candidate.id)}
                                    className={`w-full rounded-lg px-3 py-2 text-left text-sm transition ${candidate.id === document.id ? "bg-primary-soft text-primary-ink" : "text-ink-muted hover:bg-line"}`}
                                >
                                    {candidate.title}
                                </button>
                            </li>
                        ))}
                    </ul>
                </div>
                <div className="flex min-h-0 flex-col gap-3">
                    <p className="text-base text-ink-muted">{slide.strategyNotes[strategy]}</p>
                    <p className="text-sm font-medium text-ink">{spans.length} trechos · média de {averageLength} caracteres</p>
                    <div className="min-h-0 flex-1 overflow-y-auto rounded-2xl border border-line bg-surface p-5">
                        <p className="whitespace-pre-wrap text-sm leading-relaxed">
                            {segments.map((segment, index) => (
                                <span key={index} className={segmentClassName(segment.chunkIndexes)} title={segmentTitle(segment.chunkIndexes)}>
                                    {segment.text}
                                </span>
                            ))}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
