// Real Chrome DOM/focus/navigation tests using a local API double. No npm dependencies.
// Run: node tests/web/password_modal.browser.mjs
// CHROME_PATH may select another installed Chromium executable.
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import os from "node:os";
const chromePath = process.env.CHROME_PATH || [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
].find(file => fs.existsSync(file));
assert.ok(chromePath, "Set CHROME_PATH to an installed Chromium browser");
const profile = fs.mkdtempSync(path.join(os.tmpdir(), "moveinmate-password-modal-"));
const sessions = new Set();
let required = true;
let accountUsername = "issued";
let usernameChangeRequired = true;
let password = "Issued-Password!";
let failure = "";
let passwordCalls = 0;
let businessCalls = 0;
let logouts = 0;
let serial = 0;
const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, "http://localhost");
  const reply = (status, data = {}) => {
    res.writeHead(status, { "Content-Type": "application/json", "Cache-Control": "no-store" });
    res.end(status === 204 ? undefined : JSON.stringify(data));
  };
  const token = req.headers.authorization?.replace("Bearer ", "");
  if (url.pathname.startsWith("/api/v1/")) {
    let body = "";
    for await (const chunk of req) body += chunk;
    const values = body ? JSON.parse(body) : {};
    if (url.pathname.endsWith("/auth/config")) return reply(200, { auth_mode: "required", auth_provider: "local", enabled: true });
    if (url.pathname.endsWith("/auth/login-hints")) return reply(200, { visible: false, accounts: [] });
    if (url.pathname.endsWith("/auth/login")) {
      if (values.password !== password || values.username !== accountUsername) return reply(401, { detail: { message: "Tên đăng nhập hoặc mật khẩu không đúng." } });
      const access_token = `test-session-${++serial}`;
      sessions.add(access_token);
      return reply(200, { access_token, expires_in: 3600, password_change_required: required });
    }
    if (!sessions.has(token)) return reply(401, { detail: { code: "token_expired" } });
    if (url.pathname.endsWith("/me/context")) return reply(200, {
      username: accountUsername, username_change_required: usernameChangeRequired, user_id: "issued", roles: ["resident"], resident_id: "R001",
      resident_ids: ["R001"], site_ids: ["sunrise-residence"], manager_site_ids: [],
      password_change_required: required, demo_reset_enabled: false,
    });
    if (url.pathname.endsWith("/auth/logout")) { logouts += 1; sessions.delete(token); return reply(204); }
    if (url.pathname.endsWith("/auth/username-availability")) return reply(200, { available: !["taken", "admin", ...(usernameChangeRequired ? [accountUsername] : [])].includes(values.username) });
    if (url.pathname.endsWith("/auth/password/first-login")) {
      passwordCalls += 1;
      await new Promise(resolve => setTimeout(resolve, 150));
      if (failure === "network") { res.destroy(); return; }
      if (failure) return reply(500, { detail: "Máy chủ tạm thời không khả dụng." });
      if (["taken", "admin"].includes(values.username)) return reply(409, { detail: "username_unavailable" });
      if (Object.hasOwn(values, "current_password")) return reply(422, { detail: "unexpected_password" });
      if (values.new_password.length < 8 || !values.new_password.trim() || values.new_password === password) return reply(422, { detail: "new_password_invalid" });
      password = values.new_password;
      accountUsername = values.username;
      usernameChangeRequired = false;
      required = false;
      sessions.clear(); // Mirrors the existing credential_tag invalidation.
      return reply(204);
    }
    businessCalls += 1;
    if (required) return reply(403, { detail: { code: "password_change_required", message: "Bạn cần đổi mật khẩu được cấp." } });
    if (url.pathname.endsWith("/health")) return reply(200, { status: "configuration_required" });
    if (url.pathname.endsWith("/household")) return reply(200, { profile: {}, vehicles: [], parking_reminders: [] });
    return reply(200, { items: [], tasks: [], total: 0, completed: 0, events: [], unread_count: 0 });
  }
  const relative = url.pathname === "/" ? "index.html" : url.pathname.replace(/^\/static\//, "");
  const file = path.resolve("web", relative);
  if (!file.startsWith(path.resolve("web") + path.sep) || !fs.existsSync(file)) return reply(404);
  const types = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".svg": "image/svg+xml" };
  res.writeHead(200, { "Content-Type": types[path.extname(file)] || "application/octet-stream", "Cache-Control": "no-store" });
  res.end(fs.readFileSync(file));
});
await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
const origin = `http://127.0.0.1:${server.address().port}`;
const chrome = spawn(chromePath, ["--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
  "--no-sandbox", "--disable-background-networking",
  "--remote-debugging-port=0", `--user-data-dir=${profile}`, "about:blank"], { windowsHide: true, stdio: "ignore" });
