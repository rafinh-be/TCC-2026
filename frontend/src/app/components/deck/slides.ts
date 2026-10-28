export type titleSlideType = { kind: "title", id: string, kicker: string, title: string, authors: string, institution: string };
export type textSlideType = { kind: "text", id: string, title: string, bullets: string[] };
export type gridItemType = { heading: string, text: string };
export type gridSlideType = { kind: "grid", id: string, title: string, items: gridItemType[] };
export type listSlideType = { kind: "list", id: string, title: string, items: gridItemType[] };
export type siteSectionType = { heading: string, bullets: string[] };
export type siteSlideType = { kind: "site", id: string, title: string, url: string, sections: siteSectionType[] };
export type modelSlideType = { kind: "model", id: string, title: string, sections: siteSectionType[], prompt: string, panes: { gemini: string, ollama: string } };
export type topicSlideType = { kind: "topic", id: string, title: string, sections: siteSectionType[] };
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
export type slideKindType = titleSlideType | textSlideType | gridSlideType | listSlideType | siteSlideType | modelSlideType | topicSlideType | conceptsSlideType | demoSlideType | pipelineSlideType | providerCompareSlideType | chunkingSlideType | embeddingMapSlideType | retrievalCompareSlideType | compareSlideType | metricsSlideType | sourcesSlideType;
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
            { heading: "Infraestrutura", text: "Deploy na rede e backend idempotente" },
            { heading: "Modelo e raciocínio", text: "Overhaul do modelo, thinking e processamento na rede pelo Gemini" },
            { heading: "Busca e conhecimento", text: "Overhaul dos embeddings e do RAG (chunking)" },
            { heading: "Respostas confiáveis", text: "Grounding, clarificação e atribuição de fontes" },
        ],
    },
    {
        kind: "site",
        id: "infraestrutura",
        title: "Infraestrutura",
        url: "https://tcc-2026-1.onrender.com/",
        sections: [
            {
                heading: "Deploy na rede",
                bullets: [
                    "Do protótipo local para um app publicado, acessível a qualquer pessoa pela internet.",
                    "Frontend totalmente novo, em Next.js.",
                    "O projeto chega a um estado muito mais próximo de um produto acabado.",
                ],
            },
            {
                heading: "Backend idempotente",
                bullets: [
                    "Iniciar o backend várias vezes leva sempre ao mesmo estado: só reindexa quando algo mudou.",
                    "Novas instâncias sobem sem refazer a base de embeddings.",
                    "Abre caminho para escalar e atender N usuários ao mesmo tempo.",
                ],
            },
        ],
    },
    {
        kind: "topic",
        id: "overhaul-modelo",
        title: "Overhaul do modelo",
        sections: [
            {
                heading: "O que é",
                bullets: [
                    "O modelo de linguagem deixou de ser fixo: o provedor é escolhido ao iniciar o backend.",
                    "Dois provedores: Ollama, rodando localmente (qwen3.5:9b), e Gemini, na nuvem (gemini-3.6-flash).",
                ],
            },
            {
                heading: "Por que importa",
                bullets: [
                    "É o modelo que escreve a resposta final: sua capacidade define a qualidade do texto.",
                    "Modelos mais capazes tendem a seguir melhor instruções longas, como não diagnosticar e responder só com a base.",
                ],
            },
            {
                heading: "Na prática",
                bullets: [
                    "O resto do pipeline não muda: mesma busca, mesmo prompt, mesmas citações.",
                    "Trocar de modelo é uma opção de inicialização, não uma reescrita.",
                ],
            },
        ],
    },
    {
        kind: "topic",
        id: "thinking",
        title: "Thinking",
        refs: ["cot", "gemini-thinking", "self-refine", "self-correct"],
        sections: [
            {
                heading: "O que é",
                bullets: [
                    "Antes de responder, o modelo gera passos intermediários de raciocínio{ref:cot}.",
                    "A API do Gemini devolve um resumo desse raciocínio, não os passos completos{ref:gemini-thinking}.",
                ],
            },
            {
                heading: "Por que importa",
                bullets: [
                    "Substitui a segunda chamada de crítica e refinamento: menos chamadas por pergunta.",
                    "O refinamento iterativo melhora saídas{ref:self-refine}, mas modelos nem sempre corrigem o próprio raciocínio sem feedback externo{ref:self-correct}.",
                ],
            },
            {
                heading: "Na prática",
                bullets: [
                    "O nível de raciocínio é configurável (minimal, low, medium, high): mais raciocínio, mais latência.",
                    "A interface usa o nível medium e mostra o resumo ao vivo enquanto o modelo pensa.",
                ],
            },
        ],
    },
    {
        kind: "model",
        id: "processamento-na-rede",
        title: "Processamento na rede",
        prompt: "Quais são os sinais de alerta da pré-eclâmpsia?",
        panes: { gemini: "Gemini · gemini-3.6-flash", ollama: "Ollama · qwen3.5:9b (local)" },
        sections: [
            {
                heading: "O que é",
                bullets: [
                    "O modelo roda na API do Gemini, na nuvem, e não mais na máquina local.",
                ],
            },
            {
                heading: "Por que importa",
                bullets: [
                    "O app não depende do hardware de quem o executa: qualquer navegador usa o mesmo modelo.",
                    "O servidor publicado não precisa de uma GPU própria.",
                ],
            },
            {
                heading: "Na prática",
                bullets: [
                    "A chave de API fica no servidor, nunca no navegador.",
                    "Cada resposta mostra seu tempo, ao lado do modelo local respondendo à mesma pergunta.",
                ],
            },
        ],
    },
];

function stepCount(slide: slideType) {
    if (slide.kind === "pipeline") return slide.stages.length;
    if (slide.kind === "concepts") return slide.items.length;
    return 1;
}

export const stepCounts = slides.map(stepCount);
