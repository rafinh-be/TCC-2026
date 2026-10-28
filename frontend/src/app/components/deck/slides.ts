export type titleSlideType = { kind: "title", id: string, kicker: string, title: string, authors: string, institution: string };
export type textSlideType = { kind: "text", id: string, title: string, bullets: string[] };
export type gridItemType = { heading: string, text: string };
export type gridSlideType = { kind: "grid", id: string, title: string, items: gridItemType[] };
export type demoSlideType = { kind: "demo", id: string, claim: string, title: string, points: string[], prompt: string };
export type pipelineSlideType = { kind: "pipeline", id: string, title: string, stages: { label: string, detail: string }[], note?: string };
export type compareSideType = { label: string, points: string[] };
export type compareSlideType = { kind: "compare", id: string, title: string, before: compareSideType, after: compareSideType, note: string };
export type chunkingSlideType = { kind: "chunking", id: string, title: string, strategyNotes: { paragraph: string, window: string } };
export type embeddingMapSlideType = { kind: "embeddingMap", id: string, title: string, caption: string, modelNotes: Record<string, string> };
export type retrievalCompareSlideType = { kind: "retrievalCompare", id: string, title: string, caption: string };
export type providerCompareSlideType = { kind: "providerCompare", id: string, claim: string, title: string, prompt: string, caption: string, panes: { gemini: string, ollama: string } };
export type metricsSlideType = { kind: "metrics", id: string, title: string };
export type sourcesSlideType = { kind: "sources", id: string, title: string };
export type slideKindType = titleSlideType | textSlideType | gridSlideType | demoSlideType | pipelineSlideType | providerCompareSlideType | chunkingSlideType | embeddingMapSlideType | retrievalCompareSlideType | compareSlideType | metricsSlideType | sourcesSlideType;
export type slideType = slideKindType & { refs?: string[] };

export const slides: slideType[] = [
    {
        kind: "title",
        id: "titulo",
        kicker: "Trabalho de Conclusão de Curso · Apresentação intermediária",
        title: "Assistente de IA para Letramento em Saúde em Obstetrícia",
        authors: "Rafa Bertão de Sousa · Victor Rosselli Moraca",
        institution: "Escola Politécnica da Universidade de São Paulo · 2026",
    },
    {
        kind: "grid",
        id: "recap",
        title: "Onde estávamos",
        refs: ["rag"],
        items: [
            { heading: "Problema", text: "O baixo letramento em saúde reduz a adesão a tratamentos e sobrecarrega os pronto-socorros." },
            { heading: "Proposta", text: "Um assistente de IA que responde apenas a partir de uma base de conhecimento confiável (RAG){ref:rag}." },
            { heading: "Escopo", text: "Obstetrícia, uma área com quadros bem catalogados e pacientes em geral saudáveis." },
            { heading: "Arquitetura", text: "Cinco pilares: base de dados, modelo, engenharia de prompt, verificação e interface." },
        ],
    },
];

export const stepCounts = slides.map((slide) => (slide.kind === "pipeline" ? slide.stages.length : 1));
