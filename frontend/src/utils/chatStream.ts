import type { sourceType } from "@/app/components/chatbox/chatbox";
import type { citationType } from "@/utils/linkCitations";

export type streamEvent =
    | { type: "thinking", text: string }
    | { type: "final", answer: { message: { content: string, thinking?: string } }, sources: sourceType[], citations: citationType[] }
    | { type: "error", message: string };

export function parseStreamLines(buffer: string) {
    const lines = buffer.split("\n");
    const rest = lines.pop() ?? "";
    const events = lines.filter((line) => line.trim()).map((line) => JSON.parse(line) as streamEvent);
    return { events, rest };
}

export async function readChatStream(response: Response, onEvent: (event: streamEvent) => void) {
    if (!response.body) throw new Error("Resposta sem corpo");
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
        const { done, value } = await reader.read();
        buffer += decoder.decode(value, { stream: !done });
        const { events, rest } = parseStreamLines(done ? buffer + "\n" : buffer);
        buffer = rest;
        events.forEach(onEvent);
        if (done) break;
    }
}
