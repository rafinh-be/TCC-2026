"use client";
import { useRef, useState } from "react";
import { useRouter } from "next/navigation";

import { HomeInput } from "./homeInput";

const PENDING_MESSAGE_KEY = "pendingMessage";
const LEAVE_DURATION_MS = 600;
const CHAT_INPUT_BOTTOM_OFFSET = 10;
const CHAT_INPUT_WIDTH_RATIO = 0.85 * 0.9;
const CHAT_INPUT_HORIZONTAL_PADDING = 20;
const HOME_INPUT_MAX_WIDTH = 576;

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
      setInputMaxWidth(container.clientWidth * CHAT_INPUT_WIDTH_RATIO - CHAT_INPUT_HORIZONTAL_PADDING);
    }
    setIsLeaving(true);
    sessionStorage.setItem(PENDING_MESSAGE_KEY, message);
    setTimeout(() => router.push("/chat"), LEAVE_DURATION_MS);
  };

  const fadeClasses = `transition-all ease-in-out duration-500 ${isLeaving ? "-translate-y-6 opacity-0" : ""}`;

  return (
    <div ref={containerRef} className={`flex-1 bg-page ${isLeaving ? "overflow-hidden" : "overflow-y-auto"}`}>
      <div className="mx-auto flex max-w-4xl flex-col gap-20 px-6 py-16">
        <section className="flex min-h-[60vh] flex-col items-center justify-center gap-6 text-center">
          <h1 className={`${fadeClasses} text-4xl font-semibold leading-tight tracking-tight text-neutral-900 sm:text-5xl`}>
            Assistente Virtual em Obstetrícia
          </h1>
          <p className={`${fadeClasses} max-w-2xl text-lg leading-relaxed text-neutral-600`}>
            Um assistente que esclarece dúvidas de pacientes com linguagem simples, usando exclusivamente
            conteúdo de uma base de conhecimento confiável.
          </p>
          <p className={`${fadeClasses} mt-6 text-sm text-neutral-500`}>
            Tem alguma dúvida? Escreva abaixo para iniciar a conversa.
          </p>
          <div
            ref={inputRef}
            className="w-full transition-all ease-in-out duration-500"
            style={{ transform: `translateY(${inputShift}px)`, maxWidth: `${inputMaxWidth}px` }}
          >
            <HomeInput onSendMessage={handleSend} disabled={isLeaving} />
          </div>
        </section>

        <section className={`${fadeClasses} flex flex-col gap-8`}>
          <h2 className="text-sm font-medium uppercase tracking-[0.2em] text-neutral-400">Como funciona</h2>
          <ol className="grid gap-px overflow-hidden rounded-xl border border-chat-border bg-chat-border sm:grid-cols-3">
            {steps.map((step, index) => (
              <li key={step.title} className="flex flex-col gap-3 bg-page p-6">
                <span className="text-sm font-medium text-chat-user">{String(index + 1).padStart(2, "0")}</span>
                <h3 className="text-lg font-semibold text-neutral-900">{step.title}</h3>
                <p className="text-sm leading-relaxed text-neutral-600">{step.description}</p>
              </li>
            ))}
          </ol>
        </section>

        <section className={`${fadeClasses} flex flex-col gap-8`}>
          <h2 className="text-sm font-medium uppercase tracking-[0.2em] text-neutral-400">Princípios</h2>
          <div className="grid gap-8 sm:grid-cols-3">
            {principles.map((principle) => (
              <div key={principle.title} className="flex flex-col gap-2 border-t-2 border-chat-user pt-4">
                <h3 className="text-base font-semibold text-neutral-900">{principle.title}</h3>
                <p className="text-sm leading-relaxed text-neutral-600">{principle.description}</p>
              </div>
            ))}
          </div>
        </section>

        <footer className={`${fadeClasses} rounded-xl bg-chat-bot p-6 text-sm leading-relaxed text-neutral-500 ring-1 ring-chat-border`}>
          Este assistente não substitui a avaliação de um profissional de saúde. Em caso de sintomas, urgência ou
          dúvidas sobre tratamento, procure atendimento médico.
        </footer>
      </div>
    </div>
  );
}
