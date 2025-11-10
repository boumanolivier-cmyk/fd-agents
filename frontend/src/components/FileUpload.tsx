/**
 * File upload component - FD-inspired clean interface
 */
import { useState, useCallback } from "react";
import { useAtom, useAtomValue, useSetAtom } from "jotai";
import {
  Box,
  Paper,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Chip,
} from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import DescriptionIcon from "@mui/icons-material/Description";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import InsertDriveFileIcon from "@mui/icons-material/InsertDriveFile";
import {
  sessionIdAtom,
  chatHistoryAtom,
  isLoadingAtom,
  currentChartAtom,
  errorAtom,
} from "../state/atoms";
import { uploadExcelFile } from "../api/client";
import type { Message } from "../types";

export default function FileUpload() {
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useAtom(isLoadingAtom);
  const [error, setError] = useAtom(errorAtom);
  const sessionId = useAtomValue(sessionIdAtom);
  const setChatHistory = useSetAtom(chatHistoryAtom);
  const setCurrentChart = useSetAtom(currentChartAtom);

  const handleFile = useCallback(
    async (file: File) => {
      if (!file.name.match(/\.(xlsx|xls)$/)) {
        setError("Please upload an Excel file (.xlsx or .xls)");
        return;
      }

      setIsLoading(true);
      setError(null);
      setUploadedFileName(file.name); // Show which file is being uploaded

      const userMessage: Message = {
        id: `msg-${Date.now()}`,
        role: "user",
        content: `Uploaded file: ${file.name}`,
        timestamp: Date.now(),
      };
      setChatHistory((prev) => [...prev, userMessage]);

      try {
        const response = await uploadExcelFile(file, sessionId);

        const assistantMessage: Message = {
          id: `msg-${Date.now() + 1}`,
          role: "assistant",
          content: response.response,
          chartUrl: response.chart_url,
          chartId: response.chart_id,
          timestamp: Date.now(),
        };

        setChatHistory((prev) => [...prev, assistantMessage]);

        if (response.chart_url && response.chart_id) {
          setCurrentChart({
            url: response.chart_url,
            id: response.chart_id,
          });
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to upload file");
        setUploadedFileName(null); // Clear filename on error
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId, setChatHistory, setCurrentChart, setIsLoading, setError]
  );

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  return (
    <Box>
      <Paper
        elevation={0}
        sx={{
          p: 5,
          textAlign: "center",
          border: 2,
          borderStyle: "dashed",
          borderColor: dragActive ? "primary.main" : "#e0e0e0",
          bgcolor: dragActive ? "rgba(55, 149, 150, 0.04)" : "#fafafa",
          borderRadius: 2,
          transition: "all 0.2s ease",
          cursor: isLoading ? "wait" : "pointer",
          "&:hover": {
            borderColor: isLoading ? "#e0e0e0" : "primary.light",
            bgcolor: isLoading ? "#fafafa" : "rgba(55, 149, 150, 0.02)",
          },
        }}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-upload"
          accept=".xlsx,.xls"
          onChange={handleChange}
          disabled={isLoading}
          style={{ display: "none" }}
        />

        <label
          htmlFor="file-upload"
          style={{ cursor: isLoading ? "wait" : "pointer" }}
        >
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 2,
            }}
          >
            {isLoading ? (
              <>
                <CircularProgress size={56} thickness={4} />
                <Typography variant="h6" fontWeight={600}>
                  Processing File...
                </Typography>
                {uploadedFileName && (
                  <Chip
                    icon={<InsertDriveFileIcon />}
                    label={uploadedFileName}
                    size="small"
                    sx={{
                      mt: 1,
                      bgcolor: "rgba(55, 149, 150, 0.1)",
                      color: "primary.main",
                      fontWeight: 500,
                    }}
                  />
                )}
                <Typography variant="body2" color="text.secondary">
                  Analyzing data and generating chart
                </Typography>
              </>
            ) : (
              <>
                <Box
                  sx={{
                    width: 72,
                    height: 72,
                    borderRadius: "50%",
                    bgcolor: "rgba(55, 149, 150, 0.1)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    mb: 1,
                  }}
                >
                  <DescriptionIcon
                    sx={{ fontSize: 36, color: "primary.main" }}
                  />
                </Box>

                <Typography variant="h6" fontWeight={600}>
                  Upload Excel File
                </Typography>

                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ maxWidth: 400 }}
                >
                  Drag and drop your Excel file here, or click to browse. We'll
                  automatically analyze your data and generate an appropriate
                  chart.
                </Typography>

                <Box sx={{ display: "flex", gap: 1, mt: 1 }}>
                  <Typography
                    variant="caption"
                    sx={{
                      px: 1.5,
                      py: 0.5,
                      bgcolor: "#ffffff",
                      border: "1px solid #e0e0e0",
                      borderRadius: 1,
                      fontWeight: 500,
                    }}
                  >
                    .xlsx
                  </Typography>
                  <Typography
                    variant="caption"
                    sx={{
                      px: 1.5,
                      py: 0.5,
                      bgcolor: "#ffffff",
                      border: "1px solid #e0e0e0",
                      borderRadius: 1,
                      fontWeight: 500,
                    }}
                  >
                    .xls
                  </Typography>
                </Box>

                <Button
                  variant="contained"
                  component="span"
                  startIcon={<CloudUploadIcon />}
                  sx={{
                    mt: 2,
                    textTransform: "none",
                    px: 3,
                    py: 1,
                    fontWeight: 600,
                  }}
                >
                  Choose File
                </Button>
              </>
            )}
          </Box>
        </label>
      </Paper>

      {/* Success notification */}
      {uploadedFileName && !isLoading && !error && (
        <Alert
          severity="success"
          icon={<CheckCircleIcon />}
          onClose={() => setUploadedFileName(null)}
          sx={{ mt: 2, borderRadius: 1 }}
        >
          Successfully uploaded and processed:{" "}
          <strong>{uploadedFileName}</strong>
        </Alert>
      )}

      {/* Error notification */}
      {error && (
        <Alert
          severity="error"
          onClose={() => setError(null)}
          sx={{ mt: 2, borderRadius: 1 }}
        >
          {error}
        </Alert>
      )}
    </Box>
  );
}
