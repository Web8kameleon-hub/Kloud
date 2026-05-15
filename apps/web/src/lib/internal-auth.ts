import { randomBytes, randomInt, createHmac, pbkdf2Sync, timingSafeEqual } from "crypto";
import { promises as fs } from "fs";
import path from "path";
import { writeAuthStigmaEvent } from "@/lib/stigma-memory";

export type AuthChannel = "sms" | "email";

export type InternalUser = {
  id: string;
  name: string;
  email: string | null;
  phone: string | null;
  passwordHash: string;
  passwordSalt: string;
  emailVerified: boolean;
  phoneVerified: boolean;
  googleLinked: boolean;
  createdAt: string;
  updatedAt: string;
};

type OtpChallenge = {
  id: string;
  userId: string;
  channel: AuthChannel;
  target: string;
  codeHash: string;
  expiresAt: string;
  attempts: number;
  purpose: "register" | "login";
  remember: boolean;
  context?: AuthUsageContext;
  consumed: boolean;
  createdAt: string;
};

export type AuthUsageContext = {
  nodeId?: string;
  ip?: string;
  userAgent?: string;
};

type GoogleState = {
  state: string;
  createdAt: string;
  returnUrl: string | null;
};

type InternalStore = {
  users: Record<string, InternalUser>;
  otpChallenges: Record<string, OtpChallenge>;
  googleStates: Record<string, GoogleState>;
};

const DEFAULT_STORE: InternalStore = {
  users: {},
  otpChallenges: {},
  googleStates: {},
};

const STORE_PATH =
  process.env.INTERNAL_AUTH_STORE_PATH ||
  path.join(process.cwd(), ".runtime", "internal-auth", "store.json");

const INTERNAL_AUTH_KEY =
  process.env.INTERNAL_AUTH_KEY || "dev-internal-auth-key-change-me";

const TOKEN_TTL_SECONDS = Number(process.env.INTERNAL_AUTH_TOKEN_TTL || "86400");
const PERSISTENT_TOKEN_TTL_SECONDS = Number(
  process.env.INTERNAL_AUTH_PERSISTENT_TOKEN_TTL || "315360000",
);
const OTP_TTL_SECONDS = Number(process.env.INTERNAL_AUTH_OTP_TTL || "300");
const OTP_MAX_ATTEMPTS = Number(process.env.INTERNAL_AUTH_OTP_MAX_ATTEMPTS || "5");

let storeWriteLock: Promise<void> = Promise.resolve();

function b64UrlEncode(input: string): string {
  return Buffer.from(input, "utf-8")
    .toString("base64")
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/g, "");
}

function b64UrlDecode(input: string): string {
  const normalized = input.replace(/-/g, "+").replace(/_/g, "/");
  const padLen = (4 - (normalized.length % 4)) % 4;
  const padded = normalized + "=".repeat(padLen);
  return Buffer.from(padded, "base64").toString("utf-8");
}

function nowIso(): string {
  return new Date().toISOString();
}

function plusSeconds(seconds: number): string {
  return new Date(Date.now() + seconds * 1000).toISOString();
}

function hmac(input: string): string {
  return createHmac("sha256", INTERNAL_AUTH_KEY).update(input).digest("hex");
}

function hashPassword(password: string, salt?: string): { salt: string; hash: string } {
  const passwordSalt = salt || randomBytes(16).toString("hex");
  const hash = pbkdf2Sync(password, passwordSalt, 120000, 32, "sha256").toString("hex");
  return { salt: passwordSalt, hash };
}

function verifyPassword(password: string, salt: string, hash: string): boolean {
  const check = pbkdf2Sync(password, salt, 120000, 32, "sha256").toString("hex");
  const a = Buffer.from(check, "hex");
  const b = Buffer.from(hash, "hex");
  if (a.length !== b.length) {
    return false;
  }
  return timingSafeEqual(a, b);
}

function signTokenPayload(payload: Record<string, unknown>): string {
  const encoded = b64UrlEncode(JSON.stringify(payload));
  const signature = b64UrlEncode(hmac(encoded));
  return `kli.${encoded}.${signature}`;
}

