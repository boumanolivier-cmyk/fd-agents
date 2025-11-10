/**
 * Main App component - FD-inspired professional layout
 */
import { Box, Typography, AppBar, Toolbar, Tabs, Tab } from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { useState } from "react";
import ChatInterface from "./components/ChatInterface";
import FileUpload from "./components/FileUpload";
import ChartDisplay from "./components/ChartDisplay";
import StyleSelector from "./components/StyleSelector";
import "./App.css";

const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#379596",
      light: "#5ab0b1",
      dark: "#2d7a7b",
    },
    background: {
      default: "#fafafa",
      paper: "#ffffff",
    },
    text: {
      primary: "#1a1a1a",
      secondary: "#666666",
    },
    divider: "#e0e0e0",
  },
  typography: {
    fontFamily:
      "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif",
    h6: {
      fontWeight: 600,
      letterSpacing: "-0.01em",
    },
    body1: {
      lineHeight: 1.6,
    },
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: "none",
          borderBottom: "1px solid #e0e0e0",
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: "none",
          fontWeight: 500,
          fontSize: "0.95rem",
        },
      },
    },
  },
});

function App() {
  const [tab, setTab] = useState(0);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          height: "100vh",
          overflow: "hidden",
        }}
      >
        {/* Professional Header */}
        <AppBar position="static" color="inherit" className="app-header">
          <Toolbar sx={{ borderBottom: "1px solid", borderColor: "divider" }}>
            <Box
              sx={{
                display: "flex",
                alignItems: "baseline",
                gap: 1,
                flexGrow: 1,
              }}
            >
              <Typography
                variant="h6"
                component="h1"
                sx={{
                  color: "primary.main",
                  fontWeight: 700,
                  letterSpacing: "-0.02em",
                }}
              >
                AI Chart Generator
              </Typography>
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{ display: { xs: "none", sm: "block" } }}
              >
                Professional data visualization powered by AI
              </Typography>
            </Box>
          </Toolbar>
        </AppBar>

        {/* Full-width Main Content Grid */}
        <Box className="app-container">
          <Box className="main-content">
            {/* Left Panel - Input Section */}
            <Box
              sx={{
                display: "flex",
                flexDirection: "column",
                height: "100%",
                bgcolor: "background.paper",
                borderRight: { md: "1px solid" },
                borderColor: { md: "divider" },
                overflow: "hidden",
              }}
            >
              {/* Tab Navigation */}
              <Box
                sx={{
                  borderBottom: "1px solid",
                  borderColor: "divider",
                  bgcolor: "#fafafa",
                }}
              >
                <Tabs
                  value={tab}
                  onChange={(_, v) => setTab(v)}
                  sx={{
                    minHeight: 48,
                    "& .MuiTabs-indicator": {
                      height: 3,
                    },
                  }}
                >
                  <Tab label="Chat Interface" sx={{ minHeight: 48 }} />
                  <Tab label="Excel Upload" sx={{ minHeight: 48 }} />
                </Tabs>
              </Box>

              {/* Tab Content */}
              <Box
                sx={{
                  flex: 1,
                  overflow: "hidden",
                  display: "flex",
                  flexDirection: "column",
                }}
              >
                {tab === 0 && <ChatInterface />}
                {tab === 1 && (
                  <Box sx={{ flex: 1, overflow: "auto", p: 3 }}>
                    <FileUpload />
                  </Box>
                )}
              </Box>
            </Box>

            {/* Right Panel - Output Section */}
            <Box
              sx={{
                display: "flex",
                flexDirection: "column",
                height: "100%",
                bgcolor: "#fafafa",
                overflow: "hidden",
              }}
            >
              {/* Chart Display Area */}
              <Box sx={{ flex: 1, overflow: "auto", p: 3 }}>
                <ChartDisplay />
              </Box>

              {/* Style Selector at Bottom */}
              <Box
                sx={{
                  borderTop: "1px solid",
                  borderColor: "divider",
                  p: 2,
                  bgcolor: "background.paper",
                }}
              >
                <StyleSelector />
              </Box>
            </Box>
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
