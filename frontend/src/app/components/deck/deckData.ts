import chunksJson from "./data/chunks.json";
import embeddingsJson from "./data/embeddings.json";

export type chunkSpan = [number, number];
export type chunkedDocumentType = { id: string, title: string, content: string, spans: { paragraph: chunkSpan[], window: chunkSpan[] } };
export type chunksDataType = { settings: { size: number, overlap: number }, documents: chunkedDocumentType[] };

export type embeddedChunkType = { id: string, documentId: string, title: string, text: string };
export type neighborType = { chunkIndex: number, score: number };
export type embeddingModelType = {
    id: string,
    label: string,
    dimensions: number,
    points: [number, number][],
    questionPoints: [number, number][],
    neighbors: neighborType[][],
};
export type embeddingsDataType = { chunks: embeddedChunkType[], questions: { id: string, text: string }[], models: embeddingModelType[] };

export const chunksData = chunksJson as chunksDataType;
export const embeddingsData = embeddingsJson as embeddingsDataType;
