import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";

import { paragraphSpanType, rehypeParagraphMarks } from "@/utils/rehypeParagraphMarks";
import { ScrollToParagraph } from "./scrollToParagraph";

export type documentType = { id: string, title: string, tags: string[], content: string, paragraph_spans: paragraphSpanType[] };

export function DocumentContent({ document, highlightedParagraph }: { document: documentType, highlightedParagraph: number | null }) {
    return (
        <div className="min-h-0 flex-1 overflow-y-auto">
            {highlightedParagraph !== null && <ScrollToParagraph index={highlightedParagraph} />}
            <article className="mx-auto w-full max-w-3xl px-6 pt-10 pb-16">
                <div className="mb-6 flex flex-wrap gap-2 text-sm">
                    {document.tags.map((tag) => (
                        <span key={tag} className="rounded-full border border-line bg-primary-soft px-3 py-1 text-primary-ink">
                            {tag.replaceAll("_", " ")}
                        </span>
                    ))}
                </div>
                <div className="answer-prose max-w-[68ch]">
                    <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]} rehypePlugins={[rehypeKatex, rehypeParagraphMarks(document.paragraph_spans)]}>
                        {document.content}
                    </ReactMarkdown>
                </div>
            </article>
        </div>
    );
}
