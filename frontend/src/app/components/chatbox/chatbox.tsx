import { useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { ChatInput } from "./chatInput";
import { MessageSources } from "./messageSources";
import { CitationLink } from "./citationLink";
import { LiveThinking, ThinkingSummary } from "./thinkingSummary";
import { citationType, linkCitations } from "@/utils/linkCitations";

export type sourceType = { title: string, chunk_ids: string[] };
export type messageType = { content: string, sender: "user" | "bot", sources?: sourceType[], citations?: citationType[], thinking?: string };

export function Chatbox({ messages, isProcessing, liveThinking = [], onSendMessage }: { messages: messageType[], isProcessing: boolean, liveThinking?: string[], onSendMessage: (message: string) => void }) {
    const bottomRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, isProcessing, liveThinking]);

    const chatItems : React.ReactNode[] = messages.map((message, index) => {
        if (message.sender == "user") {
            return(
                <div key={index} className="rise-in flex justify-end">
                    <div className="max-w-[80%] whitespace-pre-wrap rounded-2xl bg-primary-soft px-4 py-2.5 text-primary-ink">
                        {message.content}
                    </div>
                </div>
            )
        } else if (message.sender == "bot") {
            return(
                <div key={index} className="rise-in answer-prose max-w-[68ch]">
                    <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                            a: ({ href, children }) => href?.startsWith("/documentos/")
                                ? <CitationLink href={href} title="Abrir trecho na fonte">{children}</CitationLink>
                                : <a href={href}>{children}</a>,
                        }}
                    >
                        {linkCitations(message.content, message.citations ?? [])}
                    </ReactMarkdown>
                    <MessageSources sources={message.sources ?? []} />
                    {message.thinking && <ThinkingSummary thinking={message.thinking} />}
                </div>
            )
        }
    })

    const waitingIndicator = isProcessing && (liveThinking.length > 0 ? <LiveThinking blocks={liveThinking} /> : (
        <div className="rise-in flex items-center gap-3 text-sm text-ink-muted">
            <div className="flex items-center gap-1.5">
                <span className="typing-dot" />
                <span className="typing-dot" style={{animationDelay: "0.2s"}} />
                <span className="typing-dot" style={{animationDelay: "0.4s"}} />
            </div>
            <span>Consultando a base de conhecimento</span>
        </div>
    ));

    return (
        <div className="flex min-h-0 flex-1 flex-col">
            <div className="flex min-h-0 flex-1 flex-col overflow-y-auto">
                <div className="mx-auto flex w-full max-w-3xl flex-1 flex-col px-6">
                    <div className="flex flex-col gap-8 pt-10 pb-8">
                        {chatItems}
                        {waitingIndicator}
                    </div>
                    <div className="sticky bottom-0 mt-auto bg-linear-to-t from-page from-75% to-transparent pt-6 pb-4">
                        <ChatInput onSendMessage={onSendMessage} />
                    </div>
                    <div ref={bottomRef} />
                </div>
            </div>
        </div>
    );
}
