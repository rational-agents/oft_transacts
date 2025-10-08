// frontend/src/lib/oidc.ts
import { UserManager, WebStorageStateStore, Log } from "oidc-client-ts";

const authority = import.meta.env.VITE_OIDC_ISSUER;          // e.g., https://your-tenant.auth0.com
const client_id = import.meta.env.VITE_OIDC_CLIENT_ID;       // SPA client id at your IdP
const redirect_uri = window.location.origin + "/signin-callback";
const post_logout_redirect_uri = window.location.origin + "/";
const scope = "openid profile email";                         // add API-specific scopes if configured

Log.setLevel(Log.NONE); // use Log.DEBUG locally

export const oidc = new UserManager({
  authority,
  client_id,
  redirect_uri,
  post_logout_redirect_uri,
  response_type: "code", // Authorization Code
  scope,
  userStore: new WebStorageStateStore({ store: window.sessionStorage }),
  // PKCE is on by default in oidc-client-ts
});

export async function ensureSignedIn() {
  const user = await oidc.getUser();
  if (!user || user.expired) {
    await oidc.signinRedirect();
    return;
  }
  return user;
}

export async function handleSigninCallback() {
  return oidc.signinCallback();
}

export async function signOut() {
  await oidc.signoutRedirect();
}