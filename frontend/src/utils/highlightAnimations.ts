import { HIGHLIGHT_CLASS_NAME } from "@/utils/rehypeParagraphMarks";

const MARKER_SPEED_PX_PER_MS = 0.7;
const LINE_TOLERANCE_PX = 2;
const MARKER_OVERFLOW_PX = 4;

type lineBoxType = { left: number, right: number, top: number, bottom: number };

function ownTextRects(element: Element, paragraphIndex: string) {
    const rects: DOMRect[] = [];
    const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
    const range = document.createRange();
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
        if (!node.textContent?.trim()) continue;
        if (node.parentElement?.closest("[data-trecho]")?.getAttribute("data-trecho") !== paragraphIndex) continue;
        range.selectNodeContents(node);
        rects.push(...Array.from(range.getClientRects()).filter((rect) => rect.width > 0 && rect.height > 0));
    }
    return rects;
}

function mergeIntoLines(rects: DOMRect[]) {
    const lines: lineBoxType[] = [];
    [...rects].sort((a, b) => a.top - b.top || a.left - b.left).forEach((rect) => {
        const line = lines.find((candidate) => rect.top < candidate.bottom - LINE_TOLERANCE_PX && rect.bottom > candidate.top + LINE_TOLERANCE_PX);
        if (!line) {
            lines.push({ left: rect.left, right: rect.right, top: rect.top, bottom: rect.bottom });
            return;
        }
        line.left = Math.min(line.left, rect.left);
        line.right = Math.max(line.right, rect.right);
        line.top = Math.min(line.top, rect.top);
        line.bottom = Math.max(line.bottom, rect.bottom);
    });
    return lines;
}

export function fadeHighlight(elements: Element[]) {
    elements.forEach((element) => element.classList.add(HIGHLIGHT_CLASS_NAME));
    return () => elements.forEach((element) => element.classList.remove(HIGHLIGHT_CLASS_NAME));
}

export function markerHighlight(elements: Element[], container: HTMLElement, paragraphIndex: number, animate: boolean) {
    const overlay = document.createElement("div");
    overlay.className = "marker-overlay";
    container.append(overlay);

    const containerRect = container.getBoundingClientRect();
    let delay = 0;
    elements.forEach((element) => {
        mergeIntoLines(ownTextRects(element, String(paragraphIndex))).forEach((line) => {
            const width = line.right - line.left + MARKER_OVERFLOW_PX * 2;
            const bar = document.createElement("div");
            bar.className = "marker-bar";
            bar.style.left = `${line.left - containerRect.left - MARKER_OVERFLOW_PX}px`;
            bar.style.top = `${line.top - containerRect.top}px`;
            bar.style.width = `${width}px`;
            bar.style.height = `${line.bottom - line.top}px`;
            overlay.append(bar);
            if (!animate) return;
            const duration = width / MARKER_SPEED_PX_PER_MS;
            bar.animate([{ transform: "scaleX(0)" }, { transform: "scaleX(1)" }], { duration, delay, easing: "ease-in-out", fill: "backwards" });
            delay += duration;
        });
    });

    return () => overlay.remove();
}
