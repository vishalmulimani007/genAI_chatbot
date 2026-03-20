import React from "react";

function Sidebar({
  chats,
  currentChatId,
  setCurrentChatId,
  createNewChat,
  deleteChat,
}) {
  return (
    <div className="sidebar">
      {/* ✅ New Chat */}
      <button className="new-chat-btn" onClick={createNewChat}>
        + New Chat
      </button>

      {/* ✅ Chat List */}
      <div className="chat-list">
        {Object.entries(chats).map(([id, chat]) => (
          <div
            key={id}
            className={id === currentChatId ? "chat-item active" : "chat-item"}
          >
            {/* ✅ Chat title click */}
            <span className="chat-title" onClick={() => setCurrentChatId(id)}>
              {chat.title}
            </span>

            {/* ✅ Delete button */}
            <button
              className="delete-btn"
              onClick={(e) => {
                e.stopPropagation(); // 🔥 IMPORTANT (prevents selecting chat)
                deleteChat(id);
              }}
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Sidebar;