function createToken(user: InternalUser, ttlSeconds: number): string {
  const iat = Math.floor(Date.now() / 1000);
  const exp = iat + Math.max(300, ttlSeconds);
  return signTokenPayload({
    sub: user.id,
    email: user.email,
    phone: user.phone,
    name: user.name,
    iat,
    exp,
    provider: "internal",
  });
}

async function sendOtpCode(channel: AuthChannel, target: string, code: string): Promise<void> {
  const smsEnabled = String(process.env.AUTH_SMS_ENABLED || "false").toLowerCase() === "true";
  const emailEnabled = String(process.env.AUTH_EMAIL_OTP_ENABLED || "false").toLowerCase() === "true";

  if (channel === "sms" && !smsEnabled) {
    return;
  }
  if (channel === "email" && !emailEnabled) {
    return;
  }

  const webhook = process.env.AUTH_OTP_WEBHOOK_URL;
  if (!webhook) {
    return;
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 2500);
  try {
    await fetch(webhook, {
      method: "POST",
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...(process.env.AUTH_OTP_WEBHOOK_KEY
          ? { "X-OTP-Webhook-Key": process.env.AUTH_OTP_WEBHOOK_KEY }
          : {}),
      },
      body: JSON.stringify({ channel, target, code }),
    });
  } catch {
    // Delivery failures are intentionally non-fatal in this stage.
  } finally {
    clearTimeout(timeout);
  }
}

function parseTokenUnsafe(token: string): Record<string, unknown> | null {
  const parts = token.split(".");
  if (parts.length !== 3 || parts[0] !== "kli") {
    return null;
  }
  const payloadEncoded = parts[1];
  const signature = parts[2];
  const expected = b64UrlEncode(hmac(payloadEncoded));

  const a = Buffer.from(signature);
  const b = Buffer.from(expected);
  if (a.length !== b.length || !timingSafeEqual(a, b)) {
    return null;
  }

  try {
    return JSON.parse(b64UrlDecode(payloadEncoded)) as Record<string, unknown>;
  } catch {
    return null;
  }
}

async function readStore(): Promise<InternalStore> {
  try {
    const text = await fs.readFile(STORE_PATH, "utf-8");
    const parsed = JSON.parse(text) as InternalStore;
    return {
      users: parsed.users || {},
      otpChallenges: parsed.otpChallenges || {},
      googleStates: parsed.googleStates || {},
    };
  } catch {
    return { ...DEFAULT_STORE };
  }
}

async function writeStore(store: InternalStore): Promise<void> {
  await fs.mkdir(path.dirname(STORE_PATH), { recursive: true });
  await fs.writeFile(STORE_PATH, JSON.stringify(store, null, 2), "utf-8");
}

async function withStoreLock<T>(fn: (store: InternalStore) => Promise<T>): Promise<T> {
  const prev = storeWriteLock;
  let release!: () => void;
  storeWriteLock = new Promise<void>((resolve) => {
    release = resolve;
  });
  await prev;
  try {
    const store = await readStore();
    const result = await fn(store);
    await writeStore(store);
    return result;
  } finally {
    release();
  }
}

function sanitizeIdentifier(input: string): string {
  return input.trim().toLowerCase();
}

function normalizePhone(input: string): string {
  return input.trim().replace(/\s+/g, "");
}

function isProduction(): boolean {
  return process.env.NODE_ENV === "production";
}

function pruneStore(store: InternalStore): void {
  const now = Date.now();
  for (const [id, challenge] of Object.entries(store.otpChallenges)) {
    if (challenge.consumed || new Date(challenge.expiresAt).getTime() < now) {
      delete store.otpChallenges[id];
    }
  }

  for (const [state, item] of Object.entries(store.googleStates)) {
    const ageMs = now - new Date(item.createdAt).getTime();
    if (ageMs > 10 * 60 * 1000) {
      delete store.googleStates[state];
    }
  }
}

function createOtpCode(): string {
  return String(randomInt(0, 1000000)).padStart(6, "0");
}

function hashOtp(challengeId: string, code: string): string {
  return hmac(`${challengeId}:${code}`);
}

function publicUser(user: InternalUser): Record<string, unknown> {
  return {
    id: user.id,
    name: user.name,
    email: user.email,
    phone: user.phone,
    emailVerified: user.emailVerified,
    phoneVerified: user.phoneVerified,
    googleLinked: user.googleLinked,
  };
}

