/**
 * API client for communicating with the FastAPI backend
 */
import axios from "axios";
import type {
  ChatRequest,
  ChatResponse,
  UploadResponse,
  StylePreference,
  ChartStyle,
} from "../types";

const api = axios.create({
  baseURL: "", // Using Vite proxy, so we don't need a base URL
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Send a chat message to create a chart
 */
export const sendChatMessage = async (
  message: string,
  sessionId: string
): Promise<ChatResponse> => {
  const response = await api.post<ChatResponse>("/api/chat", {
    message,
    session_id: sessionId,
  } as ChatRequest);

  return response.data;
};

/**
 * Upload an Excel file
 */
export const uploadExcelFile = async (
  file: File,
  sessionId: string
): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("session_id", sessionId);

  const response = await api.post<UploadResponse>("/api/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
};

/**
 * Get style preference for a session
 */
export const getStylePreference = async (
  sessionId: string
): Promise<ChartStyle> => {
  const response = await api.get<StylePreference>(
    `/api/preferences/${sessionId}`
  );
  return response.data.style;
};

/**
 * Set style preference for a session
 */
export const setStylePreference = async (
  sessionId: string,
  style: ChartStyle
): Promise<void> => {
  await api.post(`/api/preferences/${sessionId}`, {
    style,
  } as StylePreference);
};

/**
 * Clear chat history for a session (start new conversation)
 */
export const clearChatHistory = async (sessionId: string): Promise<void> => {
  await api.delete(`/api/chat/${sessionId}`);
};

/**
 * Get chart URL for display
 */
export const getChartUrl = (
  chartId: string,
  format: "png" | "svg" = "png"
): string => {
  return `/charts/${chartId}.${format}`;
};

export default api;
