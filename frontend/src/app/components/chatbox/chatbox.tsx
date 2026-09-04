import { useState } from "react";

export type messageType = { content: string, sender: "user" | "bot" };

export function Chatbox({ messages, isProcessing, onSendMessage }: { messages: messageType[], isProcessing: boolean, onSendMessage: (message: string) => void }) {
    const chatItems : React.ReactNode[] = [];
    const [userMessage, setUserMessage] = useState<string | null>(null);

    messages.forEach((message) => {
        if (message.sender == "user") {
            chatItems.push(
                <div className="chat chat-end">
                    <div className="chat-bubble chat-bubble-primary">
                        {message.content}
                    </div>
                </div>
            )
        } else if (message.sender == "bot") {
            chatItems.push(
                <div className="chat chat-start">
                    <div className="chat-bubble chat-bubble-secondary">
                        {message.content}
                    </div>
                </div>
            )
        }
    })
    
    /*
    useEffect(() => {
        if (isProcessing) {
    }, [isProcessing])*/

    return (
        <div>
            <div>
                {chatItems}   
            </div>
            <div style={{position: "fixed", bottom: "0%", width: "100%", display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between", paddingLeft: "10px", paddingRight: "10px"}}>
                <input type="text" onSubmit={(() => {onSendMessage(userMessage || "")})} style={{position: "fixed", bottom: "3%", width: "90%", borderRadius: "8px", borderColor: "#F0F0F0", borderWidth: "2px", backgroundColor: "#FCFCFC", padding: "5px", paddingTop: "10px", paddingBottom: "10px"}} value={userMessage || ""} onChange={(e) => setUserMessage(e.target.value)} placeholder="Digite sua mensagem..." />
                <button style={{position: "fixed", right: "10px", zIndex: "1000", bottom: "3%"}} onClick={(() => {onSendMessage(userMessage || "")})}>
                    Enviar
                </button>
            </div>    
        </div>
    );
}