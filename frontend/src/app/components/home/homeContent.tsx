"use client";
import { useRef, useState } from "react";
import { useRouter } from "next/navigation";

import { HomeInput } from "./homeInput";

const PENDING_MESSAGE_KEY = "pendingMessage";
const LEAVE_DURATION_MS = 600;
const CHAT_INPUT_BOTTOM_OFFSET = 40;
const CHAT_COLUMN_MAX_WIDTH = 768;
const CHAT_COLUMN_HORIZONTAL_PADDING = 48;
const HOME_INPUT_MAX_WIDTH = 576;

const suggestions = [
  "O que é normal no primeiro trimestre?",
  "Quais sinais indicam trabalho de parto?",
  "Como é a recuperação no pós-parto?",
];

const steps = [
  {
    title: "Você pergunta",
    description: "Escreva sua dúvida sobre gestação, parto, pós-parto ou saúde ginecológica, com as suas palavras.",
  },
  {
    title: "Buscamos na base",
    description: "O sistema localiza os trechos mais relevantes de uma base de conhecimento revisada, mantida localmente.",
  },
  {
    title: "Você recebe a resposta",
    description: "A resposta é escrita apenas com o que foi encontrado, e as fontes consultadas ficam registradas.",
  },
];

const principles = [
  {
    title: "Baseado em fontes",
    description: "Responde somente a partir do material da base. Se a informação não existe, o assistente diz isso.",
  },
  {
    title: "Sem diagnósticos",
    description: "Oferece informação educativa. Não diagnostica, não prescreve e não sugere doses de medicamentos.",
  },
  {
    title: "Privacidade",
    description: "O modelo de linguagem e a base de conhecimento são executados localmente, sem depender de serviços externos.",
  },
];

export function HomeContent() {
  const router = useRouter();
  const containerRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLDivElement | null>(null);
  const [isLeaving, setIsLeaving] = useState(false);
  const [inputShift, setInputShift] = useState(0);
  const [inputMaxWidth, setInputMaxWidth] = useState(HOME_INPUT_MAX_WIDTH);

  const handleSend = (message: string) => {
    const container = containerRef.current;
    const input = inputRef.current;
    if (container && input) {
      const targetBottom = container.getBoundingClientRect().bottom - CHAT_INPUT_BOTTOM_OFFSET;
      setInputShift(targetBottom - input.getBoundingClientRect().bottom);
      setInputMaxWidth(Math.min(container.clientWidth, CHAT_COLUMN_MAX_WIDTH) - CHAT_COLUMN_HORIZONTAL_PADDING);
    }
    setIsLeaving(true);
    sessionStorage.setItem(PENDING_MESSAGE_KEY, message);
    setTimeout(() => router.push("/chat"), LEAVE_DURATION_MS);
  };

  const fadeClasses = `transition-all ease-out duration-500 ${isLeaving ? "-translate-y-4 opacity-0" : ""}`;

  return (
    <div ref={containerRef} className={`flex-1 bg-page ${isLeaving ? "overflow-hidden" : "overflow-y-auto"}`}>
      <div className="mx-auto flex max-w-3xl flex-col gap-24 px-6 pb-16">
        <section className="flex min-h-[70vh] flex-col items-center justify-center gap-5 text-center">
          <h1 className={`${fadeClasses} text-3xl font-semibold leading-tight tracking-tight text-ink sm:text-4xl`}>
            Assistente Virtual em Obstetrícia
          </h1>
          <p className={`${fadeClasses} max-w-xl leading-relaxed text-ink-muted`}>
            Esclareça dúvidas sobre gestação, parto e pós-parto com respostas baseadas em uma base de conhecimento confiável.
          </p>
          <div
            ref={inputRef}
            className="mt-4 w-full transition-all ease-out duration-500"
            style={{ transform: `translateY(${inputShift}px)`, maxWidth: `${inputMaxWidth}px` }}
          >
            <HomeInput onSendMessage={handleSend} disabled={isLeaving} />
          </div>
          <div className={`${fadeClasses} flex flex-wrap justify-center gap-2`}>
            {suggestions.map((suggestion) => (
              <button
                key={suggestion}
                onClick={() => handleSend(suggestion)}
                disabled={isLeaving}
                className="rounded-full border border-line bg-surface px-4 py-2 text-sm text-ink-muted transition hover:border-primary/40 hover:bg-primary-soft hover:text-primary-ink active:scale-[0.98]"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </section>

        <section className={`${fadeClasses} flex flex-col gap-5`}>
          <h2 className="text-xs font-medium uppercase tracking-[0.18em] text-ink-muted">Como funciona</h2>
          <ol className="grid gap-8 sm:grid-cols-3">
            {steps.map((step, index) => (
              <li key={step.title} className="flex flex-col gap-1.5">
                <span className="text-xs font-medium text-primary">{String(index + 1).padStart(2, "0")}</span>
                <h3 className="font-medium text-ink">{step.title}</h3>
                <p className="text-sm leading-relaxed text-ink-muted">{step.description}</p>
              </li>
            ))}
          </ol>
        </section>

        <section className={`${fadeClasses} flex flex-col gap-5`}>
          <h2 className="text-xs font-medium uppercase tracking-[0.18em] text-ink-muted">Princípios</h2>
          <div className="grid gap-8 sm:grid-cols-3">
            {principles.map((principle) => (
              <div key={principle.title} className="flex flex-col gap-1.5 border-t border-line pt-4">
                <h3 className="font-medium text-ink">{principle.title}</h3>
                <p className="text-sm leading-relaxed text-ink-muted">{principle.description}</p>
              </div>
            ))}
          </div>
        </section>

        <footer className={`${fadeClasses} rounded-2xl bg-alert-soft px-5 py-4 text-sm leading-relaxed text-alert-ink`}>
          Este assistente não substitui a avaliação de um profissional de saúde. Em caso de sintomas, urgência ou
          dúvidas sobre tratamento, procure atendimento médico.
        </footer>
      </div>
    </div>
  );
}