async function createOtpChallenge(
  store: InternalStore,
  user: InternalUser,
  channel: AuthChannel,
  purpose: "register" | "login",
  remember: boolean,
  context?: AuthUsageContext,
): Promise<{ challenge: OtpChallenge; code: string }> {
  const target = channel === "sms" ? user.phone : user.email;
  if (!target) {
    throw new Error(`User has no ${channel} target configured`);
  }

  const challengeId = randomBytes(12).toString("hex");
  const code = createOtpCode();
  const challenge: OtpChallenge = {
    id: challengeId,
    userId: user.id,
    channel,
    target,
    codeHash: hashOtp(challengeId, code),
    expiresAt: plusSeconds(OTP_TTL_SECONDS),
    attempts: 0,
    purpose,
    remember,
    context,
    consumed: false,
    createdAt: nowIso(),
  };

  store.otpChallenges[challengeId] = challenge;

  return { challenge, code };
}

function deliveryMessage(channel: AuthChannel, target: string): string {
  if (channel === "sms") {
    return `OTP sent via SMS to ${target}`;
  }
  return `OTP sent via email to ${target}`;
}

export async function registerInternalUser(input: {
  name?: string;
  email?: string;
  phone?: string;
  password: string;
  channel?: AuthChannel;
  remember?: boolean;
  context?: AuthUsageContext;
}): Promise<Record<string, unknown>> {
  const startedAt = Date.now();
  const name = (input.name || "Kloud User").trim();
  const email = input.email ? sanitizeIdentifier(input.email) : null;
  const phone = input.phone ? normalizePhone(input.phone) : null;
  const password = input.password || "";
  const channel: AuthChannel = input.channel || (phone ? "sms" : "email");
  const remember = Boolean(input.remember);

  if (!email && !phone) {
    throw new Error("Either email or phone is required");
  }
  if (password.length < 8) {
    throw new Error("Password must be at least 8 characters");
  }

  return withStoreLock(async (store) => {
    pruneStore(store);

    const existing = Object.values(store.users).find(
      (u) => (email && u.email === email) || (phone && u.phone === phone)
    );

    if (existing) {
      throw new Error("User already exists");
    }

    const userId = randomBytes(10).toString("hex");
    const hashed = hashPassword(password);

    const user: InternalUser = {
      id: userId,
      name,
      email,
      phone,
      passwordHash: hashed.hash,
      passwordSalt: hashed.salt,
      emailVerified: false,
      phoneVerified: false,
      googleLinked: false,
      createdAt: nowIso(),
      updatedAt: nowIso(),
    };

    store.users[userId] = user;

    const { challenge, code } = await createOtpChallenge(
      store,
      user,
      channel,
      "register",
      remember,
      input.context,
    );
    await sendOtpCode(channel, challenge.target, code);

    await writeAuthStigmaEvent({
      event: "register",
      success: true,
      userId: user.id,
      identifier: email || phone || undefined,
      channel,
      remember,
      latencyMs: Date.now() - startedAt,
      ip: input.context?.ip,
      userAgent: input.context?.userAgent,
      extra: input.context?.nodeId ? { nodeId: input.context.nodeId } : undefined,
    });

    return {
      success: true,
      stage: "otp_required",
      challengeId: challenge.id,
      channel,
      expiresAt: challenge.expiresAt,
      delivery: deliveryMessage(channel, challenge.target),
      user: publicUser(user),
      ...(isProduction() ? {} : { devOtpCode: code }),
    };
  });
}

