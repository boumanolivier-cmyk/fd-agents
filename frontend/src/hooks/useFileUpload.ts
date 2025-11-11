/**
 * Custom hook for file upload handling
 */
import { useState, useCallback } from "react";
import { useAtom, useAtomValue, useSetAtom } from "jotai";
import {
  sessionIdAtom,
  chatHistoryAtom,
  isLoadingAtom,
  currentChartAtom,
  errorAtom,
  stylePreferenceAtom,
} from "../state/atoms";
import { uploadExcelFile } from "../api/client";
import type { Message } from "../types";

export function useFileUpload() {
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useAtom(isLoadingAtom);
  const [error, setError] = useAtom(errorAtom);
  const sessionId = useAtomValue(sessionIdAtom);
  const setChatHistory = useSetAtom(chatHistoryAtom);
  const setCurrentChart = useSetAtom(currentChartAtom);
  const setStylePreference = useSetAtom(stylePreferenceAtom);

  const handleFile = useCallback(
    async (file: File) => {
      if (!file.name.match(/\.(xlsx|xls)$/)) {
        setError("Please upload an Excel file (.xlsx or .xls)");
        return;
      }

      setIsLoading(true);
      setError(null);
      setUploadedFileName(file.name);

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

        // Update style preference if agent selected a color scheme
        if (response.color_scheme) {
          setStylePreference(response.color_scheme);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to upload file");
        setUploadedFileName(null);
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

  return {
    dragActive,
    uploadedFileName,
    isLoading,
    error,
    setError,
    setUploadedFileName,
    handleDrag,
    handleDrop,
    handleChange,
  };
}
