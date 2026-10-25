"use client";
import { useEffect, useState } from "react";

import { API_URL } from "@/config/api";

export type documentSummaryType = { id: string, title: string, tags: string[] };

let documentsRequest: Promise<documentSummaryType[]> | null = null;

function fetchDocuments() {
    documentsRequest ??= fetch(`${API_URL}/documents`)
        .then((response) => {
            if (!response.ok) throw new Error("Falha ao carregar documentos");
            return response.json();
        })
        .catch((error) => {
            documentsRequest = null;
            throw error;
        });
    return documentsRequest;
}

export function useDocuments() {
    const [documents, setDocuments] = useState<documentSummaryType[]>([]);

    useEffect(() => {
        fetchDocuments().then(setDocuments).catch(console.error);
    }, []);

    return documents;
}
