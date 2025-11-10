/**
 * Drop Zone component - Drag and drop file upload interface
 */
import { Box, Paper, Typography, Button, CircularProgress, Chip } from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import DescriptionIcon from "@mui/icons-material/Description";
import InsertDriveFileIcon from "@mui/icons-material/InsertDriveFile";

interface DropZoneProps {
  dragActive: boolean;
  isLoading: boolean;
  uploadedFileName: string | null;
  onDragEnter: (e: React.DragEvent) => void;
  onDragLeave: (e: React.DragEvent) => void;
  onDragOver: (e: React.DragEvent) => void;
  onDrop: (e: React.DragEvent) => void;
  onFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

export default function DropZone({
  dragActive,
  isLoading,
  uploadedFileName,
  onDragEnter,
  onDragLeave,
  onDragOver,
  onDrop,
  onFileChange,
}: DropZoneProps) {
  return (
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
      onDragEnter={onDragEnter}
      onDragLeave={onDragLeave}
      onDragOver={onDragOver}
      onDrop={onDrop}
    >
      <input
        type="file"
        id="file-upload"
        accept=".xlsx,.xls"
        onChange={onFileChange}
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
  );
}
