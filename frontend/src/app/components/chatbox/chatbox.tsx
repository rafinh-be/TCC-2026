type messageType = { content: string, sender: "user" | "bot" };

export function Chatbox({ messages, onSendMessage }: { messages: messageType[], onSendMessage: (message: string) => void }) {
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
    
    return (
        <div>
            {chatItems}
        </div>
    );
}