import { useState } from "react";

export function HomeInput({ onSendMessage, disabled }: { onSendMessage: (message: string) => void, disabled: boolean }) {
    const [userMessage, setUserMessage] = useState("");

    const handleSend = () => {
        if (disabled || !userMessage.trim()) return;
        onSendMessage(userMessage.trim());
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter") {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="flex w-full items-center rounded-full border-2 border-chat-border bg-chat-bot py-1.5 pl-5 pr-2.5">
            <input
                type="text"
                value={userMessage}
                onChange={(e) => setUserMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={disabled}
                placeholder="Digite sua mensagem..."
                className="grow bg-transparent p-1 text-black outline-none"
            />
            <button
                onClick={handleSend}
                disabled={disabled}
                className="rounded-full bg-chat-user px-5 py-2.5 text-white"
            >
                Enviar
            </button>
        </div>
    );
}
