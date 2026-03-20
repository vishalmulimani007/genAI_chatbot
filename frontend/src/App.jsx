import React, { useState, useEffect } from "react";
import "./App.css";
import ChatWindow from "./components/ChatWindow";
import Sidebar from "./components/Sidebar";

function App() {
  // ✅ Detect screen size
  const [isMobile, setIsMobile] = useState(() => window.innerWidth < 768);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // ✅ Load chats
  const [chats, setChats] = useState(() => {
    try {
      const saved = localStorage.getItem("chats");
      return saved ? JSON.parse(saved) : {};
    } catch (err) {
      console.error("Failed to parse chats:", err);
      return {};
    }
  });

  // ✅ Load active chat
  const [currentChatId, setCurrentChatId] = useState(() => {
    return localStorage.getItem("currentChatId") || null;
  });

  // ✅ Persist chats
  useEffect(() => {
    localStorage.setItem("chats", JSON.stringify(chats));
  }, [chats]);

  // ✅ Persist active chat
  useEffect(() => {
    if (currentChatId) {
      localStorage.setItem("currentChatId", currentChatId);
    }
  }, [currentChatId]);

  // ✅ Create new chat
  const createNewChat = () => {
    const id = "chat_" + Date.now();

    setChats((prev) => ({
      ...prev,
      [id]: {
        title: "New Chat",
        messages: [],
      },
    }));

    setCurrentChatId(id);
  };

  // ✅ Update messages
  const updateMessages = (chatId, messages) => {
    setChats((prev) => ({
      ...prev,
      [chatId]: {
        ...prev[chatId],
        messages,
      },
    }));
  };

  // ✅ Update title
  const updateTitle = (chatId, title) => {
    setChats((prev) => ({
      ...prev,
      [chatId]: {
        ...prev[chatId],
        title,
      },
    }));
  };

  // ✅ Delete chat
  const deleteChat = (chatId) => {
    setChats((prev) => {
      const updated = { ...prev };
      delete updated[chatId];
      return updated;
    });

    if (chatId === currentChatId) {
      setCurrentChatId(null);
      localStorage.removeItem("currentChatId");
    }
  };

  return (
    <div className="app-root">
      {/* ✅ HEADER (ChatGPT style) */}
      <div className="app-header">GitLab Chatbot</div>

      {/* ✅ MAIN LAYOUT */}
      <div className="app-container">
        {/* Sidebar hidden on mobile */}
        {!isMobile && (
          <Sidebar
            chats={chats}
            currentChatId={currentChatId}
            setCurrentChatId={setCurrentChatId}
            createNewChat={createNewChat}
            deleteChat={deleteChat}
          />
        )}

        <ChatWindow
          chatId={currentChatId}
          chat={chats[currentChatId]}
          updateMessages={updateMessages}
          updateTitle={updateTitle}
          isMobile={isMobile}
        />
      </div>
    </div>
  );
}

export default App;
