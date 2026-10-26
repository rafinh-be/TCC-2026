import type { embeddedChunkType, embeddingModelType } from "./deckData";

type scatterPlotProps = {
    model: embeddingModelType,
    chunks: embeddedChunkType[],
    highlightedDocumentId: string | null,
    questionIndex: number | null,
    hoveredChunkIndex: number | null,
    onHoverChunk: (chunkIndex: number | null) => void,
};

function pointClassName(isHighlighted: boolean, hasHighlight: boolean) {
    if (isHighlighted) return "fill-primary";
    return hasHighlight ? "fill-ink-muted opacity-25" : "fill-ink-muted opacity-60";
}

export function ScatterPlot({ model, chunks, highlightedDocumentId, questionIndex, hoveredChunkIndex, onHoverChunk }: scatterPlotProps) {
    const hasHighlight = highlightedDocumentId !== null;
    const neighborIndexes = questionIndex === null ? [] : model.neighbors[questionIndex].map((neighbor) => neighbor.chunkIndex);
    const orderedIndexes = model.points
        .map((_, index) => index)
        .sort((first, second) => Number(chunks[first].documentId === highlightedDocumentId) - Number(chunks[second].documentId === highlightedDocumentId));

    return (
        <svg viewBox="0 0 100 100" className="h-full w-full rounded-2xl border border-line bg-surface">
            {orderedIndexes.map((index) => {
                const [x, y] = model.points[index];
                const isHighlighted = chunks[index].documentId === highlightedDocumentId;
                return (
                    <circle
                        key={index}
                        cx={x * 100}
                        cy={y * 100}
                        r={index === hoveredChunkIndex ? 2.2 : isHighlighted ? 1.7 : 1.2}
                        className={pointClassName(isHighlighted, hasHighlight)}
                        onMouseEnter={() => onHoverChunk(index)}
                        onMouseLeave={() => onHoverChunk(null)}
                    />
                );
            })}
            {neighborIndexes.map((index) => (
                <circle key={`ring-${index}`} cx={model.points[index][0] * 100} cy={model.points[index][1] * 100} r={2.6} className="pointer-events-none fill-none stroke-ink" strokeWidth={0.4} />
            ))}
            {questionIndex !== null && (
                <circle cx={model.questionPoints[questionIndex][0] * 100} cy={model.questionPoints[questionIndex][1] * 100} r={2.4} className="pointer-events-none fill-ink" />
            )}
        </svg>
    );
}
