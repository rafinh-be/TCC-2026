import { useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { ChatInput } from "./chatInput";

export type messageType = { content: string, sender: "user" | "bot" };

export function Chatbox({ messages, isProcessing, onSendMessage }: { messages: messageType[], isProcessing: boolean, onSendMessage: (message: string) => void }) {
    const chatItems : React.ReactNode[] = [];
    const bottomRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    messages.forEach((message, index) => {
        const isWaitingForAnswer = isProcessing && index === messages.length - 1 && message.sender == "bot";

        if (isWaitingForAnswer) {
            chatItems.push(
                <div className="chat chat-start">
                    <div className="chat-header text-sm opacity-70 mb-1">
                        {message.content}
                    </div>
                    <div className="chat-bubble rounded-3xl! before:hidden! bg-chat-bot text-black border-2 border-chat-border flex items-center gap-1.5 h-10">
                        <span className="typing-dot" />
                        <span className="typing-dot" style={{animationDelay: "0.25s"}} />
                        <span className="typing-dot" style={{animationDelay: "0.5s"}} />
                    </div>
                </div>
            )
        } else if (message.sender == "user") {
            chatItems.push(
                <div className="chat chat-end">
                    <div className="chat-bubble rounded-3xl! before:hidden! bg-chat-user text-white border-2 border-chat-user max-w-[80%]">
                        {message.content}
                    </div>
                </div>
            )
        } else if (message.sender == "bot") {
            chatItems.push(
                <div className="chat chat-start">
                    <div className="chat-bubble rounded-3xl! before:hidden! bg-chat-bot text-black border-2 border-chat-border prose prose-sm prose-strong:text-black max-w-[80%]">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {message.content}
                        </ReactMarkdown>
                    </div>
                </div>
            )
        }
    })
    
    /*
    useEffect(() => {
        if (isProcessing) {
    }, [isProcessing])*/

    return (
        <div style={{display: "flex", flexDirection: "column", height: "100%"}}>
            <div style={{flexGrow: 1, overflowY: "auto"}}>
                {chatItems}
                <div ref={bottomRef} />
            </div>
            <ChatInput onSendMessage={onSendMessage} />
        </div>
    );
}