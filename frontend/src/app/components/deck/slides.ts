export type titleSlideType = { kind: "title", id: string, kicker: string, title: string, authors: string, institution: string };
export type textSlideType = { kind: "text", id: string, title: string, bullets: string[] };
export type gridItemType = { heading: string, text: string };
export type gridSlideType = { kind: "grid", id: string, title: string, items: gridItemType[] };
export type conceptsSlideType = { kind: "concepts", id: string, title: string, items: gridItemType[] };
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
export type slideKindType = titleSlideType | textSlideType | gridSlideType | conceptsSlideType | demoSlideType | pipelineSlideType | providerCompareSlideType | chunkingSlideType | embeddingMapSlideType | retrievalCompareSlideType | compareSlideType | metricsSlideType | sourcesSlideType;
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
    {
        kind: "concepts",
        id: "conceitos",
        title: "Conceitos importantes",
        refs: ["rag"],
        items: [
            { heading: "Modelo e agente", text: "Um modelo de linguagem recebe um texto e devolve um texto: não guarda memória entre chamadas e só conhece o que aprendeu no treinamento. Um agente é esse modelo cercado por instruções, histórico da conversa e acesso a uma base de consulta. No projeto, o modelo é o Gemini ou o Ollama; o agente é o modelo mais o prompt, a busca na base e as regras de recusa." },
            { heading: "Engenharia de prompt", text: "Prompt é o conjunto de instruções e de contexto que o modelo recebe a cada pergunta. Engenharia de prompt é escrever essas instruções para controlar o comportamento do modelo. No projeto, elas definem a identidade do agente e restrições absolutas: responder só com a base, não diagnosticar e não estimar números." },
            { heading: "RAG", text: "A geração aumentada por recuperação busca trechos relevantes em uma base de conhecimento e os entrega ao modelo junto com a pergunta{ref:rag}. Para atualizar o conhecimento basta atualizar a base, sem treinar o modelo de novo. No projeto, a busca combina vetores e texto sobre 16 documentos." },
            { heading: "Grounding", text: "Grounding é apoiar cada afirmação da resposta nos trechos recuperados. Sem evidência suficiente, o assistente se abstém e recusa em vez de inventar; diante de uma pergunta ambígua, faz uma pergunta breve de esclarecimento. Quem decide se a evidência basta é o modelo: não há um verificador independente." },
        ],
    },
];

function stepCount(slide: slideType) {
    if (slide.kind === "pipeline") return slide.stages.length;
    if (slide.kind === "concepts") return slide.items.length;
    return 1;
}

export const stepCounts = slides.map(stepCount);
