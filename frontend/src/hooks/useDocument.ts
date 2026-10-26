"use client";
import { useEffect, useState } from "react";

import { API_URL } from "@/config/api";
import type { documentType } from "@/app/components/documents/documentContent";

type documentResult = { id: string, document: documentType | null };

export function useDocument(id: string) {
    const [result, setResult] = useState<documentResult | null>(null);

    useEffect(() => {
        let cancelled = false;
        fetch(`${API_URL}/documents/${encodeURIComponent(id)}`)
            .then((response) => {
                if (!response.ok) throw new Error("Falha ao carregar documento");
                return response.json();
            })
            .then((loadedDocument: documentType) => {
                if (!cancelled) setResult({ id, document: loadedDocument });
            })
            .catch(() => {
                if (!cancelled) setResult({ id, document: null });
            });
        return () => {
            cancelled = true;
        };
    }, [id]);

    if (result?.id !== id) return { document: null, loading: true };
    return { document: result.document, loading: false };
}
