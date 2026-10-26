export type deckPosition = { slide: number, step: number };
export type deckAction = "next" | "previous" | "first" | "last";

const KEY_ACTIONS = new Map<string, deckAction>([
    ["ArrowRight", "next"],
    [" ", "next"],
    ["PageDown", "next"],
    ["ArrowLeft", "previous"],
    ["PageUp", "previous"],
    ["Home", "first"],
    ["End", "last"],
]);

const TYPING_TAGS = ["INPUT", "TEXTAREA", "SELECT"];
const CLICKABLE_TAGS = ["BUTTON", "A"];

export function actionForKey(key: string): deckAction | null {
    return KEY_ACTIONS.get(key) ?? null;
}

export function ignoresKey(key: string, target: EventTarget | null) {
    if (!(target instanceof HTMLElement)) return false;
    if (target.isContentEditable || TYPING_TAGS.includes(target.tagName)) return true;
    return key === " " && CLICKABLE_TAGS.includes(target.tagName);
}

export function advance(position: deckPosition, action: deckAction, stepCounts: number[]): deckPosition {
    const lastSlide = stepCounts.length - 1;
    const { slide, step } = position;

    if (action === "first") return { slide: 0, step: 0 };
    if (action === "last") return { slide: lastSlide, step: 0 };
    if (action === "next") {
        if (step < stepCounts[slide] - 1) return { slide, step: step + 1 };
        return slide < lastSlide ? { slide: slide + 1, step: 0 } : position;
    }
    if (step > 0) return { slide, step: step - 1 };
    return slide > 0 ? { slide: slide - 1, step: stepCounts[slide - 1] - 1 } : position;
}

export function slideFromHash(hash: string, slideCount: number) {
    const number = /^#(\d+)$/.exec(hash)?.[1];
    if (number === undefined) return 0;
    return Math.min(Math.max(Number(number) - 1, 0), slideCount - 1);
}
