// frontend/src/lib/api.ts
import { oidc } from "./oidc";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * Build headers for a JSON request, optionally including the OIDC access token.
 * We keep this separate so you can unit-test header logic easily.
 */
async function buildJsonHeaders(init?: RequestInit): Promise<Headers> {
  const headers = new Headers(init?.headers || {});
  // Always ensure JSON content-type unless caller overrode it
  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  // If the user is signed in and has an access token, attach it
  // (oidc-client-ts manages the browser session and tokens for you)
  const user = await oidc.getUser(); // returns null if not signed-in/expired
  if (user?.access_token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${user.access_token}`);
  }

  return headers;
}

/**
 * Typed JSON fetch with OIDC token support.
 * - Preserves your original error handling and generic return type.
 * - Adds Authorization header automatically when a token is available.
 */
export async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = await buildJsonHeaders(init);

  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
  });

  // If unauthorized/forbidden, clear local user and force a fresh sign-in
  if (res.status === 401 || res.status === 403) {
    try {
      await oidc.removeUser();
    } finally {
      await oidc.signinRedirect();
    }
    throw new Error(`HTTP ${res.status}: unauthorized`);
  }

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text}`);
  }

  if (res.status === 204) return undefined as unknown as T;

  return (await res.json()) as T;
}

/**
 * Convenience helpers (optional):
 * These mirror common patterns but are purely optional sugar.
 */
export const api = {
  get: <T>(path: string, init?: RequestInit) =>
    fetchJson<T>(path, { ...init, method: "GET" }),
  post: <T>(path: string, body?: unknown, init?: RequestInit) =>
    fetchJson<T>(path, {
      ...init,
      method: "POST",
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }),
  put: <T>(path: string, body?: unknown, init?: RequestInit) =>
    fetchJson<T>(path, {
      ...init,
      method: "PUT",
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }),
  patch: <T>(path: string, body?: unknown, init?: RequestInit) =>
    fetchJson<T>(path, {
      ...init,
      method: "PATCH",
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }),
  delete: <T>(path: string, init?: RequestInit) =>
    fetchJson<T>(path, { ...init, method: "DELETE" }),
};