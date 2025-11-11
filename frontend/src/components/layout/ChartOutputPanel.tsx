/**
 * Chart Output Panel component - Right side panel with chart display and style selector
 */
import { Box } from '@mui/material';
import ChartDisplay from '../ChartDisplay';
import StyleSelector from '../StyleSelector';

export default function ChartOutputPanel() {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        bgcolor: '#fafafa',
        overflow: 'hidden',
      }}
    >
      {/* Chart Display Area */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 3 }}>
        <ChartDisplay />
      </Box>

      {/* Style Selector at Bottom */}
      <Box
        sx={{
          borderTop: '1px solid',
          borderColor: 'divider',
          p: 2,
          bgcolor: 'background.paper',
        }}
      >
        <StyleSelector />
      </Box>
    </Box>
  );
}
