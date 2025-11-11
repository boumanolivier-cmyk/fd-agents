/**
 * TypeScript type definitions for the application
 */

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  chartUrl?: string;
  chartId?: string;
  timestamp: number;
}

export interface ChatRequest {
  message: string;
  session_id: string;
}

export interface ChatResponse {
  response: string;
  chart_url?: string;
  chart_id?: string;
  color_scheme?: ChartStyle;
}

export interface UploadResponse {
  response: string;
  chart_url?: string;
  chart_id?: string;
  color_scheme?: ChartStyle;
}

export interface StylePreference {
  style: 'fd' | 'bnr';
}

export type ChartStyle = 'fd' | 'bnr';

export interface ChartData {
  id: string;
  url: string;
  style: ChartStyle;
  timestamp: number;
}
