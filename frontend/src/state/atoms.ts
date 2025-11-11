/**
 * Jotai atoms for global state management
 */
import { atom } from 'jotai';
import { atomWithStorage } from 'jotai/utils';
import type { Message, ChartStyle } from '../types';

// Generate or retrieve session ID from localStorage
const generateSessionId = () => {
  const stored = localStorage.getItem('chart-app-session-id');
  if (stored) return stored;

  const newId = `session-${Date.now()}-${Math.random().toString(36).substring(7)}`;
  localStorage.setItem('chart-app-session-id', newId);
  return newId;
};

// Session ID atom (persisted in localStorage)
export const sessionIdAtom = atom<string>(generateSessionId());

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
