/**
 * Layer 17: Authentication & Authorization
 * JWT-based authentication with role-based access control
 */

import jwt from "jsonwebtoken";
import bcrypt from "bcryptjs";
import { Request, Response, NextFunction } from "express";

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════════

const JWT_SECRET =
  process.env.JWT_SECRET || "kloud-super-secret-key-change-in-production";
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || "24h";
const SALT_ROUNDS = 12;

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

export interface TokenPayload {
  userId: string;
  email: string;
  role: UserRole;
  iat?: number;
  exp?: number;
}

export type UserRole = "admin" | "user" | "guest" | "api";

export interface AuthenticatedRequest extends Request {
  user?: TokenPayload;
}

// ═══════════════════════════════════════════════════════════════════════════════
// PASSWORD UTILITIES
// ═══════════════════════════════════════════════════════════════════════════════

export const password = {
  hash: async (plainPassword: string): Promise<string> => {
    return bcrypt.hash(plainPassword, SALT_ROUNDS);
  },

  verify: async (
    plainPassword: string,
    hashedPassword: string,
  ): Promise<boolean> => {
    return bcrypt.compare(plainPassword, hashedPassword);
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// JWT UTILITIES
// ═══════════════════════════════════════════════════════════════════════════════

export const token = {
  generate: (payload: Omit<TokenPayload, "iat" | "exp">): string => {
    return jwt.sign(payload, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN });
  },

  verify: (tokenString: string): TokenPayload | null => {
    try {
      return jwt.verify(tokenString, JWT_SECRET) as TokenPayload;
    } catch {
      return null;
    }
  },

  decode: (tokenString: string): TokenPayload | null => {
    try {
      return jwt.decode(tokenString) as TokenPayload;
    } catch {
      return null;
    }
  },
};

// ═══════════════════════════════════════════════════════════════════════════════
// MIDDLEWARE
// ═══════════════════════════════════════════════════════════════════════════════

export const authenticate = (
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction,
) => {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return res.status(401).json({ error: "Authentication required" });
  }

  const tokenString = authHeader.substring(7);
  const payload = token.verify(tokenString);

  if (!payload) {
    return res.status(401).json({ error: "Invalid or expired token" });
  }

  req.user = payload;
  next();
};

export const authorize = (...allowedRoles: UserRole[]) => {
  return (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({ error: "Authentication required" });
    }

    if (!allowedRoles.includes(req.user.role)) {
      return res.status(403).json({ error: "Insufficient permissions" });
    }

    next();
  };
};

// Optional authentication (doesn't fail if no token)
export const optionalAuth = (
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction,
) => {
  const authHeader = req.headers.authorization;

  if (authHeader && authHeader.startsWith("Bearer ")) {
    const tokenString = authHeader.substring(7);
    const payload = token.verify(tokenString);
    if (payload) {
      req.user = payload;
    }
  }

  next();
};

// ═══════════════════════════════════════════════════════════════════════════════
// API KEY AUTHENTICATION
// ═══════════════════════════════════════════════════════════════════════════════

const API_KEYS = new Map<string, { name: string; role: UserRole }>([
  ["kloud-api-key-1", { name: "Default API", role: "api" }],
]);

export const apiKeyAuth = (
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction,
) => {
  const apiKey = req.headers["x-api-key"] as string;

  if (!apiKey) {
    return res.status(401).json({ error: "API key required" });
  }

  const keyData = API_KEYS.get(apiKey);
  if (!keyData) {
    return res.status(401).json({ error: "Invalid API key" });
  }

  req.user = {
    userId: "api",
    email: `${keyData.name}@api.kloud.com`,
    role: keyData.role,
  };

  next();
};

export default {
  password,
  token,
  authenticate,
  authorize,
  optionalAuth,
  apiKeyAuth,
};

