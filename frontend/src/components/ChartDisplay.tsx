/**
 * Chart display component - FD-inspired professional presentation
 */
import { useAtomValue } from "jotai";
import {
  Box,
  Typography,
  Button,
  ButtonGroup,
  Paper,
  Divider,
} from "@mui/material";
import DownloadIcon from "@mui/icons-material/Download";
import BarChartIcon from "@mui/icons-material/BarChart";
import { currentChartAtom } from "../state/atoms";

export default function ChartDisplay() {
  const currentChart = useAtomValue(currentChartAtom);

  if (!currentChart) {
    return (
      <Box
        sx={{
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          textAlign: "center",
          p: 4,
        }}
      >
        <BarChartIcon
          sx={{ fontSize: 64, color: "text.disabled", mb: 2, opacity: 0.3 }}
        />
        <Typography
          variant="h6"
          color="text.secondary"
          gutterBottom
          fontWeight={600}
        >
          No Chart Generated Yet
        </Typography>
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ maxWidth: 400 }}
        >
          Start by sending a chat message or uploading an Excel file. Your chart
          will appear here once generated.
        </Typography>
      </Box>
    );
  }

  const handleDownload = (format: "png" | "svg") => {
    const downloadUrl = currentChart.url.replace(/\.(png|svg)$/, `.${format}`);
    const link = document.createElement("a");
    link.href = downloadUrl;
    link.download = `chart-${currentChart.id}.${format}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Paper
      elevation={0}
      sx={{
        border: "1px solid",
        borderColor: "divider",
        borderRadius: 2,
        overflow: "hidden",
        height: "100%",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* Header */}
      <Box
        sx={{
          px: 3,
          py: 2,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          bgcolor: "#ffffff",
        }}
      >
        <Box>
          <Typography variant="h6" fontWeight={600}>
            Generated Chart
          </Typography>
          <Typography variant="caption" color="text.secondary">
            ID: {currentChart.id}
          </Typography>
        </Box>
        <ButtonGroup variant="outlined" size="small">
          <Button
            startIcon={<DownloadIcon />}
            onClick={() => handleDownload("png")}
            sx={{ textTransform: "none" }}
          >
            PNG
          </Button>
          <Button
            startIcon={<DownloadIcon />}
            onClick={() => handleDownload("svg")}
            sx={{ textTransform: "none" }}
          >
            SVG
          </Button>
        </ButtonGroup>
      </Box>

      <Divider />

      {/* Chart Image */}
      <Box
        sx={{
          flex: 1,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          bgcolor: "#fafafa",
          p: 3,
          overflow: "auto",
        }}
      >
        <img
          src={currentChart.url}
          alt="Generated chart"
          style={{
            maxWidth: "100%",
            maxHeight: "100%",
            height: "auto",
            objectFit: "contain",
          }}
        />
      </Box>
    </Paper>
  );
}
