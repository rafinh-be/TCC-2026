export function referenceNumbers(slides: { refs?: string[] }[]): Map<string, number> {
    const numbers = new Map<string, number>();
    for (const slide of slides) {
        for (const id of slide.refs ?? []) {
            if (!numbers.has(id)) numbers.set(id, numbers.size + 1);
        }
    }
    return numbers;
}
