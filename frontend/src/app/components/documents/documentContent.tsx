import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export type documentType = { id: string, title: string, tags: string[], content: string };

export function DocumentContent({ document }: { document: documentType }) {
    return (
        <div className="min-h-0 flex-1 overflow-y-auto">
            <article className="mx-auto w-full max-w-3xl px-6 pt-10 pb-16">
                <div className="mb-6 flex flex-wrap gap-2 text-sm">
                    {document.tags.map((tag) => (
                        <span key={tag} className="rounded-full border border-line bg-primary-soft px-3 py-1 text-primary-ink">
                            {tag.replaceAll("_", " ")}
                        </span>
                    ))}
                </div>
                <div className="answer-prose max-w-[68ch]">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {document.content}
                    </ReactMarkdown>
                </div>
            </article>
        </div>
    );
}
