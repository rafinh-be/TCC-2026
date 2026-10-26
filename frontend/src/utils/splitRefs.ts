export type textPart = { kind: "text", value: string } | { kind: "ref", id: string };

const REFERENCE_PATTERN = /\{ref:([a-z0-9-]+)\}/;

export function splitRefs(text: string): textPart[] {
    return text.split(REFERENCE_PATTERN).flatMap((piece, index): textPart[] => {
        if (index % 2 === 1) return [{ kind: "ref", id: piece }];
        return piece ? [{ kind: "text", value: piece }] : [];
    });
}