export async function loginInternalUser(input: {
  identifier: string;
  password: string;
  channel?: AuthChannel;
  remember?: boolean;
  context?: AuthUsageContext;
}): Promise<Record<string, unknown>> {
  const startedAt = Date.now();
  const identifier = input.identifier.trim();
  const password = input.password || "";
  const preferredChannel: AuthChannel | undefined = input.channel;
  const remember = Boolean(input.remember);

  if (!identifier || !password) {
    throw new Error("Identifier and password are required");
  }

  return withStoreLock(async (store) => {
    pruneStore(store);

    const idNorm = sanitizeIdentifier(identifier);
    const phoneNorm = normalizePhone(identifier);

    const user = Object.values(store.users).find(
      (u) => u.email === idNorm || u.phone === phoneNorm
    );

    if (!user) {
      throw new Error("User not found");
    }

    if (!verifyPassword(password, user.passwordSalt, user.passwordHash)) {
      throw new Error("Invalid credentials");
    }

    const channel: AuthChannel =
      preferredChannel || (user.phone ? "sms" : "email");

    const { challenge, code } = await createOtpChallenge(
      store,
      user,
      channel,
      "login",
      remember,
      input.context,
    );
    await sendOtpCode(channel, challenge.target, code);

    await writeAuthStigmaEvent({
      event: "login",
      success: true,
      userId: user.id,
      identifier,
      channel,
      remember,
      latencyMs: Date.now() - startedAt,
      ip: input.context?.ip,
      userAgent: input.context?.userAgent,
      extra: input.context?.nodeId ? { nodeId: input.context.nodeId } : undefined,
    });

    return {
      success: true,
      stage: "otp_required",
      challengeId: challenge.id,
      channel,
      expiresAt: challenge.expiresAt,
      delivery: deliveryMessage(channel, challenge.target),
      user: publicUser(user),
      ...(isProduction() ? {} : { devOtpCode: code }),
    };
  });
}

export async function verifyInternalOtp(input: {
  challengeId: string;
  code: string;
  context?: AuthUsageContext;
}): Promise<Record<string, unknown>> {
  const startedAt = Date.now();
  const challengeId = input.challengeId.trim();
  const code = input.code.trim();

  if (!challengeId || !code) {
    throw new Error("challengeId and code are required");
  }

  return withStoreLock(async (store) => {
    pruneStore(store);

    const challenge = store.otpChallenges[challengeId];
    if (!challenge) {
      throw new Error("OTP challenge not found or expired");
    }
    if (challenge.consumed) {
      throw new Error("OTP challenge already used");
    }
    if (new Date(challenge.expiresAt).getTime() < Date.now()) {
      delete store.otpChallenges[challenge.id];
      throw new Error("OTP challenge expired");
    }

    challenge.attempts += 1;
    if (challenge.attempts > OTP_MAX_ATTEMPTS) {
      delete store.otpChallenges[challenge.id];
      throw new Error("OTP attempts exceeded");
    }

    const expected = hashOtp(challenge.id, code);
    if (challenge.codeHash !== expected) {
      store.otpChallenges[challenge.id] = challenge;
      throw new Error("Invalid OTP code");
    }

    const user = store.users[challenge.userId];
    if (!user) {
      throw new Error("User not found");
    }

    if (challenge.channel === "email") {
      user.emailVerified = true;
    }
    if (challenge.channel === "sms") {
      user.phoneVerified = true;
    }
    user.updatedAt = nowIso();
    store.users[user.id] = user;

    challenge.consumed = true;
    store.otpChallenges[challenge.id] = challenge;

    const ttlSeconds = challenge.remember
      ? Math.max(TOKEN_TTL_SECONDS, PERSISTENT_TOKEN_TTL_SECONDS)
      : TOKEN_TTL_SECONDS;
    const token = createToken(user, ttlSeconds);

    await writeAuthStigmaEvent({
      event: "otp_verified",
      success: true,
      userId: user.id,
      channel: challenge.channel,
      remember: challenge.remember,
      latencyMs: Date.now() - startedAt,
      ip: input.context?.ip || challenge.context?.ip,
      userAgent: input.context?.userAgent || challenge.context?.userAgent,
      extra: {
        ttlSeconds,
        ...(input.context?.nodeId || challenge.context?.nodeId
          ? { nodeId: input.context?.nodeId || challenge.context?.nodeId }
          : {}),
      },
    });

    return {
      success: true,
      stage: "authenticated",
      token,
      tokenType: "Bearer",
      expiresIn: TOKEN_TTL_SECONDS,
      user: publicUser(user),
    };
  });
}

export function verifyInternalToken(token: string): Record<string, unknown> | null {
  const payload = parseTokenUnsafe(token);
  if (!payload) {
    return null;
  }
  const exp = Number(payload.exp || 0);
  if (!exp || exp < Math.floor(Date.now() / 1000)) {
    return null;
  }
  return payload;
}

export async function getInternalUserById(userId: string): Promise<InternalUser | null> {
  const store = await readStore();
  return store.users[userId] || null;
}

