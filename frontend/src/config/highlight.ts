export type highlightAnimationType = "fade" | "marker";

export const HIGHLIGHT_ANIMATION: highlightAnimationType =
    process.env.NEXT_PUBLIC_HIGHLIGHT_ANIMATION === "marker" ? "marker" : "fade";
