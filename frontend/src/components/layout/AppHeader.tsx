/**
 * App Header component
 */
import { AppBar, Toolbar, Box, Typography } from "@mui/material";

export default function AppHeader() {
  return (
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
  );
}
