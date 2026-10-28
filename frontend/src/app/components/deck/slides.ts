export type titleSlideType = { kind: "title", id: string, kicker: string, title: string, authors: string, institution: string };
export type textSlideType = { kind: "text", id: string, title: string, bullets: string[] };
export type gridItemType = { heading: string, text: string };
export type gridSlideType = { kind: "grid", id: string, title: string, items: gridItemType[] };
export type listSlideType = { kind: "list", id: string, title: string, items: string[] };
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
export type slideKindType = titleSlideType | textSlideType | gridSlideType | listSlideType | conceptsSlideType | demoSlideType | pipelineSlideType | providerCompareSlideType | chunkingSlideType | embeddingMapSlideType | retrievalCompareSlideType | compareSlideType | metricsSlideType | sourcesSlideType;
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
            { heading: "Modelo e agente", text: "Um modelo de linguagem (LLM) é um modelo de aprendizado de máquina que, após treinamentos intensivos, prevê o resultado esperado a partir de entradas e dialoga de forma quase humana. Sozinho, ele alucina: inventa respostas não factuais, porque seu treinamento não é composto só de conteúdo factual e sua diretriz principal é agradar o usuário, não ser preciso. Um agente é uma envoltura sobre o modelo que adiciona contextualização e iteração para gerar resultados mais precisos: engenharia de prompt, gerenciamento de contexto e etapas de verificação contornam os maiores problemas do modelo puro." },
            { heading: "Engenharia de prompt", text: "É a camada que contextualiza o modelo para o propósito da ferramenta. No projeto, o prompt apresenta o propósito do assistente, o perfil da paciente e a informação médica disponível, e fixa restrições: responder só com a base, não diagnosticar e não estimar números." },
            { heading: "RAG", text: "O RAG (Retrieval-Augmented Generation) transforma o modelo em um mecanismo de pesquisa: em vez de retornar apenas links, devolve um resumo do conteúdo encontrado, explicado da forma mais conveniente ao usuário{ref:rag}. Ao restringir o contexto a uma base limitada porém confiável, reduz dramaticamente a probabilidade de alucinação. No projeto, a base reúne 16 documentos de obstetrícia." },
            { heading: "Grounding", text: "Grounding é manter a resposta presa a fontes verificadas: o modelo só afirma o que está nos trechos recuperados, o que garante respostas factuais. Quando a base não traz informação suficiente, o assistente recusa em vez de inventar; diante de uma pergunta ambígua, pergunta antes de responder." },
        ],
    },
    {
        kind: "list",
        id: "novos-conceitos",
        title: "Novos conceitos",
        items: [
            "Overhaul do modelo e dos embeddings + thinking",
            "Backend idempotente",
            "Deploy na rede",
            "Overhaul do embedding e do RAG (chunking)",
            "Grounding e clarificação",
            "Atribuição de fontes",
            "Processamento na rede (pelo Gemini)",
        ],
    },
];

function stepCount(slide: slideType) {
    if (slide.kind === "pipeline") return slide.stages.length;
    if (slide.kind === "concepts") return slide.items.length;
    return 1;
}

export const stepCounts = slides.map(stepCount);
