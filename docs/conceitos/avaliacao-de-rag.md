# Avaliação de RAG

Criado em: 2026-10-18 · Atualizado em: 2026-10-18

## O que é

Avaliar RAG significa verificar se o sistema encontra as evidências necessárias e produz respostas adequadas a partir delas. Uma resposta fluida não comprova que a busca funcionou ou que as afirmações estão respaldadas.

Convém separar três perguntas:

1. **Recuperação:** os trechos necessários foram encontrados e bem posicionados?
2. **Geração:** a resposta atende à pergunta e preserva o conteúdo das evidências?
3. **Abstenção:** o sistema recusa quando falta informação e responde quando ela existe?

Essa separação ajuda a localizar o problema. Se a evidência existe na base mas não chega ao modelo, a falha está na recuperação. Se chega e é ignorada ou distorcida, a falha está na geração.

## O que já existe no TCC

[gerar_testset.py](../../gerar_testset.py) usa o Gemini para produzir perguntas e respostas sintéticas e exportá-las para CSV e JSON. O esquema `SyntheticQA` é validado com Pydantic.

Para cada documento processado, o script solicita uma pergunta simples, uma de raciocínio e uma sem resposta no documento. Os registros incluem `question`, `ground_truth`, `context`, `fonte_documento` e `expected_refusal`.

Esse script **gera casos de teste**. Ele não executa o chat para cada pergunta nem calcula métricas. O projeto ainda não possui uma rotina automática completa de avaliação do RAG.

## Limitações do conjunto sintético atual

- A origem padrão é `my_notes`, enquanto a indexação do chat usa `database/data_files`. É necessário conferir se as evidências de referência existem na base efetivamente consultada.
- A execução padrão processa no máximo três documentos. Isso não representa toda a cobertura temática do projeto.
- O prompt de geração recebe até 2.500 caracteres, mas o campo `context` exportado guarda até 1.500. Uma resposta de referência pode depender de uma passagem ausente desse campo.
- Uma pergunta sem resposta em um documento pode ser respondida por outro documento da base. O rótulo de recusa precisa ser conferido contra a base inteira.
- O gerador pede casos de diagnóstico/conduta, mas o assistente é instruído a não formular diagnósticos. As referências precisam respeitar o comportamento esperado do produto.
- Perguntas e respostas produzidas pelo modelo precisam de revisão. O nome `ground_truth` não garante que a referência esteja correta.

## Medidas úteis

As métricas abaixo são sugestões para uma avaliação futura, não resultados já calculados no projeto.

| Aspecto | Medida | O que observar |
|---|---|---|
| Recuperação | Recall@k | Fração das evidências relevantes de referência encontrada entre os primeiros k resultados. |
| Recuperação | Precision@k | Fração dos primeiros k resultados considerada relevante. |
| Ranking | MRR | Média do inverso da posição do primeiro resultado relevante; consultas sem acerto contribuem com zero. |
| Geração | Fidelidade ao contexto | Se as afirmações da resposta são sustentadas pelos trechos recuperados. |
| Geração | Correção e completude | Se a resposta corresponde à referência revisada e cobre o que foi perguntado. |
| Abstenção | Recusa correta | Entre perguntas sem resposta na base, quantas receberam a recusa esperada. |
| Abstenção | Recusa indevida | Entre perguntas respondíveis, quantas foram recusadas. |

Para Recall@k e Precision@k, é preciso definir a unidade de relevância: documento, chunk ou passagem de evidência. Usar documentos como unidade pode ocultar a recuperação de um trecho errado do documento certo. A sobreposição entre chunks também exige cuidado para não contar a mesma evidência várias vezes.

Exemplo hipotético: se uma pergunta exige duas passagens anotadas e ambas aparecem entre dez resultados, o Recall@10 é 1. Se apenas essas duas são relevantes, a Precision@10 é 0,2. Isso mede recuperação; não comprova que a resposta gerada esteja correta.

O [catálogo de métricas do Ragas](https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/) apresenta medidas como fidelidade, precisão e recall de contexto. A definição operacional e os dados exigidos variam por métrica; implementar uma contagem simples não equivale automaticamente à métrica da biblioteca.

## Um procedimento possível para o TCC

1. Selecionar perguntas respondíveis, não respondíveis, ambíguas e com continuação de conversa; revisar as referências e marcar as evidências na base completa.
2. Registrar a versão dos documentos, os modelos, os prompts, o tamanho dos chunks e os parâmetros de recuperação.
3. Executar cada pergunta com histórico controlado, salvando trechos recuperados, ordem, resposta e tempo de execução.
4. Avaliar recuperação, geração e abstenção separadamente, usando revisão humana para os critérios que exigem julgamento.
5. Comparar configurações no mesmo conjunto de perguntas e reservar um conjunto separado para avaliação final, evitando ajustar o sistema às perguntas usadas para medir o resultado.

Uma LLM pode auxiliar na avaliação, mas sua nota também pode falhar. A revisão especializada é particularmente relevante para conferir referências e critérios clínicos do TCC. Nenhum resultado de validação clínica foi produzido por esta documentação.

## Conceitos relacionados

- [RAG](rag.md).
- [Busca híbrida](busca-hibrida.md).
- [Ranking e RRF](ranking-e-rrf.md).
- [Grounding e abstenção](grounding-e-abstencao.md).
