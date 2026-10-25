type messageWithCitations = { citations?: { doc_id: string }[] };

export function citedDocumentIds(messages: messageWithCitations[]) {
    const ids = messages.flatMap((message) => message.citations ?? []).map((citation) => citation.doc_id);
    return [...new Set(ids)];
}
