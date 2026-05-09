/**
 * Kloud SIMPLE USER AUTHENTICATION
 * ====================================
 * Basic user auth pÃ«r payment system
 */

import { FastifyInstance, FastifyRequest, FastifyReply } from "fastify";
import * as crypto from "crypto";

// =================================================================================
// USER INTERFACES
// =================================================================================

export interface User {
  id: string;
  email: string;
  username: string;
  hashed_password: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserCreateRequest {
  email: string;
  username: string;
  password: string;
}

export interface UserLoginRequest {
  username_or_email: string;
  password: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// =================================================================================
// IN-MEMORY USER STORAGE
// =================================================================================

const users = new Map<string, User>();
const tokens = new Map<string, { user_id: string; expires_at: string }>();

// Pre-populate with admin user
const adminUser: User = {
  id: "admin-001",
  email: "admin@kloud.com",
  username: "admin",
  hashed_password: hashPassword(process.env['ADMIN_PASSWORD'] || "ChangeMe123!"),
  is_active: true,
  is_superuser: true,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString()
};
users.set(adminUser.id, adminUser);

// =================================================================================
// UTILITY FUNCTIONS
// =================================================================================

import bcryptjs from 'bcryptjs';

const BCRYPT_ROUNDS = 12;

function hashPassword(password: string): string {
  // SECURITY: Use bcrypt with proper work factor for password hashing
  return bcryptjs.hashSync(password, BCRYPT_ROUNDS);
}

function verifyPassword(password: string, hashedPassword: string): boolean {
  // SECURITY: Use bcrypt's constant-time comparison
  return bcryptjs.compareSync(password, hashedPassword);
}

function generateToken(): string {
  return crypto.randomUUID() + '.' + Date.now() + '.' + crypto.randomBytes(16).toString('hex');
}

function createTokenPair(user: User): TokenPair {
  const accessToken = generateToken();
  const refreshToken = generateToken();
  const expiresIn = 3600; // 1 hour

  // Store tokens
  tokens.set(accessToken, {
    user_id: user.id,
    expires_at: new Date(Date.now() + expiresIn * 1000).toISOString()
  });

  tokens.set(refreshToken, {
    user_id: user.id,
    expires_at: new Date(Date.now() + 14 * 24 * 3600 * 1000).toISOString() // 14 days
  });

  return {
    access_token: accessToken,
    refresh_token: refreshToken,
    token_type: "bearer",
    expires_in: expiresIn
  };
}

function findUserByEmail(email: string): User | null {
  for (const user of users.values()) {
    if (user.email === email) {
      return user;
    }
  }
  return null;
}

function findUserByUsername(username: string): User | null {
  for (const user of users.values()) {
    if (user.username === username) {
      return user;
    }
  }
  return null;
}

function verifyToken(token: string): User | null {
  const tokenData = tokens.get(token);
  if (!tokenData) return null;

  // Check expiration
  if (new Date() > new Date(tokenData.expires_at)) {
    tokens.delete(token);
    return null;
  }

  return users.get(tokenData.user_id) || null;
}

// =================================================================================
// AUTH ROUTES
// =================================================================================

export async function registerAuthRoutes(app: FastifyInstance) {

  // =================================================================================
  // REGISTER USER
  // =================================================================================
  app.post("/auth/register", async (request: FastifyRequest, reply: FastifyReply) => {
    const body = request.body as UserCreateRequest;

    try {
      // Check if email or username exists
      if (findUserByEmail(body.email)) {
        reply.code(409);
        return {
          success: false,
          error: "Email already registered"
        };
      }

      if (findUserByUsername(body.username)) {
        reply.code(409);
        return {
          success: false,
          error: "Username already taken"
        };
      }

      // Create new user
      const user: User = {
        id: crypto.randomUUID(),
        email: body.email,
        username: body.username,
        hashed_password: hashPassword(body.password),
        is_active: true,
        is_superuser: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      users.set(user.id, user);

      return {
        success: true,
        user: {
          id: user.id,
          email: user.email,
          username: user.username,
          is_active: user.is_active,
          created_at: user.created_at
        }
      };

    } catch (error: any) {
      reply.code(400);
      return {
        success: false,
        error: error.message || "Registration failed"
      };
    }
  });

  // =================================================================================
  // LOGIN USER
  // =================================================================================
  app.post("/auth/login", async (request: FastifyRequest, reply: FastifyReply) => {
    const body = request.body as UserLoginRequest;

    try {
      // Find user by email or username
      let user = findUserByEmail(body.username_or_email);
      if (!user) {
        user = findUserByUsername(body.username_or_email);
      }

      if (!user || !verifyPassword(body.password, user.hashed_password)) {
        reply.code(401);
        return {
          success: false,
          error: "Invalid credentials"
        };
      }

      if (!user.is_active) {
        reply.code(403);
        return {
          success: false,
          error: "User account is inactive"
        };
      }

      // Create token pair
      const tokenPair = createTokenPair(user);

      return {
        success: true,
        message: "Login successful",
        user: {
          id: user.id,
          email: user.email,
          username: user.username,
          is_superuser: user.is_superuser
        },
        tokens: tokenPair
      };

    } catch (error: any) {
      reply.code(400);
      return {
        success: false,
        error: error.message || "Login failed"
      };
    }
  });

  // =================================================================================
  // GET CURRENT USER
  // =================================================================================
  app.get("/auth/me", async (request: FastifyRequest, reply: FastifyReply) => {
    const authHeader = request.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      reply.code(401);
      return {
        success: false,
        error: "No authorization token provided"
      };
    }

    const token = authHeader.substring(7);
    const user = verifyToken(token);

    if (!user) {
      reply.code(401);
      return {
        success: false,
        error: "Invalid or expired token"
      };
    }

    return {
      success: true,
      user: {
        id: user.id,
        email: user.email,
        username: user.username,
        is_active: user.is_active,
        is_superuser: user.is_superuser,
        created_at: user.created_at
      }
    };
  });

  // =================================================================================
  // LOGOUT
  // =================================================================================
  app.post("/auth/logout", async (request: FastifyRequest, reply: FastifyReply) => {
    const authHeader = request.headers.authorization;
    
    if (authHeader && authHeader.startsWith('Bearer ')) {
      const token = authHeader.substring(7);
      tokens.delete(token);
    }

    return {
      success: true,
      message: "Logout successful"
    };
  });

  // =================================================================================
  // GET ALL USERS (Admin only)
  // =================================================================================
  app.get("/auth/users", async (request: FastifyRequest, reply: FastifyReply) => {
    const authHeader = request.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      reply.code(401);
      return {
        success: false,
        error: "No authorization token provided"
      };
    }

    const token = authHeader.substring(7);
    const currentUser = verifyToken(token);

    if (!currentUser || !currentUser.is_superuser) {
      reply.code(403);
      return {
        success: false,
        error: "Admin access required"
      };
    }

    const allUsers = Array.from(users.values()).map(user => ({
      id: user.id,
      email: user.email,
      username: user.username,
      is_active: user.is_active,
      is_superuser: user.is_superuser,
      created_at: user.created_at
    }));

    return {
      success: true,
      users_count: allUsers.length,
      users: allUsers
    };
  });
}

