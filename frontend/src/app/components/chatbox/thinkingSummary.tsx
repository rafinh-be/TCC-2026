import ReactMarkdown from "react-markdown";

export function LiveThinking({ blocks }: { blocks: string[] }) {
    return (
        <div className="flex flex-col gap-1.5">
            <div className="flex items-center gap-3 text-sm text-ink-muted">
                <div className="flex items-center gap-1.5">
                    <span className="typing-dot" />
                    <span className="typing-dot" style={{animationDelay: "0.2s"}} />
                    <span className="typing-dot" style={{animationDelay: "0.4s"}} />
                </div>
                <span>Raciocinando</span>
            </div>
            <div className="answer-prose max-w-[68ch] border-l-2 border-line pl-4 text-sm text-ink-muted">
                {blocks.map((block, index) => (
                    <div key={index} className="rise-in">
                        <ReactMarkdown>{block}</ReactMarkdown>
                    </div>
                ))}
            </div>
        </div>
    );
}

export function ThinkingSummary({ thinking }: { thinking: string }) {
    return (
        <details className="mt-3 text-sm text-ink-muted">
            <summary className="cursor-pointer select-none hover:text-ink">Ver raciocínio</summary>
            <div className="answer-prose mt-2 border-l-2 border-line pl-4">
                <ReactMarkdown>{thinking}</ReactMarkdown>
            </div>
        </details>
    );
}
