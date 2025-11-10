/**
 * Chat interface component - FD-inspired clean design
 * Refactored into smaller components for better maintainability
 */
import { Box, Alert } from "@mui/material";
import ChatHeader from "./chat/ChatHeader";
import MessageList from "./chat/MessageList";
import MessageInput from "./chat/MessageInput";
import { useChatMessages } from "../hooks/useChatMessages";

export default function ChatInterface() {
  const {
    input,
    setInput,
    chatHistory,
    isLoading,
    error,
    setError,
    handleSend,
    handleNewConversation,
  } = useChatMessages();

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        bgcolor: "#ffffff",
      }}
    >
      <ChatHeader
        hasMessages={chatHistory.length > 0}
        onNewConversation={handleNewConversation}
        disabled={isLoading}
      />

      <MessageList
        messages={chatHistory}
        isLoading={isLoading}
        onExampleClick={setInput}
      />

      {error && (
        <Alert
          severity="error"
          onClose={() => setError(null)}
          sx={{ mx: 2, mb: 1, borderRadius: 1 }}
        >
          {error}
        </Alert>
      )}

      <MessageInput
        value={input}
        onChange={setInput}
        onSend={handleSend}
        disabled={isLoading}
      />
    </Box>
  );
}
