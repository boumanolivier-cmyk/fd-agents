/**
 * Message List component - Displays chat history
 */
import { Box, Typography, Chip, CircularProgress } from "@mui/material";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import type { Message } from "../../types";

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
  onExampleClick: (prompt: string) => void;
}

const examplePrompts = [
  "Create a bar chart: Q1=100, Q2=150, Q3=200, Q4=175",
  "Make a line chart showing monthly sales trend",
];

export default function MessageList({
  messages,
  isLoading,
  onExampleClick,
}: MessageListProps) {
  return (
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
      {messages.length === 0 && (
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
                onClick={() => onExampleClick(prompt)}
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

      {messages.map((message) => (
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
  );
}
