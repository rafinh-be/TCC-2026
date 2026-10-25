"use client";
import { useDocument } from "@/hooks/useDocument";
import type { documentTarget } from "@/utils/documentHref";
import { DocumentContent } from "../documents/documentContent";

export function DocumentPane({ target, onBack }: { target: documentTarget, onBack: () => void }) {
    const { document: loadedDocument, loading } = useDocument(target.id);

    return (
        <div className="flex min-h-0 flex-1 flex-col">
            <div className="border-b border-line px-4 py-2">
                <button type="button" onClick={onBack} className="btn btn-ghost btn-sm text-ink-muted hover:bg-line">
                    ← Voltar ao chat
                </button>
            </div>
            {loading && <p className="px-6 pt-10 text-sm text-ink-muted">Carregando documento</p>}
            {!loading && !loadedDocument && <p className="px-6 pt-10 text-sm text-ink-muted">Não foi possível carregar o documento.</p>}
            {loadedDocument && <DocumentContent document={loadedDocument} highlightedParagraph={target.paragraph} />}
        </div>
    );
}
