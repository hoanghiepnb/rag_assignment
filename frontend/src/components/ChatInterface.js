import React, { useState, useRef, useEffect } from "react";
import "../styles/Chat.css";

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Bug: Missing loading state

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!input.trim()) {
        setError("Please enter your measurements or fit issues.");
        return;
      }
    setIsLoading(true);
    setError(null);

    try {
      // Bug: No loading indicator
      const response = await fetch("http://localhost:8000/api/bra-fitting", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: input })
      });

      const data = await response.json();

      // Bug: No error handling for failed requests

      if (!response.ok) {
        throw new Error(data.detail || "Something went wrong");
      }

      setMessages(prev => [
        ...prev,
        { text: input, isUser: true },
        {
          text: `Recommended Size: ${data.recommendation || "N/A"}`,
          reasoning: data.reasoning,
          fitTips: data.fit_tips,
          issues: data.identified_issues,
          confidence: data.confidence,
          isUser: false
        }
      ]);
      setInput("");
    } catch (error) {
      // Bug: Poor error handling
      console.error(error);
      setError(error.message || "Unexpected error");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.isUser ? "user" : "bot"}`}>
            {msg.isUser ? (
              <div className="bubble user-bubble">{msg.text}</div>
            ) : (
              <div className="bubble bot-bubble">
                <div><strong>{msg.text}</strong></div>
                {msg.confidence !== undefined && (
                  <div><em>Confidence:</em> {msg.confidence}</div>
                )}
                {msg.reasoning && (
                  <div><em>Reason:</em> {msg.reasoning}</div>
                )}
                {msg.fitTips && (
                  <div><em>Tip:</em> {msg.fitTips}</div>
                )}
                {msg.issues?.length > 0 && (
                  <div><em>Issues:</em> {msg.issues.join(", ")}</div>
                )}
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="message bot">
            <div className="bubble bot-bubble loading">Loading...</div>
          </div>
        )}
        {error && <div className="error">{error}</div>}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Describe your measurements or fit issues..."
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? "Sending..." : "Send"}
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;
