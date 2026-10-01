import { ChatInput } from "./chatInput";

export type messageType = { content: string, sender: "user" | "bot" };

export function Chatbox({ messages, isProcessing, onSendMessage }: { messages: messageType[], isProcessing: boolean, onSendMessage: (message: string) => void }) {
    const chatItems : React.ReactNode[] = [];

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
            <ChatInput onSendMessage={onSendMessage} />
        </div>
    );
}