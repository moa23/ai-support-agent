import { useState } from "react";
import "./App.css";
import ReactMarkdown from "react-markdown";

type SupportMessage = {
  role: "user" | "assistant";
  content: string;
  category?: string;
};

function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<SupportMessage[]>([]);
  const [loading, setLoading] = useState(false);

  async function sendMessage(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const text = message.trim();

    if (!text || loading) return;

    setMessages((previous) => [
      ...previous,
      { role: "user", content: text },
    ]);
    setMessage("");
    setLoading(true);

    try {
      const response = await fetch("https://ai-support-agent-313288084160.europe-north1.run.app/support", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: text }),
      });

      if (!response.ok) {
        throw new Error("Support request failed");
      }

      const data = await response.json();

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: data.response,
          category: data.category,
        },
      ]);
    } catch {
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            "I could not connect to the support service. Please check that the backend is running.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app">
      <header className="header">
        <div className="logo">AI</div>
        <div>
          <h1>AI Support Agent</h1>
          <p>Your intelligent IT support assistant</p>
        </div>
        <span className="status">● Online UI</span>
      </header>

      <section className="chat">
        {messages.length === 0 ? (
          <div className="welcome">
            <div className="welcome-icon">✦</div>
            <h2>How can I help you today?</h2>
            <p>
              Describe your IT issue and I’ll help you troubleshoot it.
            </p>
            <div className="suggestions">
              {[
                "My Wi-Fi is not working",
                "I cannot access my email",
                "My computer is running slowly",
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  className="suggestion"
                  onClick={() => setMessage(suggestion)}
                >
                  {suggestion} <span>↗</span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="messages">
            {messages.map((item, index) => (
         
         <article
           key={`${item.role}-${index}`}
           className={`message ${item.role}`}
         >
           <div className="message-label">
             {item.role === "user" ? "You" : "AI Support"}
           </div>
         
           <div className="message-content">
             <ReactMarkdown>{item.content}</ReactMarkdown>
           </div>
         
           {item.category && (
             <span className="category">
               Category: {item.category}
             </span>
           )}
         </article>
            ))}
            {loading && (
              <div className="message assistant">
                <div className="message-label">AI Support</div>
                <div className="message-content">Thinking...</div>
              </div>
            )}
          </div>
        )}
      </section>

      <form className="composer" onSubmit={sendMessage}>
        <textarea
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="Describe your IT issue..."
          maxLength={2000}
          rows={2}
          disabled={loading}
        />
        <div className="composer-footer">
          <span>Never share passwords or API keys.</span>
          <button
            className="send-button"
            type="submit"
            disabled={loading || message.trim().length < 3}
          >
            {loading ? "Sending..." : "Send message ↑"}
          </button>
        </div>
      </form>

      <footer>AI-powered troubleshooting · Built with React and FastAPI</footer>
    </main>
  );
}

export default App;
