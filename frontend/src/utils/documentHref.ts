export type documentTarget = { id: string, paragraph: number | null };

const DOCUMENT_HREF = /^\/documentos\/([^/?#]+)(?:\?trecho=(\d+))?$/;

export function parseDocumentHref(href: string): documentTarget | null {
    const match = DOCUMENT_HREF.exec(href);
    if (!match) return null;
    try {
        return { id: decodeURIComponent(match[1]), paragraph: match[2] === undefined ? null : Number(match[2]) };
    } catch {
        return null;
    }
}
