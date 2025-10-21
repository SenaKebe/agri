import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./App.css";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [location, setLocation] = useState("Central Ethiopia");
  const [cropType, setCropType] = useState("maize");
  const [systemStatus, setSystemStatus] = useState({
    api: "checking",
    rag: "checking",
  });
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
    checkSystemStatus();
  }, [messages]);

  const checkSystemStatus = async () => {
    try {
      console.log("Checking system status...");
      const response = await axios.get(`${API_BASE_URL}/rag/status`);
      console.log("RAG Status response:", response.data);
      setSystemStatus((prev) => ({ ...prev, rag: "active" }));
    } catch (error) {
      console.error("Error checking RAG status:", error);
      setSystemStatus((prev) => ({ ...prev, rag: "inactive" }));
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: "user",
      content: inputMessage,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);

    try {
      console.log("Sending message to API:", {
        message: inputMessage,
        location: location,
        crop_type: cropType,
      });

      const response = await axios.post(
        `${API_BASE_URL}/chat`,
        {
          message: inputMessage,
          location: location,
          crop_type: cropType,
        },
        {
          timeout: 30000, // 30 second timeout
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      console.log("API Response:", response.data);

      const aiMessage = {
        id: Date.now() + 1,
        type: "ai",
        content: response.data.response,
        agentBreakdown: response.data.agent_breakdown || [],
        timestamp: new Date().toLocaleTimeString(),
      };

      setMessages((prev) => [...prev, aiMessage]);
      setSystemStatus((prev) => ({ ...prev, api: "active" }));
    } catch (error) {
      console.error("Full error details:", error);

      let errorMessage = "Sorry, I encountered an error. Please try again.";

      if (error.code === "ECONNREFUSED") {
        errorMessage =
          "Cannot connect to the server. Make sure your FastAPI backend is running on port 8000.";
      } else if (error.response) {
        // Server responded with error status
        errorMessage = `Server error: ${error.response.status} - ${
          error.response.data?.detail || "Unknown error"
        }`;
      } else if (error.request) {
        // Request was made but no response received
        errorMessage =
          "No response from server. Check if the backend is running.";
      } else if (error.message.includes("Network Error")) {
        errorMessage =
          "Network error. Check your connection and CORS settings.";
      } else if (error.message.includes("timeout")) {
        errorMessage =
          "Request timeout. The server is taking too long to respond.";
      }

      const errorMessageObj = {
        id: Date.now() + 1,
        type: "error",
        content: errorMessage,
        timestamp: new Date().toLocaleTimeString(),
      };

      setMessages((prev) => [...prev, errorMessageObj]);
      setSystemStatus((prev) => ({ ...prev, api: "inactive" }));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  const testConnection = async () => {
    try {
      console.log("Testing connection to backend...");
      const response = await axios.get(`${API_BASE_URL}/health`);
      console.log("Backend health check:", response.data);
      alert(`Backend is running: ${response.data.status}`);
    } catch (error) {
      console.error("Connection test failed:", error);
      alert("Cannot connect to backend. Check if it's running on port 8000.");
    }
  };

  const quickQuestions = [
    "When is the best time to plant maize in my region?",
    "How do I control maize stalk borer in Ethiopia?",
    "What fertilizer should I use for clay soil?",
    "Should I plant with the current weather forecast?",
    "How much water does maize need during dry season?",
  ];

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">🌱</span>
            <h1>Ethiopia Crop Advisor</h1>
          </div>
          <div className="status-indicators">
            <div className={`status-indicator ${systemStatus.api}`}>
              <div className="status-dot"></div>
              API {systemStatus.api}
            </div>
            <div className={`status-indicator ${systemStatus.rag}`}>
              <div className="status-dot"></div>
              RAG {systemStatus.rag}
            </div>
            <button className="clear-btn" onClick={clearChat}>
              Clear Chat
            </button>
            <button className="test-btn" onClick={testConnection}>
              Test Connection
            </button>
          </div>
        </div>
      </header>

      {/* Main Chat Area */}
      <main className="chat-container">
        {messages.length === 0 ? (
          <div className="welcome-section">
            <div className="welcome-content">
              <h2>Welcome to Ethiopia Crop Advisor</h2>
              <p>
                Your intelligent farming assistant for Ethiopian agriculture
              </p>

              <div className="connection-info">
                <p>
                  <strong>Backend URL:</strong> {API_BASE_URL}
                </p>
                <button
                  onClick={testConnection}
                  className="test-connection-btn"
                >
                  Test Backend Connection
                </button>
              </div>

              <div className="quick-questions">
                <h3>Quick Questions:</h3>
                <div className="question-chips">
                  {quickQuestions.map((question, index) => (
                    <button
                      key={index}
                      className="question-chip"
                      onClick={() => {
                        setInputMessage(question);
                        setTimeout(
                          () =>
                            document.getElementById("message-input")?.focus(),
                          100
                        );
                      }}
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="messages-container">
            {messages.map((message) => (
              <div key={message.id} className={`message ${message.type}`}>
                <div className="message-content">
                  <div className="message-header">
                    <span className="message-sender">
                      {message.type === "user"
                        ? "👤 You"
                        : message.type === "error"
                        ? "❌ Error"
                        : "🌱 Crop Advisor"}
                    </span>
                    <span className="message-time">{message.timestamp}</span>
                  </div>
                  <div className="message-text">{message.content}</div>

                  {message.agentBreakdown &&
                    message.agentBreakdown.length > 0 && (
                      <div className="agent-breakdown">
                        <div className="breakdown-header">
                          <small>Expert Analysis:</small>
                        </div>
                        {message.agentBreakdown.map((agent, index) => (
                          <div key={index} className="agent-response">
                            <span className="agent-name">
                              {agent.agent_type
                                ? agent.agent_type
                                    .replace("_", " ")
                                    .replace(/\b\w/g, (c) => c.toUpperCase())
                                : "Expert"}
                            </span>
                            <div className="confidence-bar">
                              <div
                                className="confidence-fill"
                                style={{
                                  width: `${(agent.confidence || 0.5) * 100}%`,
                                }}
                              ></div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="message ai">
                <div className="message-content">
                  <div className="typing-indicator">
                    <div className="typing-dots">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                    <span>
                      Agricultural experts are analyzing your question...
                    </span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </main>

      {/* Input Section */}
      <footer className="input-section">
        <div className="input-controls">
          <select
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="location-select"
          >
            <option value="Central Ethiopia">Central Ethiopia</option>
            <option value="Amhara Region">Amhara Region</option>
            <option value="Oromia Region">Oromia Region</option>
            <option value="Southern Region">Southern Region</option>
            <option value="Tigray Region">Tigray Region</option>
          </select>

          <select
            value={cropType}
            onChange={(e) => setCropType(e.target.value)}
            className="crop-select"
          >
            <option value="maize">Maize</option>
            <option value="teff">Teff</option>
            <option value="wheat">Wheat</option>
            <option value="barley">Barley</option>
            <option value="sorghum">Sorghum</option>
          </select>
        </div>

        <div className="input-container">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Ask about planting, weather, pests, or soil management for Ethiopian agriculture..."
            rows="1"
            className="message-input"
            disabled={isLoading}
            id="message-input"
          />
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="send-button"
          >
            {isLoading ? (
              <div className="loading-spinner"></div>
            ) : (
              <span>Send</span>
            )}
          </button>
        </div>

        <div className="input-hint">
          <small>Press Enter to send • Shift+Enter for new line</small>
        </div>
      </footer>
    </div>
  );
}

export default App;
