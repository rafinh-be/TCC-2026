"use client";
import React, { useState, useEffect, useRef } from 'react';

import { Sidebar } from '../components/sidebar/sidebar';
import { Chatbox } from '../components/chatbox/chatbox';

import { citedDocumentIds } from '@/utils/citedDocuments';
import { useChat } from '@/hooks/useChat';

function AsyncMessenger() {
  //const [inputMessage, setInputMessage] = useState("");
  const [serverStatus, setServerStatus] = useState("Disconnected");
  const [receivedMessage, setReceivedMessage] = useState("");
  const { messages, isProcessing, liveThinking, sendMessage } = useChat();
  
  const socketRef = useRef(null);

  /*
  const onReceiveMessage = (message: { assistant: string }) => {
    setMessages((prev) => [...prev.slice(0, -1), { content: message.assistant, sender: "bot" }]);
  }

  useEffect(() => {
    const ws = new WebSocket("ws://127.0.0.1:8000/ws/chat");
    socketRef.current = ws;

    ws.onopen = () => {
      setServerStatus("Connected & Ready");
    };

    ws.onmessage = (event) => {
      const parsedData = JSON.parse(event.data);
      onReceiveMessage(parsedData);
      setIsProcessing(false); 
    };

    ws.onclose = () => {
      setServerStatus("Disconnected");
    };

    return () => {
        ws.close();
    };
  }, []);*/

  /*
  const handleSendMessage = (inputMessage: string | null) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      if (!inputMessage?.trim()) return;

      setMessages((prev) => [
        ...prev,
        { content: inputMessage, sender: "user" },
        { content: "Aguarde, estou processando sua solicitação...", sender: "bot" },
      ]);
      // Send the initial message to backend
      socketRef.current.send(inputMessage);
      setIsProcessing(true); // Put frontend into a waiting/loading state
      setReceivedMessage(""); // Clear previous responses
    } else {
      alert("WebSocket is not connected to backend.");
    }
  };
  */

  useEffect(() => {
    const pendingMessage = sessionStorage.getItem("pendingMessage");
    if (!pendingMessage) return;
    sessionStorage.removeItem("pendingMessage");
    sendMessage(pendingMessage);
  }, []);

  const pageContent = () => {
    return (
    <div style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column" }}>
      {/*<h2>Async Delayed Response Pattern</h2>
      <p>System Status: <strong>{serverStatus}</strong></p>

      <div style={{ marginBottom: '20px' }}>
        <input 
          type="text" 
          value={inputMessage} 
          onChange={(e) => setInputMessage(e.target.value)} 
          placeholder="Type something for backend..."
          disabled={isProcessing}
          style={{ padding: '8px', width: '250px', marginRight: '10px' }}
        />
        <button onClick={handleSendMessage} disabled={isProcessing} style={{ padding: '8px 15px' }}>
          {isProcessing ? "Backend processing..." : "Send to Backend"}
        </button>
      </div>

      {isProcessing && (
        <div style={{ color: 'orange' }}>
          ⏳ Frontend is now idling and awaiting the backend to respond...
        </div>
      )}

      {receivedMessage && (
        <div style={{ marginTop: '20px', padding: '15px', background: '#e2f0d9', borderRadius: '5px' }}>
          <h4>📩 Received from Backend:</h4>
          <p>{receivedMessage}</p>
        </div>
      )}*/}
      <Chatbox messages={messages} isProcessing={isProcessing} liveThinking={liveThinking} onSendMessage={sendMessage} />
    </div>
    );}

  return (
    <Sidebar content={pageContent()} citedDocumentIds={citedDocumentIds(messages)} />
  );
}

export default AsyncMessenger;
