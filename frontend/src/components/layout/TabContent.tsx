/**
 * Tab Content component - Displays content based on active tab
 */
import { Box } from '@mui/material';
import ChatInterface from '../ChatInterface';
import FileUpload from '../FileUpload';

interface TabContentProps {
  activeTab: number;
}

export default function TabContent({ activeTab }: TabContentProps) {
  return (
    <Box
      sx={{
        flex: 1,
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {activeTab === 0 && <ChatInterface />}
      {activeTab === 1 && (
        <Box sx={{ flex: 1, overflow: 'auto', p: 3 }}>
          <FileUpload />
        </Box>
      )}
    </Box>
  );
}
