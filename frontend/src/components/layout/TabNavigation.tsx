/**
 * Tab Navigation component
 */
import { Box, Tabs, Tab } from "@mui/material";
import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";
import UploadFileIcon from "@mui/icons-material/UploadFile";

interface TabNavigationProps {
  activeTab: number;
  onTabChange: (tab: number) => void;
}

export default function TabNavigation({
  activeTab,
  onTabChange,
}: TabNavigationProps) {
  return (
    <Box
      sx={{
        borderBottom: "1px solid",
        borderColor: "divider",
        bgcolor: "#fafafa",
      }}
    >
      <Tabs
        value={activeTab}
        onChange={(_, v) => onTabChange(v)}
        sx={{
          minHeight: 48,
          "& .MuiTabs-indicator": {
            height: 3,
          },
        }}
      >
        <Tab
          icon={<ChatBubbleOutlineIcon />}
          iconPosition="start"
          label="Chat Interface"
          sx={{ minHeight: 48 }}
        />
        <Tab
          icon={<UploadFileIcon />}
          iconPosition="start"
          label="Excel Upload"
          sx={{ minHeight: 48 }}
        />
      </Tabs>
    </Box>
  );
}
