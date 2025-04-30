import React, { useState } from "react";
import "../styles/Chat.css";

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);


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
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.isUser ? "user" : "bot"}`}>
            {msg.isUser ? (
              msg.text
            ) : (
              // Bug: Poor information display
              <div>
                <strong>{msg.text}</strong>
                <div><em>Confidence:</em> {msg.confidence}</div>
                <div><em>Reason:</em> {msg.reasoning}</div>
                <div><em>Tips:</em> {msg.fitTips}</div>
                {msg.issues?.length > 0 && (
                  <div><em>Identified Issues:</em> {msg.issues.join(", ")}</div>
                )}
              </div>
            )}
          </div>
        ))}
        {isLoading && <div className="message bot">Loading recommendation...</div>}
        {error && <div className="error">{error}</div>}
      </div>
      <form onSubmit={handleSubmit} className="input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter your measurements and fit issues..."
        />
        <button type="submit">Get Recommendation</button>
      </form>
    </div>
  );
};

export default ChatInterface;
