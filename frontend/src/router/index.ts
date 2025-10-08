// frontend/src/router/index.ts
import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import Home from "../pages/Home.vue";
import Accounts from "../pages/Accounts.vue";
import { ensureSignedIn, handleSigninCallback } from "../lib/oidc";

const routes: RouteRecordRaw[] = [
  // keeps your original route + name
  { path: "/", name: "home", component: Home },

  // keeps your original route + name; just marks it as protected
  { path: "/accounts", name: "accounts", component: Accounts, meta: { requiresAuth: true } },

  // new: OIDC redirect target (Okta sends the user back here with ?code=...)
  { path: "/signin-callback", name: "signin-callback", component: { template: "<div>Signing in…</div>" } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Minimal global guard: only enforces auth where required
router.beforeEach(async (to) => {
  // Handle the OAuth 2.0 Authorization Code + PKCE callback
  if (to.path === "/signin-callback") {
    await handleSigninCallback();        // processes ?code=... & stores tokens
    return { name: "accounts" };         // land somewhere useful post-login
  }

  // Protect pages flagged as requiring auth
  if (to.meta.requiresAuth) {
    await ensureSignedIn();              // triggers redirect to Okta if not signed in
  }

  return true;
});

export default router;