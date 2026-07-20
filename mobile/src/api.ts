// Silver API client — talks to backend/main.py (FastAPI).
import AsyncStorage from '@react-native-async-storage/async-storage';
import Constants from 'expo-constants';

export const API_URL: string =
  (Constants.expoConfig?.extra?.apiUrl as string) || 'http://localhost:8000';

let token: string | null = null;

export async function loadToken(): Promise<string | null> {
  token = await AsyncStorage.getItem('silver_token');
  return token;
}

export async function setToken(value: string | null): Promise<void> {
  token = value;
  if (value) await AsyncStorage.setItem('silver_token', value);
  else await AsyncStorage.removeItem('silver_token');
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new ApiError(res.status, (data as any).detail ?? 'error');
  return data as T;
}

export const api = {
  get: <T>(path: string) => request<T>('GET', path),
  post: <T>(path: string, body?: unknown) => request<T>('POST', path, body),
  put: <T>(path: string, body?: unknown) => request<T>('PUT', path, body),
  del: <T>(path: string) => request<T>('DELETE', path),
};

export function mediaUrl(rel: string | null | undefined): string | undefined {
  if (!rel) return undefined;
  return rel.startsWith('http') ? rel : `${API_URL}${rel}`;
}

// ---- realtime (WebSocket) ----
function wsBase(): string {
  return API_URL.replace(/^http/, 'ws');
}

/** Per-user channel: message/notification events. Returns the socket (caller closes). */
export function openUserSocket(onEvent: (e: any) => void): WebSocket | null {
  if (!token) return null;
  try {
    const ws = new WebSocket(`${wsBase()}/ws?token=${token}`);
    ws.onmessage = (m) => {
      try { onEvent(JSON.parse(m.data as string)); } catch { /* ignore */ }
    };
    return ws;
  } catch {
    return null;
  }
}

/** Per-stream channel: live chat events. */
export function openLiveSocket(streamId: number, onEvent: (e: any) => void): WebSocket | null {
  if (!token) return null;
  try {
    const ws = new WebSocket(`${wsBase()}/ws/live/${streamId}?token=${token}`);
    ws.onmessage = (m) => {
      try { onEvent(JSON.parse(m.data as string)); } catch { /* ignore */ }
    };
    return ws;
  } catch {
    return null;
  }
}

/** Register this device's Expo push token with the backend (best-effort). */
export async function registerDevice(pushToken: string, platform: string): Promise<void> {
  try {
    await api.post('/devices', { push_token: pushToken, platform });
  } catch { /* best-effort */ }
}

export async function uploadFile(uri: string, name: string, type: string): Promise<{ path: string; url: string }> {
  const form = new FormData();
  // React Native FormData file object.
  form.append('file', { uri, name, type } as unknown as Blob);
  const headers: Record<string, string> = {};
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(`${API_URL}/upload`, { method: 'POST', headers, body: form });
  if (!res.ok) throw new ApiError(res.status, 'upload failed');
  return res.json();
}

// ---- typed payloads (subset of backend fields the UI uses) ----
export interface User {
  id: number;
  username: string;
  display_name: string;
  bio?: string;
  city?: string;
  role?: string;
  avatar_path?: string;
}

export interface Post {
  id: number;
  author_id: number;
  username: string;
  display_name: string;
  body: string;
  kind: string;
  likes: number;
  comment_count: number;
  liked: boolean;
  ai_generated: number;
  created_at: number;
  audiences: string[];
  media: { kind: string; url: string }[];
}

export interface Story {
  id: number;
  author_id: number;
  username: string;
  display_name: string;
  body: string;
  seen: number;
  media_url: string | null;
  media_kind: string | null;
}

export interface Conversation {
  id: number;
  is_request: number;
  unread: number;
  last_body: string | null;
  peer: User | null;
}

export interface Message {
  id: number;
  sender_id: number;
  body: string;
  media_path: string;
  story_id: number | null;
  post_id: number | null;
  created_at: number;
  display_name: string;
}

export interface Community {
  id: number;
  name: string;
  description: string;
  kind: string;
  member_count?: number;
  role?: string;
}

export interface Stream {
  id: number;
  host_id: number;
  title: string;
  description: string;
  status: string;
  display_name: string;
  username: string;
  viewer_count: number;
  comments_enabled: number;
  guests_enabled: number;
  comments?: { id: number; author_id: number; body: string; display_name: string; pinned: number }[];
  guests?: { user_id: number; status: string; display_name: string }[];
}

export interface Notification {
  id: number;
  kind: string;
  actor_name: string | null;
  read: number;
  created_at: number;
}

export interface Category {
  id: number;
  slug: string;
  name_ar: string;
  name_en: string;
}
