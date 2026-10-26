export type referenceType = { short: string, citation: string, url: string };

export const references: Record<string, referenceType> = {
    rag: {
        short: "Lewis et al., 2020",
        citation: "LEWIS, P. et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS, 2020.",
        url: "https://arxiv.org/abs/2005.11401",
    },
    cot: {
        short: "Wei et al., 2022",
        citation: "WEI, J. et al. Chain-of-Thought Prompting Elicits Reasoning in Large Language Models. NeurIPS, 2022.",
        url: "https://arxiv.org/abs/2201.11903",
    },
    "self-refine": {
        short: "Madaan et al., 2023",
        citation: "MADAAN, A. et al. Self-Refine: Iterative Refinement with Self-Feedback. NeurIPS, 2023.",
        url: "https://arxiv.org/abs/2303.17651",
    },
    "self-correct": {
        short: "Huang et al., 2024",
        citation: "HUANG, J. et al. Large Language Models Cannot Self-Correct Reasoning Yet. ICLR, 2024.",
        url: "https://arxiv.org/abs/2310.01798",
    },
    minilm: {
        short: "Reimers e Gurevych, 2020",
        citation: "REIMERS, N.; GUREVYCH, I. Making Monolingual Sentence Embeddings Multilingual using Knowledge Distillation. EMNLP, 2020.",
        url: "https://arxiv.org/abs/2004.09813",
    },
    "gemini-embedding": {
        short: "Lee et al., 2025",
        citation: "LEE, J. et al. Gemini Embedding: Generalizable Embeddings from Gemini. arXiv:2503.07891, 2025.",
        url: "https://arxiv.org/abs/2503.07891",
    },
    matryoshka: {
        short: "Kusupati et al., 2022",
        citation: "KUSUPATI, A. et al. Matryoshka Representation Learning. arXiv:2205.13147, 2022.",
        url: "https://arxiv.org/abs/2205.13147",
    },
    ragas: {
        short: "Es et al., 2024",
        citation: "ES, S. et al. Ragas: Automated Evaluation of Retrieval Augmented Generation. EACL (System Demonstrations), 2024.",
        url: "https://arxiv.org/abs/2309.15217",
    },
    "gemini-thinking": {
        short: "Google, Gemini thinking",
        citation: "GOOGLE. Gemini thinking. Gemini API documentation.",
        url: "https://ai.google.dev/gemini-api/docs/thinking",
    },
    "gemini-embeddings-docs": {
        short: "Google, Gemini embeddings",
        citation: "GOOGLE. Embeddings. Gemini API documentation.",
        url: "https://ai.google.dev/gemini-api/docs/embeddings",
    },
    "lancedb-hybrid": {
        short: "LanceDB, busca híbrida",
        citation: "LANCEDB. Hybrid Search. LanceDB documentation.",
        url: "https://docs.lancedb.com/search/hybrid-search",
    },
};
