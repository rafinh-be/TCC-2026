"use client";
import { useState } from "react";

import type { messageType } from "@/app/components/chatbox/chatbox";
import { readChatStream } from "@/utils/chatStream";
import { API_URL } from "@/config/api";
import { STREAM_THINKING } from "@/config/chat";

export function useChat() {
    const [messages, setMessages] = useState<messageType[]>([]);
    const [isProcessing, setIsProcessing] = useState(false);
    const [liveThinking, setLiveThinking] = useState<string[]>([]);

    const sendMessageApi = async (inputMessage: string) => {
        try {
            const payload: messageType[] = [...messages, { content: inputMessage, sender: "user" }];

            setMessages([...messages, { sender: "user", content: inputMessage }]);
            setIsProcessing(true);
            const response = await fetch(`${API_URL}/chat`, {
                method: "POST",
                body: JSON.stringify({ messages: payload }),
                headers: { "Content-Type": "application/json" }
            });
            const data = await response.json();
            setIsProcessing(false);

            setMessages([...messages, { sender: "user", content: inputMessage }, { sender: "bot", content: data["answer"].message.content, sources: data["sources"], citations: data["citations"] }]);
        } catch (e) {
            console.log(e);
        }
    };

    const sendMessageStream = async (inputMessage: string) => {
        const history: messageType[] = [...messages, { sender: "user", content: inputMessage }];
        setMessages(history);
        setIsProcessing(true);
        setLiveThinking([]);
        try {
            const response = await fetch(`${API_URL}/chat/stream`, {
                method: "POST",
                body: JSON.stringify({ messages: history }),
                headers: { "Content-Type": "application/json" }
            });
            if (!response.ok) throw new Error(`Falha ${response.status}`);
            await readChatStream(response, (event) => {
                if (event.type === "thinking") {
                    setLiveThinking((previous) => [...previous, event.text]);
                } else if (event.type === "final") {
                    setMessages([...history, { sender: "bot", content: event.answer.message.content, thinking: event.answer.message.thinking, sources: event.sources, citations: event.citations }]);
                } else {
                    setMessages([...history, { sender: "bot", content: event.message }]);
                }
            });
        } catch (e) {
            console.log(e);
            setMessages([...history, { sender: "bot", content: "Não foi possível gerar a resposta. Tente novamente." }]);
        } finally {
            setIsProcessing(false);
            setLiveThinking([]);
        }
    };

    const sendMessage = STREAM_THINKING ? sendMessageStream : sendMessageApi;

    return { messages, isProcessing, liveThinking, sendMessage };
}
