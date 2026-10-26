"use client";
import { useState } from "react";

import { embeddingsData } from "./deckData";
import { RichText } from "./richText";
import type { retrievalCompareSlideType } from "./slides";

export function RetrievalCompareSlide({ slide }: { slide: retrievalCompareSlideType }) {
    const [questionIndex, setQuestionIndex] = useState(0);

    return (
        <div className="mx-auto flex h-full w-full max-w-7xl flex-col gap-4 px-10 py-6">
            <h2 className="text-3xl font-semibold tracking-tight text-ink">{slide.title}</h2>
            <div className="flex flex-wrap gap-2">
                {embeddingsData.questions.map((question, index) => (
                    <button
                        key={question.id}
                        type="button"
                        aria-pressed={questionIndex === index}
                        onClick={() => setQuestionIndex(index)}
                        className={`rounded-full border px-3 py-1 text-sm transition ${questionIndex === index ? "border-primary bg-primary-soft text-primary-ink" : "border-line bg-surface text-ink-muted hover:text-ink"}`}
                    >
                        {question.text}
                    </button>
                ))}
            </div>
            <div className="grid min-h-0 flex-1 grid-cols-2 gap-6 overflow-y-auto">
                {embeddingsData.models.map((model, modelIndex) => {
                    const otherChunkIndexes = embeddingsData.models[1 - modelIndex].neighbors[questionIndex].map((neighbor) => neighbor.chunkIndex);
                    return (
                        <section key={model.id} className="flex flex-col gap-3">
                            <h3 className="text-lg font-semibold text-ink">{model.label}</h3>
                            <ol className="flex flex-col gap-2">
                                {model.neighbors[questionIndex].map((neighbor, rank) => {
                                    const chunk = embeddingsData.chunks[neighbor.chunkIndex];
                                    return (
                                        <li key={chunk.id} className="flex flex-col gap-1 rounded-2xl border border-line bg-surface px-4 py-3">
                                            <div className="flex items-center justify-between gap-3 text-sm">
                                                <span className="font-medium text-ink">{rank + 1}. {chunk.title}</span>
                                                <span className="flex items-center gap-2">
                                                    {otherChunkIndexes.includes(neighbor.chunkIndex) && (
                                                        <span className="rounded-full bg-primary-soft px-2 py-0.5 text-xs text-primary-ink">nos dois</span>
                                                    )}
                                                    <span className="text-ink-muted">{neighbor.score.toFixed(2)}</span>
                                                </span>
                                            </div>
                                            <p className="text-sm text-ink-muted">{chunk.text.slice(0, 140)}{chunk.text.length > 140 ? "…" : ""}</p>
                                        </li>
                                    );
                                })}
                            </ol>
                        </section>
                    );
                })}
            </div>
            <p className="text-sm text-ink-muted"><RichText text={slide.caption} /></p>
        </div>
    );
}
