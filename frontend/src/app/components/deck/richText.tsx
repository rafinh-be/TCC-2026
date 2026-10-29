import { splitRefs } from "@/utils/splitRefs";
import { referenceNumbering } from "./referenceNumbering";

export function RichText({ text, highlightModels = false }: { text: string, highlightModels?: boolean }) {
    return (
        <>
            {splitRefs(text).map((part, index) =>
                part.kind === "text"
                    ? <span key={index}>{highlightModels ? part.value.split(/(Ollama|Gemini)/g).map((word, wordIndex) => word === "Ollama" || word === "Gemini" ? <strong key={wordIndex} className="font-semibold text-ink">{word}</strong> : word) : part.value}</span>
                    : <sup key={index} className="ml-0.5 font-medium text-primary">[{referenceNumbering.get(part.id) ?? "?"}]</sup>,
            )}
        </>
    );
}
