/**
 * Message Input component - Text input with send button
 */
import { Box, TextField, IconButton } from "@mui/material";
import SendIcon from "@mui/icons-material/Send";

interface MessageInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  disabled: boolean;
}

export default function MessageInput({
  value,
  onChange,
  onSend,
  disabled,
}: MessageInputProps) {
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
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
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Describe the chart you want to create..."
          disabled={disabled}
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
          onClick={onSend}
          disabled={!value.trim() || disabled}
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
  );
}
