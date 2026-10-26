export type chunkSegment = { text: string, chunkIndexes: number[] };

export function chunkSegments(content: string, spans: [number, number][]): chunkSegment[] {
    const boundaries = [...new Set([0, content.length, ...spans.flat()])].sort((first, second) => first - second);
    return boundaries.slice(0, -1).map((start, index) => {
        const end = boundaries[index + 1];
        const chunkIndexes = spans.flatMap(([spanStart, spanEnd], chunkIndex) => (spanStart <= start && spanEnd >= end ? [chunkIndex] : []));
        return { text: content.slice(start, end), chunkIndexes };
    });
}
