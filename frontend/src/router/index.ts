// frontend/src/router/index.ts
import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import Home from "../pages/Home.vue";
import Accounts from "../pages/Accounts.vue";
import { ensureSignedIn, handleSigninCallback } from "../lib/oidc";

const routes: RouteRecordRaw[] = [
  { path: "/", name: "home", component: Home },
  { path: "/accounts", name: "accounts", component: Accounts, meta: { requiresAuth: true } },
  { path: "/signin-callback", name: "signin-callback", component: { template: "<div>Signing in…</div>" } },
  { path: "/logged-out", name: "logged-out", component: () => import("../pages/LoggedOut.vue") },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to) => {
  // Handle the OAuth 2.0 Authorization Code + PKCE callback and restore intended path
  if (to.path === "/signin-callback") {
    await handleSigninCallback();
    const dest = sessionStorage.getItem("post_login_redirect") || "/accounts";
    sessionStorage.removeItem("post_login_redirect");
    return dest;
  }

  // Protect pages flagged as requiring auth
  if (to.meta.requiresAuth) {
    // Remember where we were going, in case we need to leave to Okta
    sessionStorage.setItem("post_login_redirect", to.fullPath);
    await ensureSignedIn();
  }

  return true;
});

export default router;