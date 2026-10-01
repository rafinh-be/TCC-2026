import { useEffect, useLayoutEffect, useRef, useState } from "react";

const MAX_TEXTAREA_HEIGHT = 120;
const GAP_BETWEEN_INPUT_AND_BUTTON = 10;

export function ChatInput({ onSendMessage }: { onSendMessage: (message: string) => void }) {
    const [userMessage, setUserMessage] = useState<string | null>(null);
    const [isMultiline, setIsMultiline] = useState(false);
    const wrapperRef = useRef<HTMLDivElement | null>(null);
    const textareaRef = useRef<HTMLTextAreaElement | null>(null);
    const buttonRef = useRef<HTMLButtonElement | null>(null);
    const measureRef = useRef<HTMLSpanElement | null>(null);
    const typableWidthRef = useRef<number | null>(null);

    const recalcTypableWidth = () => {
        const wrapper = wrapperRef.current;
        const button = buttonRef.current;
        if (!wrapper || !button) return;

        const wrapperStyle = getComputedStyle(wrapper);
        const horizontalPadding = parseFloat(wrapperStyle.paddingLeft) + parseFloat(wrapperStyle.paddingRight);
        typableWidthRef.current =
            wrapper.clientWidth - horizontalPadding - button.offsetWidth - GAP_BETWEEN_INPUT_AND_BUTTON;
    };

    useLayoutEffect(() => {
        recalcTypableWidth();
        window.addEventListener("resize", recalcTypableWidth);
        return () => window.removeEventListener("resize", recalcTypableWidth);
    }, []);

    useEffect(() => {
        const measure = measureRef.current;
        if (!measure || typableWidthRef.current === null) return;

        const text = userMessage || "";
        const hasNewline = text.includes("\n");
        measure.textContent = text;
        const textWidth = measure.scrollWidth;

        setIsMultiline(hasNewline || textWidth > typableWidthRef.current);
    }, [userMessage]);


    useEffect(() => {
        const textarea = textareaRef.current;
        if (!textarea) return;

        textarea.style.height = "auto";
        textarea.style.height = `${Math.min(textarea.scrollHeight, MAX_TEXTAREA_HEIGHT)}px`;
    }, [userMessage, isMultiline]);

    const handleSend = () => {
        onSendMessage(userMessage || "");
        setUserMessage("");
    };

    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setUserMessage(e.target.value);
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div style={{width: "100%", display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "center", paddingLeft: "10px", paddingRight: "10px", paddingBottom: "10px"}}>
            <div ref={wrapperRef} style={{width: "95%", display: "flex", flexDirection: isMultiline ? "column" : "row", alignItems: isMultiline ? "stretch" : "center", borderRadius: isMultiline ? "24px" : "9999px", borderColor: "#F0F0F0", borderWidth: "2px", borderStyle: "solid", backgroundColor: "#FCFCFC", paddingLeft: "20px", paddingRight: "10px", paddingTop: "6px", paddingBottom: "6px"}}>
                <div style={{position: "absolute", width: 0, height: 0, overflow: "hidden"}}>
                    <span ref={measureRef} style={{whiteSpace: "pre", fontFamily: "inherit", fontSize: "inherit"}} />
                </div>
                <textarea
                    ref={textareaRef}
                    onKeyDown={handleKeyDown}
                    rows={1}
                    style={{flexGrow: 1, flexShrink: 1, flexBasis: "auto", resize: "none", overflowY: "auto", maxHeight: `${MAX_TEXTAREA_HEIGHT}px`, boxSizing: "border-box", border: "none", outline: "none", backgroundColor: "transparent", padding: "4px", color: "black", fontFamily: "inherit", fontSize: "inherit"}}
                    value={userMessage || ""}
                    onChange={handleChange}
                    placeholder="Digite sua mensagem..."
                />
                <button
                    ref={buttonRef}
                    style={{padding: "10px 20px", borderRadius: "9999px", backgroundColor: "#cc3434", color: "white", alignSelf: isMultiline ? "flex-end" : "center", marginTop: isMultiline ? "6px" : "0"}}
                    onClick={handleSend}
                >
                    Enviar
                </button>
            </div>
        </div>
    );
}
