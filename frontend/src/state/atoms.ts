/**
 * Jotai atoms for global state management
 */
import { atom } from 'jotai';
import { atomWithStorage } from 'jotai/utils';
import type { Message, ChartStyle } from '../types';

// Generate a new session ID
export const generateNewSessionId = () => {
  const newId = `session-${Date.now()}-${Math.random().toString(36).substring(7)}`;
  localStorage.setItem('chart-app-session-id', newId);
  return newId;
};

// Get or generate initial session ID from localStorage
const getInitialSessionId = () => {
  const stored = localStorage.getItem('chart-app-session-id');
  if (stored) return stored;
  return generateNewSessionId();
};

// Session ID atom (persisted in localStorage)
export const sessionIdAtom = atom<string>(getInitialSessionId());

// Chat history atom
export const chatHistoryAtom = atom<Message[]>([]);

// Style preference atom (persisted in localStorage)
export const stylePreferenceAtom = atomWithStorage<ChartStyle>('chart-style-preference', 'fd');

// Current chart atom
export const currentChartAtom = atom<{ url: string; id: string } | null>(null);

// Loading state atom
export const isLoadingAtom = atom<boolean>(false);

// Error state atom
export const errorAtom = atom<string | null>(null);
