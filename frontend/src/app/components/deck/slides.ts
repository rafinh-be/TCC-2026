export type textSlideType = { kind: "text", id: string, title: string, bullets: string[] };
export type demoSlideType = { kind: "demo", id: string, claim: string, title: string, points: string[], prompt: string };
export type pipelineSlideType = { kind: "pipeline", id: string, title: string, stages: { label: string, detail: string }[] };
export type metricsSlideType = { kind: "metrics", id: string, title: string };
export type slideType = textSlideType | demoSlideType | pipelineSlideType | metricsSlideType;

export const slides: slideType[] = [
    {
        kind: "text",
        id: "problema",
        title: "Letramento em saúde na gestação",
        bullets: [
            "Pacientes com baixo letramento em saúde aderem menos aos tratamentos e sobrecarregam os pronto-socorros.",
            "Proposta: um assistente de IA que responde apenas a partir de uma base de conhecimento confiável.",
            "Cinco pilares: base de dados, modelo, engenharia de prompt, verificação e interface.",
        ],
    },
    {
        kind: "text",
        id: "evolucao",
        title: "O que mudou desde a última etapa",
        bullets: [
            "Verificação: a segunda chamada ao modelo foi substituída pelo raciocínio nativo do Gemini.",
            "Modelo: provedor local (Ollama) ou Gemini, escolhido na inicialização.",
            "Interface: do terminal para um aplicativo web com documentos e citações.",
            "Base de conhecimento: 16 documentos, incluindo materiais do HU-USP.",
        ],
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
    },
    {
        kind: "text",
        id: "proximos-passos",
        title: "Limites e próximos passos",
        bullets: [
            "Medir a fidelidade das respostas à base com métricas Ragas.",
            "Ampliar e revisar a base de conhecimento.",
        ],
    },
];

export const stepCounts = slides.map((slide) => (slide.kind === "pipeline" ? slide.stages.length : 1));
