"use client";
import React, { useState, useEffect, useRef } from 'react';

function AsyncMessenger() {
  const [inputMessage, setInputMessage] = useState("");
  const [serverStatus, setServerStatus] = useState("Disconnected");
  const [receivedMessage, setReceivedMessage] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  
  const socketRef = useRef(null);

  // Initialize WebSocket connection on component load
  useEffect(() => {
    socketRef.current = new WebSocket("ws://127.0.0.1:8000/ws/chat");

    socketRef.current.onopen = () => {
      setServerStatus("Connected & Ready");
    };

    // THIS IS WHERE THE FRONTEND AWAITS THE BACKEND PUSH
    socketRef.current.onmessage = (event) => {
      setReceivedMessage(event.data);
      setIsProcessing(false); // Backend finished, remove loading state
    };

    socketRef.current.onclose = () => {
      setServerStatus("Disconnected");
    };

    // Clean up connection when user leaves the page
    return () => {
      if (socketRef.current) socketRef.current.close();
    };
  }, []);

  const handleSendMessage = () => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      if (!inputMessage.trim()) return;

      // Send the initial message to backend
      socketRef.current.send(inputMessage);
      setIsProcessing(true); // Put frontend into a waiting/loading state
      setReceivedMessage(""); // Clear previous responses
    } else {
      alert("WebSocket is not connected to backend.");
    }
  };

  return (
    <div style={{ padding: '30px', fontFamily: 'Arial, sans-serif' }}>
      <h2>Async Delayed Response Pattern</h2>
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
      )}
    </div>
  );
}

export default AsyncMessenger;
