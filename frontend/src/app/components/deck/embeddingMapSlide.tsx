"use client";
import { useState } from "react";

import { embeddingsData } from "./deckData";
import { RichText } from "./richText";
import { ScatterPlot } from "./scatterPlot";
import type { embeddingMapSlideType } from "./slides";

const documents = [...new Map(embeddingsData.chunks.map((chunk) => [chunk.documentId, chunk.title])).entries()];

function chipClassName(isActive: boolean) {
    return `rounded-full border px-3 py-1 text-xs transition ${isActive ? "border-primary bg-primary-soft text-primary-ink" : "border-line bg-surface text-ink-muted hover:text-ink"}`;
}

export function EmbeddingMapSlide({ slide }: { slide: embeddingMapSlideType }) {
    const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);
    const [questionIndex, setQuestionIndex] = useState<number | null>(null);
    const [hoveredChunkIndex, setHoveredChunkIndex] = useState<number | null>(null);
    const hoveredChunk = hoveredChunkIndex === null ? null : embeddingsData.chunks[hoveredChunkIndex];
    const highlightedDocumentId = hoveredChunk?.documentId ?? selectedDocumentId;

    return (
        <div className="mx-auto flex h-full w-full max-w-7xl flex-col gap-3 px-10 py-6">
            <h2 className="text-3xl font-semibold tracking-tight text-ink">{slide.title}</h2>
            <div className="flex flex-wrap gap-2">
                {embeddingsData.questions.map((question, index) => (
                    <button key={question.id} type="button" aria-pressed={questionIndex === index} onClick={() => setQuestionIndex(questionIndex === index ? null : index)} className={chipClassName(questionIndex === index)}>
                        {question.text}
                    </button>
                ))}
            </div>
            <div className="grid min-h-0 flex-1 grid-cols-2 gap-6">
                {embeddingsData.models.map((model) => (
                    <div key={model.id} className="flex min-h-0 flex-col gap-2">
                        <p className="text-sm font-semibold text-ink">{model.label} · {model.dimensions} dimensões</p>
                        <div className="min-h-0 flex-1">
                            <ScatterPlot
                                model={model}
                                chunks={embeddingsData.chunks}
                                highlightedDocumentId={highlightedDocumentId}
                                questionIndex={questionIndex}
                                hoveredChunkIndex={hoveredChunkIndex}
                                onHoverChunk={setHoveredChunkIndex}
                            />
                        </div>
                        <p className="text-sm text-ink-muted"><RichText text={slide.modelNotes[model.id]} /></p>
                    </div>
                ))}
            </div>
            <p className="h-10 text-sm text-ink">{hoveredChunk ? `${hoveredChunk.title}: ${hoveredChunk.text.slice(0, 160)}` : slide.caption}</p>
            <div className="flex flex-wrap gap-1.5">
                {documents.map(([documentId, title]) => (
                    <button key={documentId} type="button" aria-pressed={selectedDocumentId === documentId} onClick={() => setSelectedDocumentId(selectedDocumentId === documentId ? null : documentId)} className={chipClassName(selectedDocumentId === documentId)}>
                        {title}
                    </button>
                ))}
            </div>
        </div>
    );
}
