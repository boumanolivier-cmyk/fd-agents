/**
 * Custom hook for chat message handling
 */
import { useState } from "react";
import { useAtom, useAtomValue, useSetAtom } from "jotai";
import {
  sessionIdAtom,
  chatHistoryAtom,
  isLoadingAtom,
  currentChartAtom,
  errorAtom,
  stylePreferenceAtom,
} from "../state/atoms";
import { sendChatMessage, clearChatHistory } from "../api/client";
import type { Message } from "../types";

export function useChatMessages() {
  const [input, setInput] = useState("");
  const [chatHistory, setChatHistory] = useAtom(chatHistoryAtom);
  const [isLoading, setIsLoading] = useAtom(isLoadingAtom);
  const [error, setError] = useAtom(errorAtom);
  const sessionId = useAtomValue(sessionIdAtom);
  const setCurrentChart = useSetAtom(currentChartAtom);
  const setStylePreference = useSetAtom(stylePreferenceAtom);

  const handleNewConversation = async () => {
    try {
      await clearChatHistory(sessionId);
      setChatHistory([]);
      setCurrentChart(null);
      setError(null);
      setInput("");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to clear conversation"
      );
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: "user",
      content: input,
      timestamp: Date.now(),
    };

    setChatHistory((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    setError(null);

    try {
      const response = await sendChatMessage(input, sessionId);

      const assistantMessage: Message = {
        id: `msg-${Date.now()}`,
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
      setError(err instanceof Error ? err.message : "Failed to send message");
    } finally {
      setIsLoading(false);
    }
  };

  return {
    input,
    setInput,
    chatHistory,
    isLoading,
    error,
    setError,
    handleSend,
    handleNewConversation,
  };
}
