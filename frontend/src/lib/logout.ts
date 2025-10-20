// frontend/src/lib/logout.ts
import { oidc } from "./oidc";

async function clearAllClientState() {
  try {
    sessionStorage.clear();
    localStorage.clear();

    if ("caches" in window) {
      const names = await caches.keys();
      await Promise.all(names.map((n) => caches.delete(n)));
    }

    // best-effort IndexedDB purge
    try {
      const dblist = await (indexedDB as any).databases?.() ?? [];
      await Promise.all(
        dblist.map((db: any) => new Promise<void>((resolve) => {
          const req = indexedDB.deleteDatabase(db.name);
          req.onsuccess = req.onerror = req.onblocked = () => resolve();
        }))
      );
    } catch {
      // Fallback would be deleting known DB names, if any.
    }
  } catch {
    // best-effort
  }
}

export async function hardLogout() {
  // Capture id_token BEFORE clearing session storage so we can supply id_token_hint
  const user = await oidc.getUser().catch(() => null);
  const idToken = user?.id_token;
  const postLogout = window.location.origin + "/logged-out";

  // Best-effort local cleanup first
  await clearAllClientState();

  // Ask backend to send Clear-Site-Data for its origin (defense-in-depth)
  try {
    await fetch(`${import.meta.env.VITE_API_BASE_URL}/logout`, {
      method: "POST",
      mode: "cors",
      cache: "no-store",
      credentials: "omit",
    });
  } catch {
    // ignore
  }

  // 3) OIDC end-session: Okta will redirect to /logged-out
  await oidc.signoutRedirect(
    idToken
      ? { id_token_hint: idToken, post_logout_redirect_uri: postLogout }
      : { post_logout_redirect_uri: postLogout }
  );
}