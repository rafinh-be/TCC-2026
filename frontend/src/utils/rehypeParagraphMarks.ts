export type paragraphSpanType = [number, number];

type hastNode = {
    type: string,
    tagName?: string,
    properties?: Record<string, unknown>,
    position?: { start: { offset?: number } },
    children?: hastNode[],
};

const BLOCK_TAGS = new Set(["p", "li", "ul", "ol", "blockquote", "pre", "table", "hr", "h1", "h2", "h3", "h4", "h5", "h6"]);

export const HIGHLIGHT_CLASS_NAME = "paragraph-highlight";

export function paragraphElementId(index: number) {
    return `trecho-${index}`;
}

function paragraphIndexAt(spans: paragraphSpanType[], offset: number) {
    return spans.findIndex(([start, end]) => offset >= start && offset < end);
}

export function rehypeParagraphMarks(spans: paragraphSpanType[]) {
    return () => (tree: hastNode) => {
        const identified = new Set<number>();

        const mark = (node: hastNode, parentIndex: number) => {
            let currentIndex = parentIndex;
            const offset = node.position?.start.offset;
            if (node.type === "element" && node.tagName && BLOCK_TAGS.has(node.tagName) && offset !== undefined) {
                const index = paragraphIndexAt(spans, offset);
                if (index !== -1 && index !== parentIndex) {
                    currentIndex = index;
                    const properties = node.properties ?? {};
                    properties["data-trecho"] = index;
                    if (!identified.has(index)) {
                        properties.id = paragraphElementId(index);
                        identified.add(index);
                    }
                    node.properties = properties;
                }
            }
            node.children?.forEach((child) => mark(child, currentIndex));
        };

        mark(tree, -1);
    };
}
