/**
 * Upload Status component - Shows success or error messages
 */
import { Alert } from "@mui/material";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";

interface UploadStatusProps {
  uploadedFileName: string | null;
  isLoading: boolean;
  error: string | null;
  onClearFileName: () => void;
  onClearError: () => void;
}

export default function UploadStatus({
  uploadedFileName,
  isLoading,
  error,
  onClearFileName,
  onClearError,
}: UploadStatusProps) {
  return (
    <>
      {uploadedFileName && !isLoading && !error && (
        <Alert
          severity="success"
          icon={<CheckCircleIcon />}
          onClose={onClearFileName}
          sx={{ mt: 2, borderRadius: 1 }}
        >
          Successfully uploaded and processed:{" "}
          <strong>{uploadedFileName}</strong>
        </Alert>
      )}

      {error && (
        <Alert
          severity="error"
          onClose={onClearError}
          sx={{ mt: 2, borderRadius: 1 }}
        >
          {error}
        </Alert>
      )}
    </>
  );
}
