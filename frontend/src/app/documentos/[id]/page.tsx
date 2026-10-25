import { notFound } from "next/navigation";

import { API_URL } from "@/config/api";
import { Sidebar } from "../../components/sidebar/sidebar";
import { DocumentContent, documentType } from "../../components/documents/documentContent";

async function fetchDocument(id: string): Promise<documentType | null> {
    const response = await fetch(`${API_URL}/documents/${encodeURIComponent(id)}`, { cache: "no-store" });
    if (response.status === 404) return null;
    if (!response.ok) throw new Error("Falha ao carregar documento");
    return response.json();
}

export default async function DocumentPage({ params, searchParams }: { params: Promise<{ id: string }>, searchParams: Promise<{ trecho?: string }> }) {
    const { id } = await params;
    const { trecho } = await searchParams;
    const highlightedParagraph = trecho !== undefined && /^\d+$/.test(trecho) ? Number(trecho) : null;
    const document = await fetchDocument(id);
    if (!document) notFound();

    return <Sidebar content={<DocumentContent document={document} highlightedParagraph={highlightedParagraph} />} />;
}
