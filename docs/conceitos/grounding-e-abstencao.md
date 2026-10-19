# Grounding e abstenção

Criado em: 2026-10-18 · Atualizado em: 2026-10-18

## O que são

**Grounding**, ou ancoragem, é fundamentar as afirmações da resposta nas evidências fornecidas. Neste projeto, a evidência esperada são os trechos recuperados da base local.

**Abstenção** é deixar de responder ao conteúdo solicitado quando faltam evidências suficientes. A recusa evita preencher lacunas com informações que não estejam respaldadas pela base.

São decisões complementares: primeiro é necessário identificar o que o contexto permite afirmar; depois, responder dentro desses limites, pedir esclarecimento ou recusar.

## Como usamos no TCC

[gemini_interaction.py](../../backend/gemini_interaction.py) monta a entrada do modelo com as instruções de sistema, o histórico, os trechos em `<contexto_local>`, as fontes e a pergunta atual.

As instruções de [config_agent.md](../../backend/config_agent.md) prevalecem sobre o prompt de sistema de `config.ini` quando esse arquivo existe. Elas exigem paráfrase das evidências, preservação de números e proíbem formular diagnósticos com base nos sintomas da conversa.

Quando não há informação suficiente, a resposta prevista é:

> Não encontrei dados ou critérios suficientes para esta conduta específica na minha base local de evidências.

Se não há contexto recuperado, a montagem do payload também inclui essa orientação. Para perguntas amplas ou ambíguas com informações relacionadas, o prompt permite apresentar apenas o que estiver respaldado e fazer uma pergunta breve de esclarecimento.

## Exemplo concreto

Considere **“O que vocês orientam sobre pré-parto?”**. Se os trechos contiverem informações pertinentes sobre preparação para o parto, a resposta pode abordar esse conteúdo e perguntar qual aspecto interessa à paciente.

Trechos sobre parto prematuro ou pós-parto não sustentam automaticamente essa resposta. Compartilhar palavras ou estar próximo no espaço vetorial não torna os assuntos equivalentes.

Se a pergunta pedir um valor que não consta nos trechos, o modelo não deve estimá-lo. Esse exemplo descreve o comportamento desejado; não comprova que todas as respostas geradas o seguem.

## O que o código garante e o que depende do modelo

O código entrega contexto e instruções ao Gemini. A decisão sobre suficiência da evidência permanece com o modelo; não existe um verificador independente que confronte cada afirmação da resposta com os trechos.

Os prompts de crítica e refinamento são carregados em [main.py](../../backend/main.py), mas não são executados no fluxo atual de `process_chat()`. Sua presença na configuração não constitui uma revisão automática ativa.

Enviar nomes de fontes também não cria uma ligação verificável entre cada afirmação e um trecho. Além disso, uma resposta fiel a um documento incorreto pode continuar incorreta: ancoragem e qualidade da fonte precisam ser avaliadas separadamente.

As tags `<contexto_local>` delimitam o texto para o modelo; não funcionam como uma barreira de segurança por si mesmas. A instrução de ignorar comandos presentes no material recuperado é uma regra do prompt, sujeita a falhas.

## Como avaliar esse comportamento

É necessário observar tanto respostas sem respaldo quanto recusas indevidas. Um sistema que recusa tudo evita algumas extrapolações, mas deixa de ajudar mesmo quando há evidência suficiente.

A avaliação deve incluir perguntas respondíveis, perguntas sem resposta na base e perguntas ambíguas. Veja [avaliação de RAG](avaliacao-de-rag.md).

## Conceitos relacionados

- [RAG](rag.md).
- [Busca híbrida](busca-hibrida.md).
- [Ranking e RRF](ranking-e-rrf.md).
