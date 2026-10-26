export type titleSlideType = { kind: "title", id: string, kicker: string, title: string, authors: string, institution: string };
export type textSlideType = { kind: "text", id: string, title: string, bullets: string[] };
export type demoSlideType = { kind: "demo", id: string, claim: string, title: string, points: string[], prompt: string };
export type pipelineSlideType = { kind: "pipeline", id: string, title: string, stages: { label: string, detail: string }[], note?: string };
export type compareSideType = { label: string, points: string[] };
export type compareSlideType = { kind: "compare", id: string, title: string, before: compareSideType, after: compareSideType, note: string };
export type chunkingSlideType = { kind: "chunking", id: string, title: string, strategyNotes: { paragraph: string, window: string } };
export type embeddingMapSlideType = { kind: "embeddingMap", id: string, title: string, caption: string, modelNotes: Record<string, string> };
export type metricsSlideType = { kind: "metrics", id: string, title: string };
export type sourcesSlideType = { kind: "sources", id: string, title: string };
export type slideKindType = titleSlideType | textSlideType | demoSlideType | pipelineSlideType | chunkingSlideType | embeddingMapSlideType | compareSlideType | metricsSlideType | sourcesSlideType;
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
        kind: "text",
        id: "recap",
        title: "Onde estávamos",
        refs: ["rag"],
        bullets: [
            "Problema: o baixo letramento em saúde reduz a adesão a tratamentos e sobrecarrega os pronto-socorros.",
            "Proposta: um assistente de IA que responde apenas a partir de uma base de conhecimento confiável (RAG){ref:rag}.",
            "Escopo: obstetrícia, uma área com quadros bem catalogados e pacientes em geral saudáveis.",
            "Arquitetura: cinco pilares: base de dados, modelo, engenharia de prompt, verificação e interface.",
        ],
    },
    {
        kind: "text",
        id: "evolucao",
        title: "O que mudou desde a última etapa",
        refs: ["gemini-thinking"],
        bullets: [
            "Verificação: a segunda chamada ao modelo foi substituída pelo raciocínio nativo do Gemini{ref:gemini-thinking}.",
            "Modelo: provedor local (Ollama) ou Gemini, escolhido na inicialização.",
            "Interface: do terminal para um aplicativo web com documentos e citações.",
            "Base de conhecimento: 16 documentos, incluindo materiais do HU-USP.",
        ],
    },
    {
        kind: "chunking",
        id: "chunking",
        title: "Como a base é dividida em trechos",
        refs: ["rag"],
        strategyNotes: {
            paragraph: "Estratégia atual: cada parágrafo da base vira um trecho. Preserva o sentido e permite citar o parágrafo exato.",
            window: "Alternativa: agrupa parágrafos até 500 caracteres e divide parágrafos longos com 100 caracteres de sobreposição.",
        },
    },
    {
        kind: "embeddingMap",
        id: "embedding-mapa",
        title: "Do MiniLM ao Gemini Embedding",
        refs: ["minilm", "gemini-embedding", "gemini-embeddings-docs", "matryoshka"],
        caption: "Cada ponto é um trecho da base. Passe o mouse para destacar o documento. Projeção 2D (PCA): mostra proximidade entre trechos, não a qualidade da busca.",
        modelNotes: {
            minilm: "Antes: modelo local de 384 dimensões, treinado para frases em vários idiomas{ref:minilm}.",
            gemini: "Agora: 768 dimensões, com tipos de tarefa distintos para documento e pergunta{ref:gemini-embeddings-docs}, um corte do vetor completo (Matryoshka){ref:matryoshka}{ref:gemini-embedding}.",
        },
    },
    {
        kind: "pipeline",
        id: "pensamento",
        title: "O que é pensar antes de responder",
        refs: ["cot", "gemini-thinking"],
        stages: [
            { label: "Pergunta", detail: "A pergunta e os trechos recuperados chegam ao modelo" },
            { label: "Raciocínio", detail: "O modelo gera passos intermediários antes de responder{ref:cot}" },
            { label: "Resumo exibido", detail: "A API devolve um resumo do raciocínio, não os passos completos{ref:gemini-thinking}" },
            { label: "Resposta", detail: "Só então o modelo escreve a resposta com citações" },
        ],
        note: "O nível de raciocínio é configurável (minimal, low, medium, high): mais raciocínio, mais latência. A interface usa o nível medium.",
    },
    {
        kind: "compare",
        id: "pensamento-vs-verificacao",
        title: "Por que o raciocínio substitui a verificação",
        refs: ["self-refine", "self-correct", "cot"],
        before: {
            label: "Antes: gerar, criticar e refinar",
            points: [
                "Uma chamada gera a resposta.",
                "Chamadas extras criticam e refinam a resposta.",
                "Cada pergunta custa várias chamadas ao modelo.",
            ],
        },
        after: {
            label: "Agora: pensar e responder",
            points: [
                "Uma chamada: o modelo raciocina e responde{ref:cot}.",
                "O resumo do raciocínio fica visível ao usuário.",
                "Menos chamadas por pergunta.",
            ],
        },
        note: "A literatura mostra os dois lados: o refinamento iterativo melhora saídas em várias tarefas{ref:self-refine}, mas modelos nem sempre corrigem o próprio raciocínio sem feedback externo{ref:self-correct}. A fidelidade das respostas é medida na etapa de avaliação.",
    },
    {
        kind: "demo",
        id: "fundamentada",
        claim: "Afirmação 1",
        title: "Responde apenas com o que está na base",
        points: [
            "A busca recupera trechos da base de conhecimento.",
            "A resposta é escrita só com esses trechos.",
            "As fontes usadas aparecem abaixo da resposta.",
        ],
        prompt: "Quais são os sinais de alerta da pré-eclâmpsia?",
    },
    {
        kind: "demo",
        id: "raciocinio",
        claim: "Afirmação 2",
        title: "Raciocina antes de responder",
        points: [
            "Resumos do raciocínio chegam enquanto o modelo pensa.",
            "Perguntas ambíguas geram um pedido de esclarecimento.",
            "Substitui a antiga etapa de verificação com uma segunda chamada.",
        ],
        prompt: "Estou sentindo dor, o que pode ser?",
    },
    {
        kind: "demo",
        id: "rastreavel",
        claim: "Afirmação 3",
        title: "Cada afirmação aponta para a fonte",
        points: [
            "Marcadores numerados ligam a resposta ao trecho original.",
            "Clique em um marcador para abrir o documento.",
            "O parágrafo citado fica destacado.",
        ],
        prompt: "Como é feito o diagnóstico de diabetes gestacional?",
    },
    {
        kind: "demo",
        id: "limites",
        claim: "Afirmação 4",
        title: "Sabe quando não sabe",
        points: [
            "Sem informação na base, a resposta diz isso.",
            "Nenhuma fonte é exibida nesses casos.",
            "Sem diagnóstico e sem doses inventadas.",
        ],
        prompt: "Qual a dose de ibuprofeno para uma gestante de 30 semanas?",
    },
    {
        kind: "pipeline",
        id: "arquitetura",
        title: "Como a resposta é construída",
        stages: [
            { label: "Busca na base", detail: "Trechos relevantes da base de conhecimento" },
            { label: "Raciocínio", detail: "O modelo pensa antes de responder" },
            { label: "Resposta com citações", detail: "Marcadores ligam cada afirmação à fonte" },
            { label: "Limites", detail: "Sem dados na base, o assistente recusa e não cita fontes" },
        ],
    },
    {
        kind: "metrics",
        id: "numeros",
        title: "Avaliação com Ragas",
        refs: ["ragas"],
    },
    {
        kind: "text",
        id: "proximos-passos",
        title: "Limites e próximos passos",
        refs: ["ragas"],
        bullets: [
            "Medir a fidelidade das respostas à base com métricas Ragas{ref:ragas}.",
            "Ampliar e revisar a base de conhecimento.",
        ],
    },
    {
        kind: "sources",
        id: "fontes",
        title: "Fontes",
    },
];

export const stepCounts = slides.map((slide) => (slide.kind === "pipeline" ? slide.stages.length : 1));
