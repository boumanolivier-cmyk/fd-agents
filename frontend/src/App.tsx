/**
 * Main App component - FD-inspired professional layout
 * Refactored into smaller layout components for better maintainability
 */
import { Box } from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { useState } from "react";
import AppHeader from "./components/layout/AppHeader";
import TabNavigation from "./components/layout/TabNavigation";
import TabContent from "./components/layout/TabContent";
import ChartOutputPanel from "./components/layout/ChartOutputPanel";
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
        <AppHeader />

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
              <TabNavigation activeTab={tab} onTabChange={setTab} />
              <TabContent activeTab={tab} />
            </Box>

            {/* Right Panel - Output Section */}
            <ChartOutputPanel />
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
