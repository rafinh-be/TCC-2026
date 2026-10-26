import { splitRefs } from "@/utils/splitRefs";
import { referenceNumbering } from "./referenceNumbering";

export function RichText({ text }: { text: string }) {
    return (
        <>
            {splitRefs(text).map((part, index) =>
                part.kind === "text"
                    ? <span key={index}>{part.value}</span>
                    : <sup key={index} className="ml-0.5 font-medium text-primary">[{referenceNumbering.get(part.id) ?? "?"}]</sup>,
            )}
        </>
    );
}
