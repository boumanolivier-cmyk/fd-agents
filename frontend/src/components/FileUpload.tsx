/**
 * File upload component - FD-inspired clean interface
 * Refactored into smaller components for better maintainability
 */
import { Box } from '@mui/material';
import DropZone from './upload/DropZone';
import UploadStatus from './upload/UploadStatus';
import { useFileUpload } from '../hooks/useFileUpload';

export default function FileUpload() {
  const {
    dragActive,
    uploadedFileName,
    isLoading,
    error,
    setError,
    setUploadedFileName,
    handleDrag,
    handleDrop,
    handleChange,
  } = useFileUpload();

  return (
    <Box>
      <DropZone
        dragActive={dragActive}
        isLoading={isLoading}
        uploadedFileName={uploadedFileName}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onFileChange={handleChange}
      />

      <UploadStatus
        uploadedFileName={uploadedFileName}
        isLoading={isLoading}
        error={error}
        onClearFileName={() => setUploadedFileName(null)}
        onClearError={() => setError(null)}
      />
    </Box>
  );
}
