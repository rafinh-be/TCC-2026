import { useState } from "react";

export function HomeInput({ onSendMessage, disabled }: { onSendMessage: (message: string) => void, disabled: boolean }) {
    const [userMessage, setUserMessage] = useState("");
    const canSend = !disabled && userMessage.trim().length > 0;

    const handleSend = () => {
        if (!canSend) return;
        onSendMessage(userMessage.trim());
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter") {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="flex w-full items-center gap-2 rounded-2xl border border-line bg-surface py-2 pl-4 pr-2 shadow-sm transition focus-within:border-primary focus-within:ring-4 focus-within:ring-primary/15">
            <input
                type="text"
                value={userMessage}
                onChange={(e) => setUserMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={disabled}
                placeholder="Digite sua mensagem..."
                className="grow bg-transparent py-1.5 text-ink outline-none placeholder:text-ink-muted/70"
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
    );
}