export async function resolveBearerUser(authorizationHeader: string | null): Promise<InternalUser | null> {
  if (!authorizationHeader || !authorizationHeader.startsWith("Bearer ")) {
    return null;
  }
  const token = authorizationHeader.slice("Bearer ".length).trim();
  const payload = verifyInternalToken(token);
  if (!payload) {
    return null;
  }
  const sub = String(payload.sub || "");
  if (!sub) {
    return null;
  }
  const user = await getInternalUserById(sub);
  if (user) {
    await writeAuthStigmaEvent({
      event: "token_validated",
      success: true,
      userId: user.id,
      latencyMs: 0,
    });
  }
  return user;
}

export async function startGoogleAuth(returnUrl?: string): Promise<Record<string, unknown>> {
  const clientId = process.env.GOOGLE_CLIENT_ID;
  const redirectUri = process.env.GOOGLE_REDIRECT_URI;

  if (!clientId || !redirectUri) {
    throw new Error("Google OAuth is not configured");
  }

  return withStoreLock(async (store) => {
    pruneStore(store);

    const state = randomBytes(16).toString("hex");
    store.googleStates[state] = {
      state,
      createdAt: nowIso(),
      returnUrl: returnUrl || null,
    };

    const params = new URLSearchParams({
      client_id: clientId,
      redirect_uri: redirectUri,
      response_type: "code",
      scope: "openid email profile",
      state,
      access_type: "offline",
      prompt: "consent",
    });

    return {
      success: true,
      authUrl: `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`,
      state,
    };
  });
}

export async function finishGoogleAuth(code: string, state: string): Promise<Record<string, unknown>> {
  const clientId = process.env.GOOGLE_CLIENT_ID;
  const clientSecret = process.env.GOOGLE_CLIENT_SECRET;
  const redirectUri = process.env.GOOGLE_REDIRECT_URI;

  if (!clientId || !clientSecret || !redirectUri) {
    throw new Error("Google OAuth is not configured");
  }

  return withStoreLock(async (store) => {
    pruneStore(store);

    const stateRecord = store.googleStates[state];
    if (!stateRecord) {
      throw new Error("Invalid or expired OAuth state");
    }
    delete store.googleStates[state];

    const tokenRes = await fetch("https://oauth2.googleapis.com/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        code,
        client_id: clientId,
        client_secret: clientSecret,
        redirect_uri: redirectUri,
        grant_type: "authorization_code",
      }),
    });

    if (!tokenRes.ok) {
      throw new Error("Failed to exchange Google authorization code");
    }

    const tokenJson = (await tokenRes.json()) as { access_token?: string };
    const accessToken = tokenJson.access_token;

    if (!accessToken) {
      throw new Error("Google token response missing access_token");
    }

    const profileRes = await fetch("https://www.googleapis.com/oauth2/v3/userinfo", {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    if (!profileRes.ok) {
      throw new Error("Failed to fetch Google profile");
    }

    const profile = (await profileRes.json()) as {
      email?: string;
      name?: string;
      email_verified?: boolean;
    };

    if (!profile.email) {
      throw new Error("Google profile missing email");
    }

    const email = sanitizeIdentifier(profile.email);
    let user = Object.values(store.users).find((u) => u.email === email);

    if (!user) {
      const generatedPassword = randomBytes(24).toString("hex");
      const hashed = hashPassword(generatedPassword);
      const userId = randomBytes(10).toString("hex");
      user = {
        id: userId,
        name: profile.name || "Google User",
        email,
        phone: null,
        passwordHash: hashed.hash,
        passwordSalt: hashed.salt,
        emailVerified: Boolean(profile.email_verified),
        phoneVerified: false,
        googleLinked: true,
        createdAt: nowIso(),
        updatedAt: nowIso(),
      };
    } else {
      user.googleLinked = true;
      user.emailVerified = user.emailVerified || Boolean(profile.email_verified);
      user.updatedAt = nowIso();
    }

    store.users[user.id] = user;

    const token = createToken(user, TOKEN_TTL_SECONDS);
    return {
      success: true,
      stage: "authenticated",
      token,
      tokenType: "Bearer",
      expiresIn: TOKEN_TTL_SECONDS,
      user: publicUser(user),
      returnUrl: stateRecord.returnUrl,
    };
  });
}
