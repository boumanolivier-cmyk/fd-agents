/**
 * Chat Header component - Shows conversation status and new conversation button
 */
import { Box, Typography, Button, Tooltip } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';

interface ChatHeaderProps {
  hasMessages: boolean;
  onNewConversation: () => void;
  disabled: boolean;
}

export default function ChatHeader({ hasMessages, onNewConversation, disabled }: ChatHeaderProps) {
  if (!hasMessages) {
    return null;
  }

  return (
    <Box
      sx={{
        px: 3,
        py: 2,
        borderBottom: '1px solid',
        borderColor: 'divider',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        bgcolor: '#fafafa',
      }}
    >
      <Typography variant="body2" color="text.secondary" fontWeight={500}>
        Conversation in progress
      </Typography>
      <Tooltip title="Start a new conversation (clears chat history)">
        <Button
          size="small"
          startIcon={<RefreshIcon />}
          onClick={onNewConversation}
          disabled={disabled}
          sx={{
            textTransform: 'none',
            color: 'text.secondary',
            '&:hover': {
              bgcolor: 'rgba(0, 0, 0, 0.04)',
            },
          }}
        >
          New Conversation
        </Button>
      </Tooltip>
    </Box>
  );
}
