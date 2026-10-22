import { useEffect, useRef, useState } from "react";

const MAX_TEXTAREA_HEIGHT = 160;

export function ChatInput({ onSendMessage }: { onSendMessage: (message: string) => void }) {
    const [userMessage, setUserMessage] = useState("");
    const textareaRef = useRef<HTMLTextAreaElement | null>(null);
    const canSend = userMessage.trim().length > 0;

    useEffect(() => {
        const textarea = textareaRef.current;
        if (!textarea) return;

        textarea.style.height = "auto";
        textarea.style.height = `${Math.min(textarea.scrollHeight, MAX_TEXTAREA_HEIGHT)}px`;
    }, [userMessage]);

    const handleSend = () => {
        if (!canSend) return;
        onSendMessage(userMessage.trim());
        setUserMessage("");
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="w-full">
            <div className="[view-transition-name:composer] flex items-end gap-2 rounded-2xl border border-line bg-surface py-2 pl-4 pr-2 shadow-sm transition focus-within:border-primary focus-within:ring-4 focus-within:ring-primary/15">
                <textarea
                    ref={textareaRef}
                    rows={1}
                    value={userMessage}
                    onChange={(e) => setUserMessage(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Digite sua mensagem..."
                    className="max-h-40 grow resize-none bg-transparent py-1.5 text-ink outline-none placeholder:text-ink-muted/70"
                />
                <button
                    onClick={handleSend}
                    disabled={!canSend}
                    aria-label="Enviar mensagem"
                    className="flex size-9 shrink-0 items-center justify-center rounded-full bg-primary text-on-primary transition hover:bg-primary-hover active:scale-95 disabled:bg-line disabled:text-ink-muted"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="size-4">
                        <path d="M12 19V5" />
                        <path d="m5 12 7-7 7 7" />
                    </svg>
                </button>
            </div>
            <p className="mt-2 text-center text-xs text-ink-muted">
                Informação educativa. Não substitui a avaliação de um profissional de saúde.
            </p>
        </div>
    );
}
