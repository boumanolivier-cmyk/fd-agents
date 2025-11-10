/**
 * Chat interface component - FD-inspired clean design
 */
import { useState } from "react";
import { useAtom, useAtomValue, useSetAtom } from "jotai";
import {
  Box,
  TextField,
  IconButton,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  Button,
  Tooltip,
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import RefreshIcon from "@mui/icons-material/Refresh";
import {
  sessionIdAtom,
  chatHistoryAtom,
  isLoadingAtom,
  currentChartAtom,
  errorAtom,
} from "../state/atoms";
import { sendChatMessage, clearChatHistory } from "../api/client";
import type { Message } from "../types";

export default function ChatInterface() {
  const [input, setInput] = useState("");
  const [chatHistory, setChatHistory] = useAtom(chatHistoryAtom);
  const [isLoading, setIsLoading] = useAtom(isLoadingAtom);
  const [error, setError] = useAtom(errorAtom);
  const sessionId = useAtomValue(sessionIdAtom);
  const setCurrentChart = useSetAtom(currentChartAtom);

  const handleNewConversation = async () => {
    try {
      // Clear chat history on backend
      await clearChatHistory(sessionId);

      // Clear local state
      setChatHistory([]);
      setCurrentChart(null);
      setError(null);
      setInput("");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to clear conversation"
      );
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: "user",
      content: input,
      timestamp: Date.now(),
    };

    setChatHistory((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    setError(null);

    try {
      const response = await sendChatMessage(input, sessionId);

      const assistantMessage: Message = {
        id: `msg-${Date.now()}`,
        role: "assistant",
        content: response.response,
        chartUrl: response.chart_url,
        chartId: response.chart_id,
        timestamp: Date.now(),
      };

      setChatHistory((prev) => [...prev, assistantMessage]);

      if (response.chart_url && response.chart_id) {
        setCurrentChart({
          url: response.chart_url,
          id: response.chart_id,
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message");
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const examplePrompts = [
    "Create a bar chart: Q1=100, Q2=150, Q3=200, Q4=175",
    "Make a line chart showing monthly sales trend",
  ];

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        bgcolor: "#ffffff",
      }}
    >
      {/* Header with New Conversation Button */}
      {chatHistory.length > 0 && (
        <Box
          sx={{
            px: 3,
            py: 2,
            borderBottom: "1px solid",
            borderColor: "divider",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            bgcolor: "#fafafa",
          }}
        >
          <Typography variant="body2" color="text.secondary" fontWeight={500}>
            Conversation in progress
          </Typography>
          <Tooltip title="Start a new conversation (clears chat history)">
            <Button
              size="small"
              startIcon={<RefreshIcon />}
              onClick={handleNewConversation}
              disabled={isLoading}
              sx={{
                textTransform: "none",
                color: "text.secondary",
                "&:hover": {
                  bgcolor: "rgba(0, 0, 0, 0.04)",
                },
              }}
            >
              New Conversation
            </Button>
          </Tooltip>
        </Box>
      )}

      {/* Chat History */}
      <Box
        sx={{
          flex: 1,
          overflowY: "auto",
          px: 3,
          py: 2,
          display: "flex",
          flexDirection: "column",
          gap: 2,
        }}
      >
        {chatHistory.length === 0 && (
          <Box sx={{ textAlign: "center", mt: 6, mb: 4 }}>
            <Box sx={{ display: "flex", justifyContent: "center", mb: 2 }}>
              <TrendingUpIcon
                sx={{ fontSize: 48, color: "primary.main", opacity: 0.8 }}
              />
            </Box>
            <Typography
              variant="h5"
              fontWeight={600}
              gutterBottom
              sx={{ color: "text.primary" }}
            >
              Create Professional Charts
            </Typography>
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ mb: 3, maxWidth: 480, mx: "auto" }}
            >
              Ask me to generate bar or line charts from your data. I'll analyze
              your request and create publication-ready visualizations.
            </Typography>

            <Box
              sx={{
                display: "flex",
                flexDirection: "column",
                gap: 1,
                alignItems: "center",
                mt: 3,
              }}
            >
              <Typography
                variant="caption"
                color="text.secondary"
                fontWeight={600}
                sx={{ mb: 1 }}
              >
                Example Requests:
              </Typography>
              {examplePrompts.map((prompt, idx) => (
                <Chip
                  key={idx}
                  label={prompt}
                  variant="outlined"
                  size="small"
                  onClick={() => setInput(prompt)}
                  sx={{
                    cursor: "pointer",
                    maxWidth: "100%",
                    height: "auto",
                    py: 1,
                    "& .MuiChip-label": {
                      whiteSpace: "normal",
                      textAlign: "center",
                    },
                    "&:hover": {
                      borderColor: "primary.main",
                      bgcolor: "rgba(55, 149, 150, 0.04)",
                    },
                  }}
                />
              ))}
            </Box>
          </Box>
        )}

        {chatHistory.map((message) => (
          <Box
            key={message.id}
            sx={{
              display: "flex",
              flexDirection: "column",
              alignSelf: message.role === "user" ? "flex-end" : "flex-start",
              maxWidth: "75%",
            }}
          >
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{ mb: 0.5, px: 1.5, fontWeight: 500 }}
            >
              {message.role === "user" ? "You" : "AI Assistant"}
            </Typography>
            <Box
              sx={{
                px: 2,
                py: 1.5,
                borderRadius: 2,
                bgcolor: message.role === "user" ? "primary.main" : "#f5f5f5",
                color: message.role === "user" ? "#ffffff" : "text.primary",
                border: message.role === "user" ? "none" : "1px solid #e8e8e8",
              }}
            >
              <Typography
                variant="body2"
                sx={{ whiteSpace: "pre-wrap", lineHeight: 1.6 }}
              >
                {message.content}
              </Typography>
              {message.chartUrl && (
                <Chip
                  label="Chart generated"
                  size="small"
                  color="success"
                  sx={{ mt: 1, height: 20, fontSize: "0.7rem" }}
                />
              )}
            </Box>
          </Box>
        ))}

        {isLoading && (
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              gap: 1.5,
              px: 2,
              py: 1,
            }}
          >
            <CircularProgress size={16} />
            <Typography variant="body2" color="text.secondary" fontWeight={500}>
              Analyzing request and generating chart...
            </Typography>
          </Box>
        )}
      </Box>

      {/* Error Display */}
      {error && (
        <Alert
          severity="error"
          onClose={() => setError(null)}
          sx={{ mx: 2, mb: 1, borderRadius: 1 }}
        >
          {error}
        </Alert>
      )}

      {/* Input Area */}
      <Box
        sx={{
          p: 2,
          borderTop: "1px solid",
          borderColor: "divider",
          bgcolor: "#fafafa",
        }}
      >
        <Box sx={{ display: "flex", gap: 1 }}>
          <TextField
            fullWidth
            multiline
            maxRows={3}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Describe the chart you want to create..."
            disabled={isLoading}
            variant="outlined"
            size="small"
            sx={{
              "& .MuiOutlinedInput-root": {
                bgcolor: "#ffffff",
                borderRadius: 2,
              },
            }}
          />
          <IconButton
            color="primary"
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            sx={{
              bgcolor: "primary.main",
              color: "#ffffff",
              "&:hover": {
                bgcolor: "primary.dark",
              },
              "&.Mui-disabled": {
                bgcolor: "#e0e0e0",
                color: "#ffffff",
              },
            }}
          >
            <SendIcon />
          </IconButton>
        </Box>
      </Box>
    </Box>
  );
}
