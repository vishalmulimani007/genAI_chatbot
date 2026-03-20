import React from "react";

function Message({ msg, index, deleteMessage, sendMessage }) {
  return (
    <div className={msg.role === "user" ? "user-msg" : "bot-msg"}>
      {/* ✅ MESSAGE HEADER */}
      <div className="message-header">
        <div className="message-content">{msg.content}</div>

        {/* Delete button */}
        <button className="delete-msg-btn" onClick={() => deleteMessage(index)}>
          ✕
        </button>
      </div>

      {/* ✅ SOURCES (separate section) */}
      {msg.sources?.length > 0 && (
        <div className="sources-box">
          <div className="section-title">Sources</div>

          <div className="sources-list">
            {msg.sources.map((s, i) => (
              <a
                key={i}
                href={s.url}
                target="_blank"
                rel="noreferrer"
                className="source-item"
              >
                🔗 {s.title}
              </a>
            ))}
          </div>
        </div>
      )}

      {/* ✅ SUGGESTIONS (chips style like ChatGPT) */}
      {msg.suggestions?.length > 0 && (
        <div className="suggestions-box">
          {msg.suggestions.map((q, i) => (
            <button
              key={i}
              className="suggestion-chip"
              onClick={() => sendMessage(q)}
            >
              {q}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default Message;
