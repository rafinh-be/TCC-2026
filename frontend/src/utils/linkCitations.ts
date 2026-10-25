export type citationType = { number: number, doc_id: string, title: string, chunk_index: number | null };

const CITATION_MARKER = /\[(\d+(?:\s*,\s*\d+)*)\]/g;

export function citationHref(citation: citationType) {
    const documentPath = `/documentos/${encodeURIComponent(citation.doc_id)}`;
    return citation.chunk_index === null ? documentPath : `${documentPath}?trecho=${citation.chunk_index}`;
}

export function linkCitations(content: string, citations: citationType[]) {
    if (citations.length === 0) return content;
    return content.replace(CITATION_MARKER, (_marker, numbers: string) => {
        const links = numbers.split(",")
            .map((number) => citations.find((citation) => citation.number === Number(number)))
            .filter((citation): citation is citationType => citation !== undefined)
            .map((citation) => `[${citation.number}](${citationHref(citation)})`);
        return links.join(" ");
    });
}
