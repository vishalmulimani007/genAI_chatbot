import React, { useState, useEffect, useRef } from "react";
import Message from "./Message";

function ChatWindow({ chatId, chat, updateMessages, updateTitle }) {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  const messages = chat?.messages || [];

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ✅ DELETE MESSAGE
  const handleDeleteMessage = (index) => {
    const updated = messages.filter((_, i) => i !== index);
    updateMessages(chatId, updated);
  };

  const sendMessage = async (customInput = null) => {
    const text = customInput || input;

    if (!text.trim() || !chatId || loading) return;

    const userMessage = { role: "user", content: text };

    const newMessages = [...messages, userMessage];
    updateMessages(chatId, newMessages);

    if (messages.length === 0) {
      updateTitle(chatId, text.slice(0, 30));
    }

    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:7860/chat", {
        method: "POST",
        headers: {
          "Content-Type": "text/plain",
          "session-id": chatId,
        },
        body: text,
      });

      const data = await res.json();
      let cleanedAnswer = data.answer || "";

      // Remove unwanted prefix
      cleanedAnswer = cleanedAnswer.replace(
        /^Based on the provided context.*?\.\s*/i,
        ""
      );

      const botMessage = {
        role: "assistant",
        content: cleanedAnswer,
        sources: data.sources || [],
        suggestions: data.suggested_questions || [],
      };

      updateMessages(chatId, [...newMessages, botMessage]);
    } catch (err) {
      console.error(err);
    }

    setLoading(false);
  };

  return (
    <div className="chat-window">
      {!chatId ? (
        <div className="empty-state">Start a new chat</div>
      ) : (
        <>
          {/* ✅ Messages */}
          <div className="messages">
            {messages.map((msg, i) => (
              <Message
                key={i}
                msg={msg}
                index={i}
                deleteMessage={handleDeleteMessage}
                sendMessage={sendMessage}
              />
            ))}

            {loading && (
              <div className="bot-msg typing">
                <span></span>
                <span></span>
                <span></span>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* ✅ ChatGPT-style Input */}
          <div className="input-container">
            <div className="input-wrapper">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask anything..."
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !loading && input.trim()) {
                    sendMessage();
                  }
                }}
              />

              <button
                className="send-btn"
                onClick={() => sendMessage()}
                disabled={loading || !input.trim()}
              >
                ➤
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default ChatWindow;