let socket;
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const until = async (predicate, label) => {
  const deadline = Date.now() + 10000;
  while (Date.now() < deadline) { if (await predicate()) return; await sleep(50); }
  throw new Error(`Timed out: ${label}`);
};
try {
  const portFile = path.join(profile, "DevToolsActivePort");
  await until(() => fs.existsSync(portFile), "Chrome launch");
  const port = fs.readFileSync(portFile, "utf8").split(/\r?\n/)[0];
  const pages = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
  socket = new WebSocket(pages.find(page => page.type === "page").webSocketDebuggerUrl);
  await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
  let id = 0;
  const pending = new Map();
  const exceptions = [];
  socket.onmessage = event => {
    const message = JSON.parse(event.data);
    if (message.method === "Runtime.exceptionThrown") exceptions.push(message.params.exceptionDetails.text);
    if (message.id) { const waiter = pending.get(message.id); pending.delete(message.id); if (!waiter) return; clearTimeout(waiter.timer); message.error ? waiter.reject(message.error) : waiter.resolve(message.result); }
  };
  const cdp = (method, params = {}) => new Promise((resolve, reject) => {
    const callId = ++id;
    const timer = setTimeout(() => { pending.delete(callId); reject(new Error(`CDP timeout: ${method} ${params.expression?.slice(0, 100) || ""}`)); }, 10000);
    pending.set(callId, { resolve, reject, timer });
    socket.send(JSON.stringify({ id: callId, method, params }));
  });
  const evaluate = async expression => {
    const result = await cdp("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true });
    assert.ok(!result.exceptionDetails, result.exceptionDetails?.exception?.description);
    return result.result.value;
  };
  const open = async (hash = "") => {
    await cdp("Page.navigate", { url: origin + "/" + hash });
    await until(() => evaluate('typeof authConfig !== "undefined" && authConfig !== null'), "auth config");
  };
  const dialogOpen = () => evaluate('document.getElementById("first-password-dialog")?.open === true');
  const login = async value => {
    await until(() => evaluate('!document.getElementById("login-form").hidden'), "login form");
    await evaluate(`document.getElementById("login-username").value = ${JSON.stringify(accountUsername)}; document.getElementById("login-password").value = ${JSON.stringify(value)}; document.getElementById("login-form").requestSubmit()`);
  };
  const fill = async (username = usernameChangeRequired ? "my.name" : accountUsername, next = "New-Private-Password!", confirmation = next) => {
    await evaluate(`
    document.getElementById("first-password-form").elements.username.value = ${JSON.stringify(username)};
    document.getElementById("first-password-form").elements.username.dispatchEvent(new Event("input", { bubbles: true }));
    document.getElementById("first-password-form").elements.new_password.value = "";
    document.getElementById("first-password-form").elements.new_password.focus();
    document.getElementById("first-password-form").elements.confirm_password.value = ${JSON.stringify(confirmation)};
    `);
    // Native minlength applies to user input, not JavaScript-assigned values.
    await cdp("Input.insertText", { text: next });
  };
  const submit = () => evaluate('document.getElementById("first-password-form").requestSubmit()');
  const errorShown = () => evaluate('!document.getElementById("first-password-error").hidden');
  await cdp("Runtime.enable");
  await cdp("Page.enable");
  await open("#tickets");
  // An unverified session cannot call any business API.
  assert.equal(await evaluate('api("/locations").then(() => false, () => true)'), true);
  assert.equal(businessCalls, 0);
  await login("incorrect");
  await until(() => evaluate('!document.getElementById("auth-error").hidden'), "invalid login error");
  await login(password);
  await until(dialogOpen, "mandatory dialog");
  console.log("PASS: initial login shows locked Dashboard and modal");
  assert.equal(await evaluate('!document.getElementById("main-content").hidden && document.getElementById("auth-screen").hidden'), true);
  assert.equal(await evaluate('document.getElementById("main-content").inert && document.querySelector("body > header").inert'), true);
  assert.equal(await evaluate('document.getElementById("agent").classList.contains("active") && location.hash === "" && !authReady'), true);
  assert.equal(businessCalls, 0);
  await cdp("Input.dispatchKeyEvent", { type: "keyDown", key: "Escape", code: "Escape", windowsVirtualKeyCode: 27 });
  assert.equal(await dialogOpen(), true);
  for (const type of ["mousePressed", "mouseReleased"]) await cdp("Input.dispatchMouseEvent", { type, x: 2, y: 2, button: "left", clickCount: 1 });
  assert.equal(await dialogOpen(), true);
  await evaluate('document.getElementById("first-password-cancel").focus()');
  await cdp("Input.dispatchKeyEvent", { type: "keyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
  assert.equal(await evaluate('document.activeElement.name'), "username");
  await cdp("Input.dispatchKeyEvent", { type: "keyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9, modifiers: 8 });
  assert.equal(await evaluate('document.activeElement.id'), "first-password-cancel");
  await evaluate('document.getElementById("user-role").focus(); document.getElementById("tab-tickets").click()');
  assert.equal(await evaluate('document.getElementById("first-password-dialog").contains(document.activeElement) && document.getElementById("agent").classList.contains("active")'), true);
  await evaluate('location.hash = "#household"');
  await until(() => evaluate('location.hash === ""'), "hash guard");
  await cdp("Page.reload");
  await until(dialogOpen, "refresh retains requirement");
  for (const query of ["?history=1#tickets", "?history=2#household"]) {
    await cdp("Page.navigate", { url: `${origin}/${query}` });
    await until(dialogOpen, "direct service URL remains locked");
  }
  const history = await cdp("Page.getNavigationHistory");
  await cdp("Page.navigateToHistoryEntry", { entryId: history.entries[history.currentIndex - 1].id });
  await until(() => evaluate('location.search === "?history=1" && document.getElementById("first-password-dialog")?.open === true && !authReady'), "Back remains locked");
  await cdp("Page.navigateToHistoryEntry", { entryId: history.entries[history.currentIndex].id });
  await until(() => evaluate('location.search === "?history=2" && document.getElementById("first-password-dialog")?.open === true && !authReady'), "Forward remains locked");
  for (const [width, height] of [[1280, 900], [768, 1024], [390, 844], [320, 568]]) {
    await cdp("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: width < 768 });
    await sleep(450); // Allow the existing dialog entrance animation to settle.
    const bounds = await evaluate('(() => { const r = document.getElementById("first-password-dialog").getBoundingClientRect(); return {x:r.x,y:r.y,width:r.width,height:r.height,vw:innerWidth,vh:innerHeight}; })()');
    assert.ok(bounds.x >= 0 && bounds.y >= 0 && bounds.width <= bounds.vw && bounds.height <= bounds.vh);
    assert.ok(Math.abs(bounds.x + bounds.width / 2 - bounds.vw / 2) < 2);
    assert.ok(Math.abs(bounds.y + bounds.height / 2 - bounds.vh / 2) < 2, JSON.stringify(bounds));
  }
  if (process.env.MODAL_SCREENSHOT) {
    const screenshot = await cdp("Page.captureScreenshot", { format: "png" });
    fs.writeFileSync(process.env.MODAL_SCREENSHOT, Buffer.from(screenshot.data, "base64"));
  }
  console.log("PASS: native focus trap, ESC/backdrop, direct URL/refresh/Back/Forward and mobile bounds");
  // Native validity and confirmation errors must not send a request.
  assert.equal(await evaluate('document.querySelector("#first-password-form [name=current_password]") === null'), true);
  await evaluate('document.querySelector("[data-password-toggle=first-password-new]").click()');
  assert.equal(await evaluate('document.getElementById("first-password-new").type'), "text");
  await evaluate('document.querySelector("[data-password-toggle=first-password-new]").click()');
  assert.equal(await evaluate('document.getElementById("first-password-new").type'), "password");
  assert.equal(await evaluate('document.documentElement.dataset.theme'), "dark");
  assert.equal(await evaluate('getComputedStyle(document.getElementById("first-password-cancel")).borderColor'), "rgb(94, 131, 168)");
  await evaluate('document.getElementById("appearance-toggle").click()');
  await until(() => evaluate('document.documentElement.dataset.theme === "light" && getComputedStyle(document.getElementById("first-password-cancel")).borderColor === "rgb(181, 209, 236)"'), "light theme modal colors");
  assert.equal(await evaluate('getComputedStyle(document.getElementById("first-password-cancel")).borderColor'), "rgb(181, 209, 236)");
  await fill("issued", "short"); await submit(); assert.equal(passwordCalls, 0);
  await fill("issued", "New-Private-Password!", "Mismatch!"); await submit(); assert.equal(passwordCalls, 0);
  assert.equal(await errorShown(), true);
  await fill("taken"); await submit(); await until(() => evaluate('!document.getElementById("first-password-username-error").hidden'), "duplicate username");
  assert.equal(passwordCalls, 0);
  assert.match(await evaluate('document.getElementById("first-password-username-error").textContent'), /đã được sử dụng/);
  assert.equal(await evaluate('document.getElementById("first-password-username").getAttribute("aria-invalid")'), "true");
  assert.equal(await evaluate('getComputedStyle(document.getElementById("first-password-username-error")).color'), "rgb(180, 35, 24)");
  assert.equal(await dialogOpen(), true);
  for (const kind of ["server", "network"]) {
    failure = kind;
    await fill(); await submit(); await until(errorShown, `${kind} error`);
    assert.equal(await dialogOpen(), true);
    assert.equal(await evaluate('document.getElementById("main-content").inert'), true);
  }
  failure = "";
  // Modifying client state cannot bypass the server's restriction.
  await evaluate('authReady = true; authContext.password_change_required = false; localStorage.setItem("mustChangePassword", "false"); api("/locations").catch(() => {})');
  await until(() => evaluate('!authReady && authContext.password_change_required'), "server restriction resynchronizes UI");
  assert.equal(await dialogOpen(), true);
  // Logout uses the existing revocation endpoint.
  await evaluate('document.getElementById("first-password-cancel").click()');
  await until(() => evaluate('!document.getElementById("login-form").hidden'), "logout returns to login");
  assert.equal(logouts, 1);
  console.log("PASS: validation/errors, client tampering and safe logout");
  await login(password); await until(dialogOpen, "login after logout");
  const before = passwordCalls;
  await fill();
  await evaluate('document.getElementById("first-password-form").requestSubmit(); document.getElementById("first-password-form").requestSubmit()');
  assert.equal(await evaluate('document.getElementById("first-password-submit").disabled'), true);
  await until(() => evaluate('authReady && !document.getElementById("first-password-dialog").open'), "password success unlocks dashboard");
  assert.equal(passwordCalls, before + 1);
  assert.equal(await evaluate('document.getElementById("main-content").inert'), false);
  assert.equal(await evaluate('authContext.roles.join(",")'), "resident");
  assert.equal(await evaluate('authContext.username'), "my.name");
  assert.equal(accountUsername, "my.name");
  await cdp("Page.reload");
  await until(() => evaluate('typeof authReady !== "undefined" && authReady'), "new session survives refresh");
  assert.equal(await dialogOpen(), false);
  await evaluate('void signOut()');
  await until(() => evaluate('!document.getElementById("login-form").hidden'), "normal logout");
  await login(password);
  await until(() => evaluate('authReady'), "subsequent login with new password");
  assert.equal(await dialogOpen(), false);
  // Apply the existing requirement again, then expire its session while the form is open.
  required = true;
  await evaluate('api("/locations").catch(() => {})');
  await until(dialogOpen, "reapplied requirement");
  sessions.clear();
  await fill(accountUsername, "Another-Private-Password!"); await submit();
  await until(() => evaluate('!document.getElementById("login-form").hidden'), "expired token returns to login");
  assert.equal(await dialogOpen(), false);
  assert.equal(required, true);
  assert.deepEqual(exceptions, []);
  console.log("PASS: real Chrome modal, focus, ESC/backdrop, mobile, URL/refresh, validation, errors, duplicate submit, token rotation, logout, expired session and client tampering (mock API).");
} finally {
  socket?.close();
  chrome.kill();
  server.closeAllConnections();
  await new Promise(resolve => server.close(resolve));
  // Chrome profile is intentionally left in OS temp; no recursive cleanup of browser files.
}
